from dataclasses import dataclass
import logging
import os
from subprocess import Popen, PIPE
from typing import Dict, Any, List
import uuid

import hvac
import requests
import urllib3

LOGGER = logging.getLogger(__name__)

@dataclass
class VaultAction:
    path: str
    action_type: List[str]
    params: List[Dict[str, Any]]

    @property
    def flattened_params(self) -> str:
        if not self.params:
            return ""

        flattened = [" \\\n"]
 
        for i, kv in enumerate(self.params):
            k = kv["k"]
            v = kv["v"]

            if "\n" in v:
                marker = f"EOF_{i}"
                v =  f"- <<{marker}\n{v}{marker}\n"
                flattened.append(f'  {k}={v}')
            else:
                flattened.append(f'  {k}={v}')
                if i < len(self.params) - 1:
                    flattened.append(" \\\n")

        return "".join(flattened)

    
    def build(self, output_policy: bool=False) -> List[str]:
        cmd_parts = [
            "vault",
            *self.action_type,
            "-output-policy" if output_policy else "",
            self.path,
            self.flattened_params
        ]
        
        return cmd_parts

    def _run_cli(self, output_policy: bool = False) -> str:
        cmd = self.build(output_policy)

        with Popen(cmd, stdout=PIPE) as proc:
            retval = proc.wait()
            output = proc.stdout.read().decode("utf-8")
            output += "\n"

        if retval != 0:
            raise ValueError("failed to generate policy. ret=%s", retval)

        return output

    def _run_hvac(self, client: hvac.Client, attempts: int = 3) -> str:
        def _retry(e: Exception):
            if attempts > 1:
                LOGGER.warning(f"timeout error occurred, retrying... {attempts-1} attempts left.")
                return self._run_hvac(client, attempts-1)
            else:
                LOGGER.error("maximum retry attempts reached. operation failed.")
                raise e

        params = {kv["k"]: kv["v"] for kv in self.params}

        try:
            # perform the action
            match self.action_type:
                case ["write"]:
                    LOGGER.info(f"writing %s", self.path)
                
                    result = client.write(path=self.path, **params)
                    result.raise_for_status()
                    return result

                case _:
                    raise ValueError("Unsupported action_type: %s", self.action_type)

        except urllib3.exceptions.ReadTimeoutError as e:
            _retry(e)
        except requests.exceptions.ReadTimeout as e:
            _retry(e)
    


    def run(
        self,
        client: hvac.Client,
        output_policy: bool = False
    ) -> str:
        if client.is_authenticated():
            result = self._run_hvac(client)
        else:
            result = self._run_cli(output_policy)
            
        return result


def parse_commands(config: Dict[str, Any]) -> List[VaultAction]:

    cmds = []
    for item in config["actions"]:
        action_type = [item['type']] if isinstance(item['type'], str) else item['type']
        cmd = VaultAction(
            item["path"],
            action_type,
            item.get("params", None)
        )

        cmds.append(cmd)

    return cmds

def _make_policy_script(
    client: hvac.Client,
    policy_name: str,
    cmds: List[VaultAction],
    can_cleanup: bool
) -> VaultAction:

    path = f"sys/policy/{policy_name}"

    policy_lines = []
    for action in cmds:
        output = action.run(client, output_policy=True)
        policy_lines.append(output)

    if can_cleanup:
        cleanup = (
            f'path "{path}" {{ capabilities = ["delete"] }}'
            '\n\n'
        )
        policy_lines.append(cleanup)

    policy = "".join(policy_lines)
    
    write_action = VaultAction(
        path,
        ["write"],
        [
            { "k": "policy", "v": policy },
        ]
    )

    return write_action


def _make_wrapped_token_script(
    policy_cmd: VaultAction,
    extra_params: Dict[str, Any]
) -> VaultAction:
        
    action = VaultAction(
        path="",
        action_type=["token", "create"],
        params=[
            { "k": "-policy", "v": f"'{os.path.basename(policy_cmd.path)}'" },
            { "k": "-policy", "v": "'default'" },
            { "k": "-metadata", "v": f"cleanup_path='{policy_cmd.path}'"},
            *[ { "k": f"-{k}", "v": str(v) } for k, v in extra_params.items() ]
        ]
    )

    return action


def _unique_policy_name() -> str:
    short_uuid = uuid.uuid4().hex[:16]
    name = f"autogen:tmp-bootstrap:{short_uuid}"
    return name
    
    
def bootstrap_instructions(
    cmds: List[VaultAction],
    client: hvac.Client,
    config: Dict[str, Any]
):

    LOGGER.info("printing instructions")
    client.token = None
    
    do_cleanup = config['cleanup_after_install']
    extra_params = config.get("params", {})
    
    policy_name = _unique_policy_name()
    policy_action = _make_policy_script(client, policy_name, cmds, do_cleanup)
    wrapped_token_action = _make_wrapped_token_script(policy_action, extra_params)

    border = "-" * 79
    instructions = "\n".join([
        "\n",
        "Script to create minimal-scope wrapped token for bootstrap."
        "\n",
        border,
        " ".join(policy_action.build()),
        " ".join(wrapped_token_action.build()),
        border,
        "\n",
    ])

    LOGGER.warn(instructions)
    
def run_commands(
    cmds: List[VaultAction],
    client: hvac.Client,
    config: Dict[str, Any]
) -> bool:

    do_cleanup = config['cleanup_after_install']

    LOGGER.info("writing to vault...")
    token_info = client.lookup_token()
    
    for action in cmds:
        action.run(client)

    if do_cleanup:
        try:
            data = token_info['data']
            meta = data['meta'] or dict()
            cleanup_path = meta.get('cleanup_path', None)
        
            if cleanup_path:
                LOGGER.info("deleting %s", cleanup_path)
                client.delete(cleanup_path)
        except Exception as e:
            LOGGER.error("failed to cleanup", exc_info=e)
            

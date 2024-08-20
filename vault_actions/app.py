import logging
from typing import Any, Dict

from .commands import parse_commands, run_commands, bootstrap_instructions
from .vault_util import vault_client

LOGGER = logging.getLogger(__name__)


def run(config: Dict[str, Any]) -> bool:

    cmds = parse_commands(config)
    
    client = vault_client(
        config['vault']['url'],
        config['vault'].get('token', None)
    )

    try:
        if not client.is_authenticated():
            raise PermissionError("client not authenticated")

        run_commands(cmds, client, config['bootstrap'])
        LOGGER.info("bootstrap completed.")
        return True

    except Exception as e:
        LOGGER.error("failed writing to vault.\n%s", str(e), exc_info=e)
        bootstrap_instructions(cmds, client, config['bootstrap'])
    
    return False
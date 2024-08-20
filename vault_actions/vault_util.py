from pathlib import Path
import logging
import os

import hvac
from hvac.exceptions import VaultError


LOGGER = logging.getLogger(__name__)

def try_unwrap_and_auth(client: hvac.Client, token: str) -> bool:
    try:
        client.auth_cubbyhole(token)
        return client.is_authenticated()
    except VaultError as e:
        LOGGER.warn("vault error: %s", str(e))
    except Exception as e:
        LOGGER.warn("error: %s", str(e))
    
    return False

def vault_client(url: str, token: str) -> hvac.Client:

    # os.environ.pop('VAULT_TOKEN', None)
    timeout_seconds = int(os.environ.get("VAULT_CLIENT_TIMEOUT", "60"))

    LOGGER.info(f"Connecting to vault: {url}")
    client = hvac.Client(
        url=url,
        timeout=timeout_seconds
    )

    if token is not None and Path(token).is_file():
        token = Path(token).read_text(encoding="utf-8").strip()

    if try_unwrap_and_auth(client, token):
        LOGGER.info("success: retrieved client token.")
    else:
        LOGGER.info("vault auth failed.")

    return client

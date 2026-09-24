"""The signing key is a host secret.

Empty is refused. The test value k is refused. The key is not saved in the record.
"""
from __future__ import annotations

import os

ENV_NAME = "PHOTONSEAL_KEY"


class KeyError_(Exception):
    code = "key_error"


class MissingKey(KeyError_):
    code = "missing_key"


def signing_key_from_env(environ: dict[str, str] | None = None) -> str:
    env = environ if environ is not None else os.environ
    key = env.get(ENV_NAME, "").strip()
    if not key:
        raise MissingKey(f"{ENV_NAME} unset or empty")
    if key == "k":
        raise MissingKey("literal test key k is not a production handle")
    return key

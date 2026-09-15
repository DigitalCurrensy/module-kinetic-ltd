"""Photonseal key — signing material from the environment, not a token.

Empty or missing PHOTONSEAL_KEY is refused. meter.py HMAC law stays frozen.
The key is never written to an outbox. Module Kinetic Ltd.
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
    key = str(env.get(ENV_NAME, "") or "").strip()
    if not key:
        raise MissingKey("PHOTONSEAL_KEY missing")
    return key

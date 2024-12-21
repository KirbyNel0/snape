import json
from pathlib import Path
from typing import Final, Dict, List

from snape.annotations import ShellInfo

__all__ = [
    "SHELLS",
    "FORBIDDEN_ENV_NAMES"
]


_CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.json"


with open(_CONFIG_FILE_PATH) as f:
    _CONFIG_FILE = json.load(f)

if not isinstance(_CONFIG_FILE, dict):
    raise TypeError("Not a valid config file:", _CONFIG_FILE_PATH)

# Shell configurations
if "shells" not in _CONFIG_FILE:
    raise TypeError("Key 'shells' not found in config file")

SHELLS: Final[Dict[str, ShellInfo]] = _CONFIG_FILE["shells"]


# Forbidden env name configuration
if "illegal-env-names" not in _CONFIG_FILE:
    raise TypeError("Key 'illegal-env-names' not found in config file")

FORBIDDEN_ENV_NAMES: Final[List[str]] = _CONFIG_FILE["illegal-env-names"]
"""
Used to prevent the user from unwanted venv creation when wanting to call a subcommand.

If the user tries to create a venv named as any item of this list, an error is thrown (see ``new`` subcommand).
The names of options and subcommands are added automatically.
"""

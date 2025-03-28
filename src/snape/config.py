import json
from pathlib import Path
from typing import Final, Dict, List

from snape.annotations import ShellInfo

__all__ = [
    "SHELLS",
    "FORBIDDEN_ENV_NAMES"
]


# If installed as package, access the package files
if "site-packages" in __file__:
    import sys
    if sys.version_info.minor < 11:
        import pkg_resources
        _CONFIG_DIR_PATH = Path(pkg_resources.resource_filename("snape", "config"))
    else:
        import importlib.resources
        with importlib.resources.path("snape", "config") as __f:
            _CONFIG_DIR_PATH = Path(__f.absolute().resolve())
        del __f
else:
    _CONFIG_DIR_PATH = Path(__file__).parent / "config"


_SHELLS_CONFIG = _CONFIG_DIR_PATH / "shells.json"
_ILLEGAL_ENV_NAME_CONFIG = _CONFIG_DIR_PATH / "illegal-env-names.json"

# Shell configurations
with open(_SHELLS_CONFIG, "r") as __f:
    SHELLS: Final[Dict[str, ShellInfo]] = json.load(__f)
    """
    Contains information on shell setup.
    """

if not isinstance(SHELLS, dict):
    raise TypeError("Not a valid shell config file:", _SHELLS_CONFIG)

# Forbidden env name configuration
with open(_ILLEGAL_ENV_NAME_CONFIG, "r") as __f:
    FORBIDDEN_ENV_NAMES: Final[List[str]] = json.load(__f)
    """
    Used to prevent the user from unwanted venv creation when wanting to call a subcommand.
    
    If the user tries to create a venv named as any item of this list, an error is thrown (see ``new`` subcommand).
    The names of options and subcommands are added automatically.
    """

if not isinstance(FORBIDDEN_ENV_NAMES, list):
    raise TypeError("Not a valid env name config file:", _ILLEGAL_ENV_NAME_CONFIG)

# Remove temporary stuff
del __f, _SHELLS_CONFIG, _ILLEGAL_ENV_NAME_CONFIG

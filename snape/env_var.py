"""
This package offers all environment variables used by snape
as python objects.

Example:

    from snape import env_var
    print(env_var.SHELL)
"""

import os
from pathlib import Path
from typing import Final

from snape.util import absolute_path

__all__ = []

__VARS__: Final[dict[str, str | None]] = {
    # Select the current shell as default.
    # This can be changed via command line option and is applied in ``snape.cli.main``.
    "SHELL": os.getenv("SHELL").split("/")[-1] if os.getenv("SHELL") is not None else None,

    # The currently active python environment.
    "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV"),

    # The directory of all global snape environments.
    "SNAPE_ROOT": os.getenv("SNAPE_ROOT"),

    # The name of local snape environments.
    "SNAPE_VENV": os.getenv("SNAPE_VENV"),
}


# This terrible logic is required to be able to set a variable
# after module initialization
def __getattr__(name):
    if name in __VARS__:
        return __VARS__[name]
    return globals()[name]


def list_vars() -> list[str]:
    return list(__VARS__.keys())


# Apply environment variables

SNAPE_ROOT_PATH: Final[Path | None] = absolute_path(__VARS__["SNAPE_ROOT"]) \
    if __VARS__["SNAPE_ROOT"] is not None else None
"The directory of all global snape environments. If this is not a directory, the script will throw an error."

SNAPE_REPO_PATH: Final[Path] = absolute_path(__file__).parent.parent
"The directory of the snape repository"

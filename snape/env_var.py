import os
from pathlib import Path
from typing import Final

from snape.util import absolute_path


__all__ = [
    "SHELL",
    "VIRTUAL_ENV",
    "SNAPE_ROOT",
    "SNAPE_VENV",
    "SNAPE_LOCAL_VENV",
    "SNAPE_DIR",
    "SNAPE_REPO"
]


# Select the current shell as default.
# This can be changed via command line option and is applied in ``__main__``.
SHELL = os.getenv("SHELL").split("/")[-1]

# The currently active python environment.
VIRTUAL_ENV = os.getenv("VIRTUAL_ENV")

# Load environment variables.
# Their existence is ensured by the shell script.
SNAPE_ROOT = os.getenv("SNAPE_ROOT")
"The directory of all global snape environments."
SNAPE_VENV = os.getenv("SNAPE_VENV")
"The name of the default global snape environment."

SNAPE_LOCAL_VENV = os.getenv("SNAPE_LOCAL_VENV")
"The name of local snape environments."

# Apply environment variables
SNAPE_DIR: Final[Path | None] = absolute_path(SNAPE_ROOT) if SNAPE_ROOT is not None else None
"The directory of all global snape environments. If this is not a directory, the script will throw an error."

# Save repo root
SNAPE_REPO = absolute_path(__file__).parent.parent
""

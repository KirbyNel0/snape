import os
from pathlib import Path
from typing import TypedDict, NewType

__all__ = [
    "ShellInfo",
    "VirtualEnv",
    "SnapeCancel"
]

ShellInfo = TypedDict("ShellInfo", {
    # The path to the default init file for the shell
    "init_file": os.PathLike[str],
    # A file name relative to a virtual environment root pointing to the activation shell script
    "activate_file": str
})
"An object of this type holds information on how to handle different shell environments."

VirtualEnv = NewType("VirtualEnv", Path)
"An object of this type is a ``pathlib.Path`` object pointing to a verified virtual environment"


class SnapeCancel(Warning):
    """If raised, the application should terminate without an error."""
    pass

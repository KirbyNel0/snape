from pathlib import Path
from typing import TypedDict, NewType


__all__ = [
    "ShellInfo",
    "VirtualEnv",
    "SnapeCancel"
]


ShellInfo = TypedDict("ShellInfo", {
    # The path to the default init file for the shell
    "init_file": Path,
    # The command which should be written to "init_file" to activate snape. {} is replaced by the "snape_file" value.
    "source_alias": str,
    # A file name relative to "snape/sh/" pointing to the shell script to execute
    "snape_shell_script": str,
    # A file name relative to a virtual environment root pointing to the activation shell script
    "activate_file": str
})
"An object of this type holds information on how to handle different shell environments."

VirtualEnv = NewType("VirtualEnv", Path)
"An object of this type is a ``pathlib.Path`` object pointing to a verified virtual environment"

class SnapeCancel(Warning):
    """If raised, the application should terminate without an error."""
    pass

from pathlib import Path

from snape.cli._parser import subcommands
from snape.util import log
from snape.virtualenv import create_new_snape_venv, get_snape_venv_path, install_requirements

__all__ = [
    "snape_new"
]


def snape_new(
        env: str | None,
        no_update: bool,
        requirements: str | None,
        requirements_quiet: bool,
        here: bool,
        overwrite: bool
) -> None:
    """
    Create new global or local virtual environments.

    For argument documentation, see ``snape_new_parser``.
    """
    if here and env is not None:
        raise ValueError("snape new --here: Cannot provide an environment name")

    new_venv_path = get_snape_venv_path(env, here)

    log("Directory for new venv:", new_venv_path)

    # Check whether requirements must be installed into the new environment
    if requirements is not None:
        requirements_file = Path(requirements)
        if not requirements_file.is_file():
            raise FileNotFoundError(f"Requirements file not found: {requirements_file}")
    else:
        requirements_file = None

    log("Requirements file:", requirements_file)

    if not overwrite:
        overwrite = None
    # Create environment
    new_venv = create_new_snape_venv(new_venv_path, overwrite, not no_update)

    # Install requirements
    if requirements_file:
        install_requirements(new_venv, requirements_file, no_output=requirements_quiet)


# The subcommand parser for ``snape new``.
snape_new_parser = subcommands.add_parser("new", help="create a new environment", aliases=["touch"])
# The name of the new environment
snape_new_parser.add_argument(
    "env", nargs="?",
    help="the name of the new environment",
    action="store", default=None
)
# Whether to prompt the user for existing venv
snape_new_parser.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments without prompting first",
    action="store_true", default=False, dest="overwrite"
)
# Whether to update pip (see venv package), this usually takes a while
snape_new_parser.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the environment",
    action="store_true", default=False, dest="no_update"
)
# Can be given to specify a requirements.txt file into the new environment
snape_new_parser.add_argument(
    "-r", "--requirements",
    help="install the specified file into the environment",
    action="store", default=None, metavar="FILE", dest="requirements"
)
# If specified with -r, the output of 'pip install -r' will not be printed
snape_new_parser.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing requirements",
    action="store_true", default=False, dest="requirements_quiet"
)
# If specified, a local environment will be created instead of a global one
snape_new_parser.add_argument(
    "-l", "--local", "--here",
    help="create a snape environment in the current directory. "
         "not allowed to provide 'env'.",
    action="store_true", default=False, dest="here"
)
snape_new_parser.set_defaults(func=snape_new)

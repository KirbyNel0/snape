import argparse
import typing
from pathlib import Path
from snape.annotations import VirtualEnv
from snape.cli._parser import subcommands
from snape.util import log, info
from snape.virtualenv import create_new_snape_venv, get_snape_venv_path, install_requirements, is_venv, \
    get_venv_packages, install_packages

__all__ = [
    "snape_new"
]


def snape_new(
        env: str | None,
        do_update: bool,
        requirements: str | None,
        requirements_quiet: bool,
        overwrite: bool
) -> None:
    """
    Create new global or local virtual environments.

    For argument documentation, see ``snape_new_parser``.
    """
    new_venv_path = get_snape_venv_path(env, env is None)

    log("Directory for new venv:", new_venv_path)

    # Check whether requirements must be installed into the new environment
    requirements_source: Path | list[str] | None
    if requirements is not None:
        requirements_path = Path(requirements)
        
        if requirements_path.is_file():
            requirements_source: Path = requirements_path
            log("Requirements file:", requirements_source)
        elif is_venv(requirements_path):
            # Must be a venv from here on
            requirements_venv = typing.cast(VirtualEnv, requirements_path)
            requirements_source: list[str] = get_venv_packages(requirements_venv)

            if len(requirements_source) == 0:
                info(f"Note: No additional packages were installed in {requirements_path}")
        else:
            raise FileNotFoundError(f"Requirements file/venv not found: {requirements_path}")
    else:
        requirements_source = None

    if not overwrite:
        overwrite = None
    # Create environment
    new_venv = create_new_snape_venv(new_venv_path, overwrite, do_update)

    # Install requirements
    if isinstance(requirements_source, Path):
        install_requirements(new_venv, requirements_source, no_output=requirements_quiet)
    elif isinstance(requirements_source, list):
        install_packages(new_venv, requirements_source, no_output=requirements_quiet)


snape_new_parser = subcommands.add_parser(
    "new",
    description=
    """\
  Create new snape-managed environments.

  To create a new local environment, use snape new.
  To create a new global environment named MY_VENV, use snape new MY_VENV.

  An existing environment can be overwritten with this command.
  This can only be done if it is a valid environment, meaning not a simple directory or file.

example:
  To create a global environment and name it MY_VENV, call
    snape new MY_VENV\
    """,
    help="create a new environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_new_parser.add_argument(
    "env", nargs="?",
    help="the name of the new global environment. if not provided, a local environment is created.",
    action="store", default=None
)
snape_new_parser.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments without prompting first",
    action="store_true", default=False, dest="overwrite"
)
snape_new_parser.set_defaults(func=snape_new)

snape_new_parser_packages = snape_new_parser.add_argument_group("pip and packages")
snape_new_parser_packages.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the environment",
    action="store_false", default=True, dest="do_update"
)
snape_new_parser_packages.add_argument(
    "-r", "--requirements",
    help="can be used to specify a file or venv to read packages from which should be installed into the new venv",
    action="store", default=None, metavar="SOURCE", dest="requirements"
)
snape_new_parser_packages.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing packages",
    action="store_true", default=False, dest="requirements_quiet"
)

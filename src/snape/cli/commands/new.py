import argparse
import typing
from pathlib import Path
import snape.env_var
from snape.annotations import VirtualEnv
from snape.cli._parser import subcommands
from snape.util import log, info
from snape.virtualenv import create_new_snape_env, get_snape_env_path, install_requirements, is_virtual_env, \
    get_env_packages, install_packages

__all__ = [
    "snape_new"
]


def snape_new(
        env: str | None,
        do_update: bool,
        requirements: str | None,
        requirements_quiet: bool,
        overwrite: bool | None,
        prompt: str | None,
        packages: list[str] | None,
        install_snape: bool
) -> None:
    """
    Create new global or local virtual environments.

    For argument documentation, see ``snape_new_parser``.
    """
    new_env_path = get_snape_env_path(env, env is None)

    log("Directory for new venv:", new_env_path)

    requirements_path = None if requirements is None else Path(requirements)

    is_requirements_file = requirements is not None and requirements_path.is_file()
    is_requirements_env = requirements is not None and is_virtual_env(requirements_path)

    if requirements and not is_requirements_env and not is_requirements_file:
        raise FileNotFoundError(f"Requirements file/venv not found: {requirements_path}")

    if not overwrite:
        overwrite = None
    # Create environment
    new_env = create_new_snape_env(new_env_path, overwrite, do_update, prompt)

    if new_env is None:
        return

    # Check whether requirements must be installed into the new environment
    if requirements is not None:
        if is_requirements_file:
            log("Requirements file:", requirements_path)
            install_requirements(new_env, requirements_path, no_output=requirements_quiet)
        elif is_requirements_env:
            # Must be a venv from here on
            requirements_env = typing.cast(VirtualEnv, requirements_path)
            packages = get_env_packages(requirements_env)
            if len(packages) == 0:
                info(f"Note: No additional packages were installed in {requirements_path}")

            install_packages(new_env, packages, no_output=requirements_quiet)

    if packages:
        log("Installing additional packages:", ", ".join(packages))
        install_packages(new_env, packages, no_output=requirements_quiet)

    if install_snape:
        log(f"Installing the snape package from {snape.env_var.SNAPE_REPO_PATH}")
        install_packages(new_env, [str(snape.env_var.SNAPE_REPO_PATH)], no_output=requirements_quiet)


snape_new_parser = subcommands.add_parser(
    "new",
    description=
    """\
  Create new snape-managed environments.

  To create a new local environment, use snape new.
  To create a new global environment named ENV, use snape new ENV.

  An existing environment can be overwritten with this command.
  This can only be done if it is a valid environment, meaning not a simple directory or file.\
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
snape_new_parser.add_argument(
    "-p", "--prompt",
    help="specify a prompt string to display when the environment is active",
    action="store", default=None, dest="prompt"
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
snape_new_parser_packages.add_argument(
    "-i", "--install",
    help="install the specified package into the new environment. may be provided multiple times.",
    action="append", default=None, dest="packages"
)
snape_new_parser_packages.add_argument(
    "-I", "--install-snape",
    help="install snape as a python package into the new environment",
    action="store_true", default=False, dest="install_snape"
)

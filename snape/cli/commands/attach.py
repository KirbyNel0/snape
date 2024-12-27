from pathlib import Path

from snape import env_var
from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands
from snape.config import FORBIDDEN_ENV_NAMES
from snape.util import log, info, ask
from snape.virtualenv import ensure_venv, get_snape_venv_path, get_venv_packages, create_new_snape_venv, \
    install_packages, delete_snape_venv

__all__ = [
    "snape_attach"
]


def snape_attach(
        env: str,
        here: bool,
        global_name: str | None,
        ignore_active: bool,
        no_ask: bool,
        no_update: bool,
        overwrite: bool,
        delete_old: bool,
        requirements_quiet: bool
) -> None:
    """
    Make an arbitrary virtual environment available to snape by copying its dependencies into a new environment
    which is then managed by snape.

    For argument documentation, see ``snape_attach_parser``.
    """
    old_venv = ensure_venv(Path(env))
    log("Old venv found:", old_venv)

    # Check whether the environment is located at snape root (is global environment)
    if old_venv.parent == env_var.SNAPE_ROOT_PATH:
        log("Old environment is already known to snape")
        info("Nothing to do")
        return

    # Validate the name for a new global environment. If not specified, the old name will be re-used.
    log("Checking argument conflicts")
    if global_name is None:
        global_name = old_venv.name
    else:
        if here:
            raise ValueError(
                "Local environment requested, global environment name specified. What shall I do now, Potter?"
            )
        if global_name in FORBIDDEN_ENV_NAMES:
            raise ValueError(f"Illegal environment name: {global_name}")

    packages = get_venv_packages(old_venv)
    if len(packages) == 0:
        info(f"Note: No additional packages were installed in '{env}'")

    new_venv_path = get_snape_venv_path(global_name, here)

    # Check whether the new environment is the same as the old one
    # This can happen for local environments already having the correct name
    log("New venv path:", new_venv_path)
    log("Old:", old_venv)
    if new_venv_path == Path(old_venv):
        log("New environment points to old name")
        info("Nothing to do")
        return

    # Create output and prompt
    locality = "local" if here else "global"
    question = f"Do you want to create a new {locality} environment named '{new_venv_path.name}' with the requirements of '{env}'?"
    if not no_ask and not ask(question, default=True):
        raise SnapeCancel()

    if not overwrite:
        overwrite = None
    new_venv = create_new_snape_venv(new_venv_path, overwrite, not no_update)

    if not install_packages(new_venv, packages, requirements_quiet):
        raise RuntimeError("Could not install all packages")

    if delete_old:
        delete_snape_venv(old_venv, no_ask, ignore_active)


# The subcommand parser for ``snape attach``.
snape_attach_parser = subcommands.add_parser(
    "attach", aliases=["possess"],
    description="Make a local environment available to snape.\n"
                "Snape will create a new environment it can manage and install all packages from the old venv into it.",
    help="copy any local environment to a snape-managed environment"
)
# The name of the environment to manage
snape_attach_parser.add_argument(
    "env",
    help="the name or path to the environment to make available to snape",
    action="store"
)
# Whether to make the new environment a global one
snape_attach_parser.add_argument(
    "-l", "--local", "--here",
    help="make the new environment local, not global",
    action="store_true", default=False, dest="here"
)
# A new name for the new global environment
snape_attach_parser.add_argument(
    "-g", "--global-name",
    help="give the new environment an other name. without this, it will have the same name as the old environment.",
    action="store", default=None, dest="global_name", metavar="NAME"
)
# Continue if environment is currently active
snape_attach_parser.add_argument(
    "-i", "--ignore-active",
    help="do not exit if the specified environment is currently active",
    action="store_true", default=False, dest="ignore_active"
)
# Whether to prompt the user for existing venv
snape_attach_parser.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments having the same name as the environment's new name",
    action="store_true", default=False, dest="overwrite"
)
snape_attach_parser.add_argument(
    "-a", "--no-ask",
    help="do not prompt before creating the new environment",
    action="store_true", default=False, dest="no_ask"
)
snape_attach_parser.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing requirements",
    action="store_true", default=False, dest="requirements_quiet"
)
# Whether to update pip (see venv package), this usually takes a while
snape_attach_parser.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the new environment",
    action="store_true", default=False, dest="no_update"
)
snape_attach_parser.add_argument(
    "-d", "--delete-old",
    help="delete the old environment after it has been copied successfully",
    action="store_true", default=False, dest="delete_old"
)
snape_attach_parser.set_defaults(func=snape_attach)

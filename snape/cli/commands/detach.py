from snape.cli._parser import subcommands

from snape.util import absolute_path, log, info
from snape.virtualenv import get_snape_venv_path, ensure_venv, get_venv_packages, create_new_snape_venv, \
    install_packages, delete_snape_venv

__all__ = [
    "snape_detach"
]


def snape_detach(
        path: str,
        here: bool,
        global_name: str | None,
        overwrite: bool,
        no_update: bool,
        delete_old: bool,
        requirements_quiet: bool,
        no_ask: bool,
        ignore_active: bool
):
    old_venv_path = get_snape_venv_path(global_name, here)
    old_venv = ensure_venv(old_venv_path)
    log("Old environment path:", old_venv)

    new_venv_path = absolute_path(path)
    log("New environment path:", new_venv_path)

    # Check whether the new environment is the same as the old one
    # This can happen for local environments already having the correct name
    if new_venv_path == old_venv_path:
        log("New environment points to old name")
        info("Nothing to do")
        return

    packages = get_venv_packages(old_venv)
    if len(packages) == 0:
        info(f"Note: No additional packages were installed in '{old_venv.name}'")

    new_venv = create_new_snape_venv(new_venv_path, overwrite, not no_update)

    if not install_packages(new_venv, packages, requirements_quiet):
        raise RuntimeError("Could not install all packages")

    if delete_old:
        delete_snape_venv(old_venv, no_ask, ignore_active)


snape_detach_parser = subcommands.add_parser(
    "detach",
    description="Create a new local environment not managed by snape.\n"
                "Snape will create a new environment with a given name and install all packages from a given snape-managed venv into it.",
    help="copy any snape-managed environment to a new environment"
)
snape_detach_parser.add_argument(
    "path",
    help="the path to the new environment",
    action="store", metavar="new-env-path"
)
snape_detach_parser.add_argument(
    "-l", "--local", "--here",
    help="detach a local environment. it is not allowed to provide -g.",
    action="store_true", default=False, dest="here"
)
snape_detach_parser.add_argument(
    "-g", "--global-name",
    help="the name of the global environment to detach",
    action="store", default=None, dest="global_name", metavar="ENV"
)
snape_detach_parser.set_defaults(func=snape_detach)

snape_detach_parser_new_env = snape_detach_parser.add_argument_group("setup new environment")
snape_detach_parser_new_env.add_argument(
    "-o", "--overwrite",
    help="overwrite an existing virtual environment at the specified location",
    action="store_true", default=None, dest="overwrite"
)
snape_detach_parser_new_env.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the new environment",
    action="store_true", default=False, dest="no_update"
)
snape_detach_parser_new_env.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing packages",
    action="store_true", default=False, dest="requirements_quiet"
)

snape_detach_parser_old_env = snape_detach_parser.add_argument_group("old environment")
# Continue if environment is currently active
snape_detach_parser_old_env.add_argument(
    "-d", "--delete-old",
    help="delete the old environment after it has been copied successfully",
    action="store_true", default=False, dest="delete_old"
)
snape_detach_parser_old_env.add_argument(
    "-i", "--ignore-active",
    help="do not exit if the specified environment is currently active (with -d)",
    action="store_true", default=False, dest="ignore_active"
)
snape_detach_parser_old_env.add_argument(
    "-a", "--no-ask",
    help="do not prompt before deleting the old environment (with -d)",
    action="store_true", default=False, dest="no_ask"
)

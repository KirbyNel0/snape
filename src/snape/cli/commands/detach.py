import argparse
from pathlib import Path

from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands

from snape.util import absolute_path, log, info, ask
from snape.virtualenv import get_snape_env_path, ensure_virtual_env, get_env_packages, create_new_snape_env, \
    install_packages, delete_snape_env, get_snape_env_name

__all__ = [
    "snape_detach"
]


def snape_detach(
        path: str,
        here: bool,
        global_name: str | None,
        overwrite: bool,
        do_update: bool,
        delete_old: bool,
        requirements_quiet: bool,
        do_ask: bool,
        ignore_active: bool
) -> Path | None:
    """
    Create a virtual environment with the same packages as a selected snape environment.

    For argument documentation, see ``snape_new_parser``.
    """
    snape_env_path = get_snape_env_path(global_name, here)
    snape_env = ensure_virtual_env(snape_env_path)
    log("Old environment path:", snape_env)

    user_env_path = absolute_path(path)
    log("New environment path:", user_env_path)

    # Check whether the new environment is the same as the old one
    # This can happen for local environments already having the correct name
    if user_env_path == snape_env_path:
        log("New environment points to old name")
        info("Nothing to do")
        return None

    packages = get_env_packages(snape_env)
    if len(packages) == 0:
        info(f"Note: No additional packages were installed in '{get_snape_env_name(snape_env)}'")

    locality = "local" if here else "global"
    question = f"Do you want to create a new environment named '{user_env_path.name}' with the requirements of the {locality} snape environment '{get_snape_env_name(snape_env_path)}'?"
    if do_ask and not ask(question, default=True):
        raise SnapeCancel()

    user_env = create_new_snape_env(user_env_path, overwrite, do_update, env_name=user_env_path.name)

    if not install_packages(user_env, packages, requirements_quiet):
        raise RuntimeError("Could not install all packages")

    if delete_old:
        delete_snape_env(snape_env, do_ask, ignore_active)

    return user_env


snape_detach_parser = subcommands.add_parser(
    "detach",
    description=
    """\
  Create a new local environment not managed by snape.

  Snape will create a new environment with a given name and install all packages from a given snape-managed venv into it.
  It has the same behavior for creation and deletion of environments as the new and delete subcommands.

example:
  To copy the snape-managed environment MY_SNAPE to a new environment called ENV, run the following command:
    snape detach MY_SNAPE --as ENV\
    """,
    help="copy any snape-managed environment to a new environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_detach_parser.add_argument(
    "global_name", nargs="?",
    help="the name of the global environment to detach",
    action="store", default=None, metavar="env"
)
snape_detach_parser.add_argument(
    "--as",
    help="the path to the new environment",
    action="store", dest="path", metavar="PATH", required=True
)
snape_detach_parser.add_argument(
    "-l", "--local", "--here",
    help="detach a local environment. it is not allowed to provide 'env'.",
    action="store_true", default=False, dest="here"
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
    action="store_false", default=False, dest="do_update"
)
snape_detach_parser_new_env.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing packages",
    action="store_true", default=False, dest="requirements_quiet"
)

snape_detach_parser_old_env = snape_detach_parser.add_argument_group("old environment")
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
    action="store_false", default=True, dest="do_ask"
)

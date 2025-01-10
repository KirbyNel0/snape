import argparse
from pathlib import Path

from snape import env_var
from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands
from snape.util import log, info, ask
from snape.virtualenv import ensure_venv, get_snape_venv_path, get_venv_packages, create_new_snape_venv, \
    install_packages, delete_snape_venv, get_snape_venv_name

__all__ = [
    "snape_attach"
]


def snape_attach(
        *,
        env: str,
        here: bool,
        global_name: str | None,
        ignore_active: bool,
        do_ask: bool,
        do_update: bool,
        overwrite: bool,
        delete_old: bool,
        requirements_quiet: bool
) -> Path | None:
    """
    Make an arbitrary virtual environment available to snape by copying its dependencies into a new environment
    which is then managed by snape.

    For argument documentation, see ``snape_attach_parser``.

    :return: The path of the new environment.
    """
    user_venv = ensure_venv(Path(env))
    log("Old environment path:", user_venv)

    # Check whether the environment is located at snape root (is global environment)
    if user_venv.parent == env_var.SNAPE_ROOT_PATH:
        log("Old environment is already known to snape")
        info("Nothing to do")
        return None

    snape_venv_path = get_snape_venv_path(global_name, here)
    log("New environment path:", snape_venv_path)

    # Check whether the new environment is the same as the old one
    # This can happen for local environments already having the correct name
    if snape_venv_path == Path(user_venv):
        log("New environment points to old name")
        info("Nothing to do")
        return None

    packages = get_venv_packages(user_venv)
    if len(packages) == 0:
        info(f"Note: No additional packages were installed in '{env}'")

    # Create output and prompt
    locality = "local" if here else "global"
    question = f"Do you want to create a new {locality} environment named '{get_snape_venv_name(snape_venv_path)}' with the requirements of '{env}'?"
    if do_ask and not ask(question, default=True):
        raise SnapeCancel()

    if not overwrite:
        overwrite = None
    snape_venv = create_new_snape_venv(snape_venv_path, overwrite, do_update)

    if not install_packages(snape_venv, packages, requirements_quiet):
        raise RuntimeError("Could not install all packages")

    if delete_old:
        delete_snape_venv(user_venv, do_ask, ignore_active)

    return snape_venv


snape_attach_parser = subcommands.add_parser(
    "attach", aliases=["possess"],
    description=
    """\
  Make a local environment available to snape.

  Snape will create a new environment it can manage and install all packages from the old venv into it.
  It has the same behavior for creation and deletion of environments as the new and delete subcommands.
    
example:
  To make the environment MY_VENV available to snape globally and name it MY_SNAPE, run the following command:
    snape attach MY_VENV --as MY_SNAPE\
    """,
    help="copy any local environment to a snape-managed environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_attach_parser.add_argument(
    "env",
    help="the name or path to the environment to make available to snape",
    action="store", metavar="env-path"
)
snape_attach_parser.set_defaults(func=snape_attach)

snape_attach_parser_new_env = snape_attach_parser.add_argument_group("setup new environment")
snape_attach_parser_new_env.add_argument(
    "-l", "--local", "--here",
    help="make the new environment local, not global",
    action="store_true", default=False, dest="here"
)
snape_attach_parser_new_env.add_argument(
    "--as",
    help="give the new environment an other name. without this, it will have the same name as the old environment.",
    action="store", default=None, dest="global_name", metavar="NAME"
)
snape_attach_parser_new_env.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments having the same name as the environment's new name",
    action="store_true", default=False, dest="overwrite"
)

snape_attach_parser_packages = snape_attach_parser.add_argument_group("pip and packages")
snape_attach_parser_packages.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing packages",
    action="store_true", default=False, dest="requirements_quiet"
)
snape_attach_parser_packages.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the new environment",
    action="store_false", default=True, dest="do_update"
)

snape_attach_parser_old_env = snape_attach_parser.add_argument_group("old environment")
snape_attach_parser_old_env.add_argument(
    "-d", "--delete-old",
    help="delete the old environment after it has been copied successfully",
    action="store_true", default=False, dest="delete_old"
)
snape_attach_parser_old_env.add_argument(
    "-a", "--no-ask",
    help="do not prompt before deleting the old environment (with -d)",
    action="store_false", default=True, dest="do_ask"
)
snape_attach_parser_old_env.add_argument(
    "-i", "--ignore-active",
    help="do not exit if the specified environment is currently active (with -d)",
    action="store_true", default=False, dest="ignore_active"
)

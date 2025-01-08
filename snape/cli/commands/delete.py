import argparse
from pathlib import Path

from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands
from snape.util import log, info
from snape.virtualenv import ensure_venv, delete_snape_venv
from snape.virtualenv.internal import get_snape_venv_path

__all__ = [
    "snape_delete"
]


def snape_delete(
        envs: list[str],
        ignore_not_exists: bool,
        here: bool,
        do_ask: bool,
        ignore_active: bool
) -> list[Path]:
    """
    Delete a existing global or local snape environments.

    For argument documentation, see ``snape_delete_parser``.

    :return: A list of all deleted environment paths.
    """
    if len(envs) == 0 and not here:
        raise ValueError("No snape environments specified")

    old_venv_paths = [*map(lambda x: get_snape_venv_path(x, False), envs)]

    if here:
        old_venv_paths.append(get_snape_venv_path(name=None, local=True))

    deleted_venvs = []
    for old_venv_path in old_venv_paths:
        log("Directory of old venv:", old_venv_path)

        try:
            old_venv = ensure_venv(old_venv_path)
        except Exception as e:
            if ignore_not_exists:
                info("Virtual environment directory not found:", old_venv_path)
                continue
            else:
                raise e
        try:
            delete_snape_venv(old_venv, do_ask, ignore_active)
        except SnapeCancel:
            continue
        deleted_venvs.append(old_venv)

    return deleted_venvs


# The subcommand parser for ``snape delete``.
snape_delete_parser = subcommands.add_parser(
    "delete", aliases=["rm"],
    description=
    """\
  Delete a snape-managed environment.

  To delete a global environment, its name must be provided.
  To delete a local environment, specify --local as name.

  To list all existing environments, use snape status.
  To delete invalid environments, use snape clean.

example:
  To delete a global environment named MY_VENV, call
    snape delete MY_VENV\
    """,
    help="delete an existing environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
# The name of the environment to delete
snape_delete_parser.add_argument(
    "envs", nargs="*",
    help="the names of the environments to delete",
    action="store", default=[]
)
# If specified, a local environment will be deleted instead of a global one
snape_delete_parser.add_argument(
    "-l", "--local", "--here",
    help="remove the snape environment from the current directory",
    action="store_true", default=False, dest="here"
)
snape_delete_parser.set_defaults(func=snape_delete)

snape_delete_parser_prompting = snape_delete_parser.add_argument_group("prompting")
# Do not prompt before deletion
snape_delete_parser_prompting.add_argument(
    "-f", "--no-ask",
    help="do not ask before deleting the environment",
    action="store_false", default=True, dest="do_ask"
)
# Whether to ignore non-existing directories
snape_delete_parser_prompting.add_argument(
    "-e", "--ignore-not-exists",
    help="do not throw an error if the environment does not exist",
    action="store_true", default=False, dest="ignore_not_exists"
)
# Continue if environment is currently active
snape_delete_parser_prompting.add_argument(
    "-r", "--ignore-active",
    help="do not exit if the specified environment is currently active",
    action="store_true", default=False, dest="ignore_active"
)

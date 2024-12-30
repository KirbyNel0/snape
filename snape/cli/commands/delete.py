import argparse

from snape.cli._parser import subcommands
from snape.util import log
from snape.virtualenv import ensure_venv, delete_snape_venv
from snape.virtualenv.internal import get_snape_venv_path

__all__ = [
    "snape_delete"
]


def snape_delete(
        env: str | None,
        ignore_not_exists: bool,
        here: bool,
        do_ask: bool,
        ignore_active: bool
) -> None:
    """
    Delete a existing global or local snape environments.

    For argument documentation, see ``snape_delete_parser``.
    """
    if here and env is not None:
        raise ValueError("snape delete --here: Cannot provide an environment name")

    old_venv_path = get_snape_venv_path(env, here)

    log("Directory of old venv:", old_venv_path)

    try:
        old_venv = ensure_venv(old_venv_path)
    except Exception as e:
        if ignore_not_exists:
            return
        else:
            raise e

    delete_snape_venv(old_venv, do_ask, ignore_active)


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
    "env", nargs="?",
    help="the name of the environment to delete",
    action="store", default=None
)
# If specified, a local environment will be deleted instead of a global one
snape_delete_parser.add_argument(
    "-l", "--local", "--here",
    help="remove the snape environment from the current directory. not allowed to provide 'env'.",
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

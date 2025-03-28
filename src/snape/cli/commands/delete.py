import argparse
from pathlib import Path

from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands
from snape.util import log, info
from snape.virtualenv import ensure_virtual_env, delete_snape_env
from snape.virtualenv.internal import get_snape_env_path

__all__ = [
    "snape_delete"
]


def snape_delete(
        envs: list[str],
        error_not_exists: bool,
        do_ask: bool,
        ignore_active: bool
) -> list[Path]:
    """
    Delete a existing global or local snape environments.

    For argument documentation, see ``snape_delete_parser``.

    :return: A list of all deleted environment paths.
    """
    if len(envs) == 0:
        envs = ["--local"]

    old_env_paths = []
    for env in envs:
        if env == "--local":
            old_env_paths.append(get_snape_env_path(None, True))
        else:
            old_env_paths.append(get_snape_env_path(env, False))

    deleted_envs = []
    for old_env_path in old_env_paths:
        log("Directory of old venv:", old_env_path)

        try:
            old_env = ensure_virtual_env(old_env_path)
        except Exception as e:
            if error_not_exists:
                raise e
            else:
                info("Virtual environment directory not found:", old_env_path)
                continue
        try:
            delete_snape_env(old_env, do_ask, ignore_active)
        except SnapeCancel:
            continue
        deleted_envs.append(old_env)

    return deleted_envs


snape_delete_parser = subcommands.add_parser(
    "delete", aliases=["rm"],
    description=
    """\
  Delete a snape-managed environment.

  To delete a global environment, its name must be provided.
  To delete a local environment, specify --local as name.
  If no name got specified, --local will be assumed.

  To list all existing environments, use snape status.
  To delete invalid environments, use snape clean.

example:
  To delete a global environment named ENV, call
    snape delete ENV\
    """,
    help="delete an existing environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
# The name of the environment to delete
snape_delete_parser.add_argument(
    "envs", nargs="*",
    help="the names of the environments to delete",
    action="extend"
)
# If specified, a local environment will be deleted instead of a global one
snape_delete_parser.add_argument(
    "-l", "--local", "--here",
    help="remove the snape environment from the current directory",
    action="append_const", const="--local", dest="envs"
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
    "-e", "--error-not-exists",
    help="throw an error if the environment does not exist",
    action="store_true", default=False, dest="error_not_exists"
)
# Continue if environment is currently active
snape_delete_parser_prompting.add_argument(
    "-r", "--ignore-active",
    help="do not exit if the specified environment is currently active",
    action="store_true", default=False, dest="ignore_active"
)

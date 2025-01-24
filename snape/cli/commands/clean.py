import argparse
import os
import shutil
from pathlib import Path

from snape.annotations import SnapeCancel
from snape import env_var
from snape.cli._parser import subcommands
from snape.util import ask, log, info
from snape.virtualenv import get_global_snape_envs, get_snape_env_path, is_virtual_env

__all__ = [
    "snape_clean"
]


def snape_clean(
        do_ask: bool
) -> list[Path]:
    """
    Remove unknown files from the global snape directory or delete broken local environments.

    For argument documentation, see ``snape_clean_parser``.

    :return: A list of all removed files.
    """

    # Local files
    unknown_local_files = []
    log("Collecting unknown files at", Path.cwd())
    broken_local_env = get_snape_env_path(None, True)
    if broken_local_env.exists() and not is_virtual_env(broken_local_env):
        unknown_local_files.append(broken_local_env)
    log("Unknown local files:", [*map(str, unknown_local_files)])

    # Global files
    unknown_global_files = []
    log("Collecting unknown files at", env_var.SNAPE_ROOT)
    global_env_files = list(map(lambda env: env_var.SNAPE_ROOT_PATH / env, os.listdir(env_var.SNAPE_ROOT_PATH)))
    global_envs = get_global_snape_envs()
    no_envs = list(set(global_env_files) - set(global_envs))
    log("No venvs:", [*map(str, no_envs)])
    for other_file in no_envs:
        if any(other_file in global_env.parents for global_env in global_envs):
            log("Directory contains nested venvs:", other_file)
            continue
        unknown_global_files.append(other_file)
    log("Unknown global files:", [*map(str, unknown_global_files)])

    if len(unknown_global_files) + len(unknown_local_files) == 0:
        info("Nothing to do")
        return []

    def output_files(files, name):
        info(f"Unclassified {name}:")
        for unknown_file in files:
            info("  >", unknown_file.name, "[dir]" if unknown_file.is_dir() else "[file]")

    output_files(unknown_global_files, "global files")
    output_files(unknown_local_files, "local files")

    unknown_files = [*unknown_global_files, *unknown_local_files]
    removed_files = []
    if (not do_ask) or ask("Do you want to delete all files that are no valid environments?", default=True):
        for other_file in unknown_files:
            if other_file.is_file():
                log("Removing file", other_file)
                os.remove(other_file)
                removed_files.append(other_file)
            elif other_file.is_dir():
                log("Removing directory", other_file)
                shutil.rmtree(other_file)
                removed_files.append(other_file)
    else:
        raise SnapeCancel()

    info("Snape cleanup done")
    return removed_files


snape_clean_parser = subcommands.add_parser(
    "clean",
    description=
    """\
  Delete files in the snape root directory which are no valid snape environments.
  Using the --local flag, a local environment can be checked for its validity.

  An environment is considered valid if it contains a python executable and an activation script.
  An environment is also invalid if it points to a single file instead of a directory.\
    """,
    help="delete unclassified global environments",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_clean_parser.add_argument(
    "-n", "--no-ask",
    help="do not ask before deleting unclassified files",
    action="store_false", default=True, dest="do_ask"
)
snape_clean_parser.set_defaults(func=snape_clean)

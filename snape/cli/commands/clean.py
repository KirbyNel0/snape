import os
import shutil
from pathlib import Path

from snape import env_var
from snape.cli._parser import subcommands
from snape.util import ask, log, info
from snape.virtualenv import get_global_snape_venvs, get_snape_venv_path, is_venv

__all__ = [
    "snape_clean"
]


def snape_clean(
        no_ask: bool,
        here: bool
):
    if here:
        log("Collecting unknown files at", Path.cwd())
        local_venv = get_snape_venv_path(None, True)
        if is_venv(local_venv):
            info("Nothing to do")
        else:
            if no_ask or ask("Remove broken local environment?", default=True):
                log("Removing directory", local_venv)
                shutil.rmtree(local_venv)
        return

    log("Collecting unknown files at", env_var.SNAPE_ROOT)
    global_venv_files = list(map(lambda env: env_var.SNAPE_ROOT_PATH / env, os.listdir(env_var.SNAPE_ROOT_PATH)))
    global_venvs = get_global_snape_venvs()
    other_files = list(set(global_venv_files) - set(global_venvs))
    log("Unknown files:", ", ".join(map(str, other_files)))

    if len(other_files) == 0:
        info("Nothing to do")
        return

    info("Global venvs:")
    for global_venv in global_venvs:
        info("   *", global_venv.name)
    info("Other files:")
    for other_file in other_files:
        info("   >", other_file.name, "[dir]" if other_file.is_dir() else "[file]")

    if no_ask or ask("Do you want to delete all files that are no valid global environments?", default=True):
        for other_file in other_files:
            if other_file.is_file():
                log("Removing file", other_file)
                os.remove(other_file)
            elif other_file.is_dir():
                log("Removing directory", other_file)
                shutil.rmtree(other_file)

    info("Snape cleanup done")


snape_clean_parser = subcommands.add_parser(
    "clean",
    description="Delete unclassified files in the snape root directory\nwhich are no valid snape environments.",
    help="delete unclassified global environments"
)
snape_clean_parser.add_argument(
    "-l", "--local", "--here",
    help="check for a broken local environment",
    action="store_true", default=False, dest="here"
)
snape_clean_parser.add_argument(
    "-n", "--no-ask",
    help="do not ask before deleting unclassified files",
    action="store_true", default=False, dest="no_ask"
)
snape_clean_parser.set_defaults(func=snape_clean)

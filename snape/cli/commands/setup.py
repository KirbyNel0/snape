import shutil
from pathlib import Path

from snape.annotations import SnapeCancel
from snape.util import log, info, absolute_path, ask
from snape.config import SHELLS
from snape.env_var import SNAPE_REPO, SHELL, SNAPE_DIR
from snape.cli import subcommands


def snape_setup_init() -> None:
    """
    Initialize the snape installation

    For argument documentation, see ``snape_setup_parser``.
    """
    # Get shell-dependent arguments
    shell = SHELLS[SHELL]
    snape_shell_script: Path = SNAPE_REPO / "sh" / shell["snape_shell_script"]
    init_file: Path = absolute_path(shell["init_file"])
    source_alias: str = shell["source_alias"].format(snape_shell_script)
    # Only used by is_venv function: activate_file = shell["activate_file"]

    log("Shell:          ", SHELL)
    log("Shell init file:", init_file)
    log("Snape command:  ", source_alias)

    # The snape shell script must exist, otherwise this is not allowed to proceed
    if not snape_shell_script.is_file():
        raise FileNotFoundError(f"Snape shell script not found: {snape_shell_script}")

    # Check whether the alias exists
    with open(init_file, "r") as f:
        content = f.readlines()
        if source_alias in content:
            info(f"Snape has already been initialized for the {SHELL} shell, nothing changed")
            raise SnapeCancel()
        log(source_alias, "not found in", init_file)

    # Write the alias
    with open(init_file, "a") as f:
        f.writelines(["\n", source_alias])

    info("Initialized snape for", SHELL, "at", init_file)


def snape_setup_remove(
    root: bool,
    init: bool
) -> None:
    """
    Undo snape initialization

    For argument documentation, see ``snape_setup_remove``.
    """
    argv = dict(**locals())

    # Get shell-dependent arguments
    shell = SHELLS[SHELL]
    snape_shell_script: Path = SNAPE_REPO / "sh" / shell["snape_shell_script"]
    init_file: Path = absolute_path(shell["init_file"])
    source_alias: str = shell["source_alias"].format(snape_shell_script)
    # Only used by is_venv function: activate_file = shell["activate_file"]

    log("Shell:          ", SHELL)
    log("Shell init file:", init_file)
    log("Snape command:  ", source_alias)

    # Check if any arguments were given
    if all(map(lambda x: not x, vars(argv).values())):
        log("No arguments given")
        info("Nothing to do")

    if root:
        log("Attempting to remove", SNAPE_DIR)
        if ask("Are you sure you want to remove all global environments?", default=False):
            log("Removing", SNAPE_DIR)
            shutil.rmtree(SNAPE_DIR)
            if SNAPE_DIR.is_dir():
                raise RuntimeError(f"Could not remove {SNAPE_DIR}")
            else:
                log("Removed", SNAPE_DIR)
                info("Successfully removed all global environments")

    if init:
        with open(init_file, "r") as f:
            content = f.readlines()
            if source_alias in content:
                content.remove(source_alias)
                new_content = content
            else:
                info("Snape has not yet been initialized for", SHELL)
                new_content = None
            del content

        if new_content is not None:
            log("Writing edited file contents to", init_file)
            with open(init_file, "w") as f:
                f.writelines(new_content)
            info("Successfully removed snape from", SHELL)


# The subcommand parser for ``snape setup``.
snape_setup_parser = subcommands.add_parser(
    "setup",
    description="Manage the snape installation.",
    help="manage the snape installation"
)
snape_setup_subcommands = snape_setup_parser.add_subparsers(title="commands", help=None, required=True)

snape_setup_init_parser = snape_setup_subcommands.add_parser(
    "init",
    description="Initialize the snape installation.",
    help="initialize the snape installation"
)
snape_setup_init_parser.set_defaults(func=snape_setup_init)

snape_setup_remove_parser = snape_setup_subcommands.add_parser(
    "remove",
    description="Remove the snape installation",
    help="remove the snape installation"
)
snape_setup_remove_parser.add_argument(
    "-i", "--init",
    help="undo the effects of snape setup init",
    action="store_true", default=False, dest="init"
)
# Remove all global environments as well
snape_setup_remove_parser.add_argument(
    "-r", "--root",
    help="remove the $SNAPE_ROOT directory containing all environments",
    action="store_true", default=False, dest="root"
)
snape_setup_remove_parser.set_defaults(func=snape_setup_remove)

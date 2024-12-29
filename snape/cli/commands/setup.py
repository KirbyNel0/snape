import shutil
from pathlib import Path

from snape import env_var
from snape.annotations import SnapeCancel
from snape.cli._parser import subcommands
from snape.config import SHELLS
from snape.util import log, info, absolute_path, ask

__all__ = [
    "snape_setup",
    "snape_setup_init",
    "snape_setup_remove"
]


def snape_setup() -> None:
    snape_setup_parser.print_help()


# The subcommand parser for ``snape setup``.
snape_setup_parser = subcommands.add_parser(
    "setup",
    description="Manage the snape installation.",
    help="manage the snape installation"
)
snape_setup_subcommands = snape_setup_parser.add_subparsers(title="commands", help=None, required=False)
snape_setup_parser.set_defaults(func=snape_setup)


def snape_setup_init() -> None:
    """
    Initialize the snape installation

    For argument documentation, see ``snape_setup_parser``.
    """
    # Get shell-dependent arguments
    shell = SHELLS[env_var.SHELL]
    snape_shell_script: Path = env_var.SNAPE_REPO_PATH / "sh" / f"snape.{env_var.SHELL}"
    init_file: Path = absolute_path(shell["init_file"])
    source_line: str = f"source '{snape_shell_script}'"
    # Only used by is_venv function: activate_file = shell["activate_file"]

    log("Shell:          ", env_var.SHELL)
    log("Shell init file:", init_file)
    log("Snape command:  ", source_line)

    # The snape shell script must exist, otherwise this is not allowed to proceed
    if not snape_shell_script.is_file():
        raise FileNotFoundError(f"Snape shell script not found: {snape_shell_script}")

    if not init_file.is_file():
        log("Creating file", init_file)
        with open(init_file, "w"): pass

    # Check whether the source line exists
    with open(init_file, "r") as f:
        content = f.readlines()
        if source_line in content or source_line+"\n" in content:
            info(f"Snape has already been initialized for the {env_var.SHELL} shell, nothing changed")
            raise SnapeCancel()
        log(source_line, "not found in", init_file)

    # Write the source line
    with open(init_file, "a") as init_file_stream:
        print(source_line, file=init_file_stream)

    info("Initialized snape for", env_var.SHELL, "at", init_file)


snape_setup_init_parser = snape_setup_subcommands.add_parser(
    "init",
    description="Initialize the snape installation.",
    help="initialize the snape installation"
)
snape_setup_init_parser.set_defaults(func=snape_setup_init)


def snape_setup_remove(
        argv: list[str]
) -> None:
    """
    Undo snape initialization

    For argument documentation, see ``snape_setup_remove``.
    """

    # Get shell-dependent arguments
    shell = SHELLS[env_var.SHELL]
    snape_shell_script: Path = env_var.SNAPE_REPO_PATH / "sh" / f"snape.{env_var.SHELL}"
    init_file: Path = absolute_path(shell["init_file"])
    source_line: str = f"source '{snape_shell_script}'"
    # Only used by is_venv function: activate_file = shell["activate_file"]

    log("Shell:          ", env_var.SHELL)
    log("Shell init file:", init_file)
    log("Snape command:  ", source_line)

    # Check if any arguments were given
    if len(argv) == 0:
        log("No arguments given")
        info("Nothing to do")

    if "root" in argv:
        log("Attempting to remove", env_var.SNAPE_ROOT_PATH)
        if ask("Are you sure you want to remove all global environments?", default=False):
            log("Removing", env_var.SNAPE_ROOT_PATH)
            shutil.rmtree(env_var.SNAPE_ROOT_PATH)
            if env_var.SNAPE_ROOT_PATH.is_dir():
                raise RuntimeError(f"Could not remove {env_var.SNAPE_ROOT_PATH}")
            else:
                log("Removed", env_var.SNAPE_ROOT_PATH)
                info("Successfully removed all global environments")

    if "init" in argv:
        with open(init_file, "r") as f:
            content = f.readlines()
            if source_line in content:
                content.remove(source_line)
                new_content = content
            elif source_line+"\n" in content:
                content.remove(source_line+"\n")
                new_content = content
            else:
                info("Snape has not yet been initialized for", env_var.SHELL)
                new_content = None
            del content

        if new_content is not None:
            log("Writing edited file contents to", init_file)
            with open(init_file, "w") as f:
                f.writelines(new_content)
            info("Successfully removed snape from", env_var.SHELL)


snape_setup_remove_parser = snape_setup_subcommands.add_parser(
    "remove",
    description="Remove the snape installation",
    help="remove the snape installation"
)
snape_setup_remove_parser.add_argument(
    "-a", "--all",
    help="remove everything snape changed in your current shell",
    action="store_const", const=["init", "root"], default=[], dest="argv"
)
snape_setup_remove_parser.add_argument(
    "-i", "--init",
    help="undo the effects of snape setup init",
    action="append_const", const="init", default=None, dest="argv"
)
# Remove all global environments as well
snape_setup_remove_parser.add_argument(
    "-r", "--root",
    help="remove the $SNAPE_ROOT directory containing all environments",
    action="append_const", const="root", default=None, dest="argv"
)
snape_setup_remove_parser.set_defaults(func=snape_setup_remove)

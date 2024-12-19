#!/usr/bin/python3

import argparse
import os
import shutil
import sys
import json
import subprocess
from pathlib import Path
from typing import TypedDict

import venv

# Shell portability: Dicts of this type provide information on how to use snape with a given shell.
# See ``snape setup``.
ShellInfo = TypedDict("ShellInfo", {
    # The path to the default init file for the shell
    "init_file": Path,
    # The command which should be written to "init_file" to activate snape. {} is replaced by the "snape_file" value.
    "source_alias": str,
    # A file name relative to "snape/sh/" pointing to the shell script to execute
    "snape_shell_script": str,
    # A file name relative to a virtual environment root pointing to the activation shell script
    "activate_file": str
})

shells: dict[str, ShellInfo] = {
    "bash": {
        "init_file": Path("~/.bashrc"),
        "source_alias": "alias snape='source {}'",
        "snape_shell_script": "snape.bash",
        "activate_file": "bin/activate"
    },
    "fish": {
        "init_file": Path("~/.config/fish/config.fish"),
        "source_alias": "function snape; source '{}' $argv; end",
        "snape_shell_script": "snape.fish",
        "activate_file": "bin/activate.fish"
    }
}

FORBIDDEN_ENV_NAMES = [
    # The call ``snape here`` is handled differently by the shell script, so no environment with that name is allowed
    "here",
    "--here"
]
"""
Used to prevent the user from unwanted venv creation when wanting to call a subcommand.

If the user tries to create a venv named as any item of this list, an error is thrown (see ``new`` subcommand).
The names of options and subcommands are added automatically.
"""

# Select the current shell as default.
# This can be changed via command line option and is applied in ``__main__``.
SHELL = os.getenv("SHELL").split("/")[-1]

# The currently active python environment.
VIRTUAL_ENV = os.getenv("VIRTUAL_ENV")

# Load environment variables.
# Their existence is ensured by the shell script.
SNAPE_ROOT = os.getenv("SNAPE_ROOT")
"The directory of all global snape environments."
SNAPE_VENV = os.getenv("SNAPE_VENV")
"The name of the default global snape environment."
SNAPE_LOCAL_VENV = os.getenv("SNAPE_LOCAL_VENV")
"The name of local snape environments."

# Apply environment variables
SNAPE_DIR = Path(SNAPE_ROOT).expanduser().resolve().absolute() if SNAPE_ROOT is not None else None
"The directory of all global snape environments. If this is not a directory, the script will throw an error."

# Save repo root
SNAPE_REPO = Path(__file__).parent.parent.expanduser().resolve().absolute()

def is_venv(env: Path) -> bool:
    """
    Checks whether the given path points to a python virtual environment.
    This function is shell dependant and performs its checks depending on the global ``SHELL`` variable.

    :param env: The path to check.
    :return: Whether the specified path contains an activation file and python binary.
    """
    return (env / shells[SHELL]["activate_file"]).is_file() and (env / "bin/python")


def is_active_venv(env: Path) -> bool:
    """
    Checks whether the specified environment is the currently active python environment.

    :param env: The path to check.
    :return: Whether the specified environment is currently active.
    """
    return VIRTUAL_ENV is not None \
        and Path(VIRTUAL_ENV).expanduser().resolve().absolute() == env.expanduser().resolve().absolute()


def error(status: int, *message, **kwargs) -> None:
    """
    Outputs error messages and terminates the application.

    Prints all specified objects to standard error output using the ``print`` function.
    Terminates the application with exit code ``status``.

    Error messages will always be printed.

    :param status: The exit code of the application.
    :param message: Messages to print.
    :param kwargs: Arguments to pass to ``print``.
    """
    print(*message, **kwargs, file=sys.stderr)
    exit(status)


def info(*message, **kwargs) -> None:
    """
    Output informational messages.

    Prints all specified objects to standard output using the ``print`` function.

    If option ``-q`` is present, this method will no longer output anything (see ``main()``).

    :param message: Messages to print.
    :param kwargs: Arguments to pass to ``print``.
    """
    print(*message, **kwargs)


def log(*message, **kwargs) -> None:
    """
    Output debug log messages.

    Prints all specified objects to standard output using the ``print`` function.

    This method will only work if option ``-v`` is present (see ``main()``).

    :param message: Messages to print.
    :param kwargs: Arguments to pass to ``print``.
    """
    pass


def ask(prompt: str, default: bool | None) -> bool:
    """
    Prompts the user to enter either yes (``y``/``Y``) or no (``n``/``N``).
    If a default is specified, no input will result into that output.
    Only single letter input will be accepted (case-insensitive).

    :param prompt: The thing to ask the user. Will be printed to standard output together with ``[y/n]`` question.
    :param default: The default result to return if the user enters nothing.
        If `None`, the user is required to enter something.
    :return: The user's selection as ``bool``.
    """
    if default is None:
        default_str = "[y/n]"
    else:
        default_str = "[Y/n]" if default else "[y/N]"
    
    while True:
        answer = input(f"{prompt} {default_str} ")
        if answer in ("y", "Y"):
            return True
        elif answer in ("n", "N"):
            return False
        elif answer == "" and default is not None:
            return default


# The parser of the application.
# For more information, see the ``subcommands`` object.
parser = argparse.ArgumentParser(
    prog="snape",
    description="""
    Snape: Manage python virtual environments from everywhere.
    
activate:
    To activate an environment named "env", use "snape env".
    If "env" is not provided, snape will activate the default
    environment ($SNAPE_VENV variable, default: .snape).
    If an active snape environment is detected, it will be
    deactivated before activating the new one.

deactivate:
    To deactivate an active environment, simply run "snape"
    without any arguments.

environment variables:
    Snape manages its environments using the python-venv
    package inside the $SNAPE_ROOT directory (default: ~/.snape).

local environments:
    By default, snape environments are created globally and can
    be activated from anywhere. To create a local environment,
    call "snape new --here". To activate/deactivate it, call
    "snape --here". To delete it, call "snape delete --here".

technical:
    Snape works by sourcing a bash script which will then invoke
    a python script. Inside the bash script, the virtual
    environments will be activated if requested. Anything else
    is managed by python. Therefor, snape is shell-dependent
    and requires you to install the python-venv package.
    """,
    formatter_class=argparse.RawTextHelpFormatter
)

# The command line option used to select the shell.
# This will be applied globally for the script (see __main__).
parser.add_argument(
    "-s", "--shell",
    help=f"select a specific shell instead of the current shell (default: {SHELL})",
    action="store", default=None, metavar="SHELL"
)
parser.add_argument(
    "-q", "--quiet",
    help="keep the command line output as minimal as possible",
    action="store_true", default=False, dest="quiet"
)
parser.add_argument(
    "-v", "--verbose",
    help="output debug output",
    action="store_true", default=False, dest="verbose"
)

subcommands = parser.add_subparsers(title="commands", help=None, required=True)
"""
The object containing all subcommands. The application will only run if a subcommand is given.

All subcommands (e.g. new/delete) are defined below in their own separate sections.
Each of these subcommands can implement custom logic in a function.
That function receives all arguments passed to the subcommand as object and can then process them.
The function must be registered as default for the "func" parameter to that subcommand.

All arguments should be copied to local variables at the beginning of a function to make the code more readable.

Example:
    
    def my_func(argv: argparse.Namespace): ...
    subcommand = subparsers.add_parser(...)
    subcommand.set_defaults(func=my_func)

With this, the subcommand will work properly with the application.

Naming conventions: snape_name for subcommands, snape_name_parser for corresponding function.
"""

# ======================================== #
# SETUP                                    #
# ---------------------------------------- #
 # INIT                                   #
# ---------------------------------------- #
 # REMOVE                                 #
 #   -r root: bool                        #
 #   -i init: bool                        #
# ======================================== #

def snape_setup_init(_: argparse.Namespace) -> None:
    """
    Initialize the snape installation

    For argument documentation, see ``snape_setup_parser``.
    """
    # Get shell-dependent arguments
    shell = shells[SHELL]
    snape_shell_script: Path = SNAPE_REPO / "sh" / shell["snape_shell_script"]
    init_file: Path = Path(shell["init_file"]).expanduser().resolve().absolute()
    source_alias: str = shell["source_alias"].format(snape_shell_script)
    # Only used by is_venv function: activate_file = shell["activate_file"]

    log("Shell:          ", SHELL)
    log("Shell init file:", init_file)
    log("Snape command:  ", source_alias)

    # The snape shell script must exist, otherwise this is not allowed to proceed
    if not snape_shell_script.is_file():
        error(1, "Snape shell script not found:", snape_shell_script)

    # Check whether the alias exists
    with open(init_file, "r") as f:
        content = f.readlines()
        if source_alias in content:
            info(f"Snape has already been initialized for the {SHELL} shell, nothing changed")
            exit(0)
        log(source_alias, "not found in", init_file)

    # Write the alias
    with open(init_file, "a") as f:
        f.writelines(['\n', source_alias])

    info("Initialized snape for", SHELL, "at", init_file)


def snape_setup_remove(argv: argparse.Namespace) -> None:
    """
    Undo snape initialization

    For argument documentation, see ``snape_setup_remove``.
    """
    root: bool = argv.root
    init: bool = argv.init

    # Get shell-dependent arguments
    shell = shells[SHELL]
    snape_shell_script: Path = SNAPE_REPO / "sh" / shell["snape_shell_script"]
    init_file: Path = Path(shell["init_file"]).expanduser().resolve().absolute()
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
                error(1, "Could not remove", SNAPE_DIR)
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


# ======================================== #
# STATUS                                   #
# ---------------------------------------- #
# snape status                             #
#    -r raw: bool                          #
# ======================================== #

def snape_status(argv: argparse.Namespace) -> None:
    """
    Outputs information on the current venv and snape status.

    For argument documentation, see ``snape_status_parser``.
    """
    raw: bool = argv.raw

    local_venv = Path(SNAPE_LOCAL_VENV).expanduser().resolve().absolute()

    # Construct information
    python_venv = VIRTUAL_ENV
    snape_env = VIRTUAL_ENV.split("/")[-1] if VIRTUAL_ENV else None
    if snape_env and snape_env != SNAPE_LOCAL_VENV and SNAPE_DIR not in Path(python_venv).parents:
        # Neither local nor global snape managed environment
        snape_env = None
    snape_dir = SNAPE_DIR
    snape_envs = [
        env
        for env in (os.listdir(SNAPE_DIR) if SNAPE_DIR.is_dir() else [])
        if is_venv(SNAPE_DIR / env)
    ]
    snape_default = SNAPE_VENV
    local_active = False if python_venv is None else Path(python_venv).expanduser().resolve().absolute() == local_venv
    local_exists = bool(local_venv.is_dir() and is_venv(local_venv))
    local_default = SNAPE_LOCAL_VENV

    # All variables constructed locally should be printed out
    # All functional objects must be removed from the output.
    status = locals()
    status.pop("raw")
    status.pop("argv")
    log(json.dumps(status, indent=4, default=str))

    # If requested: Output the collected information as json.
    if raw:
        # Print everything
        print(json.dumps(status, indent=4, default=str))
        return

    snape_envs_str = []
    for env in snape_envs:
        prefix = "  \033[32m*\033[0m" if env == snape_env else "  *"
        suffix = "(default)" if env == snape_default else ""
        snape_envs_str.append(f"{prefix} {env} {suffix}")

    local_active_status = "\033[32m*\033[0m active" if local_active else "inactive"
    local_exists_status = "exists" if local_exists else "no venv found"

    indent = '\n\t'
    print(
        f"""\
Python venv:
    Current:       {python_venv}

Global snape environments:
    Snape root:    {snape_dir}
    Available environments:
        {indent.join(snape_envs_str)}

Local snape environments:
    Name of local venvs: {local_default}
    Current directory:   {local_exists_status}
    Status:              {local_active_status}"""
    )


# The subcommand parser for ``snape status``
snape_status_parser = subcommands.add_parser(
    "status",
    description="List information on the current snape status.",
    help="list information on the current snape status"
)
# Whether to print out as json
snape_status_parser.add_argument(
    "-r", "--raw",
    help="print all information as json",
    action="store_true", default=False, dest="raw"
)
snape_status_parser.set_defaults(func=snape_status)


# ======================================== #
# HELP                                     #
# ======================================== #

def snape_help(_: argparse.Namespace) -> None:
    """
    Prints out help on snape. Same as ``snape --help``.
    """
    parser.print_help()


# The subcommand parser for ``snape help``.
snape_help_parser = subcommands.add_parser(
    "help",
    description="Print snape's default help",
    help="print this help and exit",
)
snape_help_parser.set_defaults(func=snape_help)


# ======================================== #
# LIST                                     #
# ======================================== #

def snape_list(argv: argparse.Namespace):
    log("Functionality not yet implemented")
    raise NotImplemented


snape_list_parser = subcommands.add_parser(
    "list",
    description="List information on a specific snape environment.",
    help="list information on a specific snape environment"
)
snape_list_parser.set_defaults(func=snape_list)


# ======================================== #
# NEW                                      #
# ---------------------------------------- #
# snape new                                #
#       env: str                           #
#    -r requirements: str | None           #
#    -u no_update: bool                    #
#    -q requirements_quiet: bool           #
#    -l here: bool                         #
#    -o overwrite: bool                    #
# ======================================== #


def snape_new(argv: argparse.Namespace):
    """
    Create new global or local virtual environments.

    For argument documentation, see ``snape_new_parser``.
    """
    env_name: str | None = argv.env
    no_upgrade: bool = argv.no_update
    requirements: str | None = argv.requirements
    requirements_quiet: bool = argv.requirements_quiet
    here: bool = argv.here
    overwrite: bool = argv.overwrite

    # The name of the new environment to create
    env_name: str
    # The full path to the new environment (ends in ``env_name``)
    new_venv: Path

    if here:
        # New local environment
        # Uses the default local environment name for snape, so no other name can be provided
        if env_name is not None:
            error(3, "snape new --here: Cannot provide environment name")
        env_name = SNAPE_LOCAL_VENV
        new_venv = Path.cwd() / env_name
    else:
        # New global environment
        # A name for the new environment must be provided
        if env_name is None:
            error(3, "snape new: No environment name provided")
        new_venv = SNAPE_DIR / env_name

    log("Directory for new venv:", new_venv)

    # Check whether the name of the new environment does not conflict with other stuff
    if env_name in FORBIDDEN_ENV_NAMES:
        error(3, f"Illegal environment name: {env_name}")

    # If the directory of the venv already exists, this must be handled differently
    if new_venv.is_dir():
        # Check whether the directory for the new venv is a normal directory and throw an error if so
        if not is_venv(new_venv):
            error(3, f"Directory '{SNAPE_VENV}' exists and is not a snape environment")

        # Ask whether an old venv should be overwritten
        if not overwrite:
            if not ask(f"Environment '{env_name}' does already exist. Overwrite?", default=False):
                exit(1)

    # Check whether requirements must be installed into the new environment
    if requirements is not None:
        requirements_file = Path(requirements)
        if not requirements_file.is_file():
            error(1, "Requirements file not found:", requirements_file)
    else:
        requirements_file = None

    log("Requirements file:", requirements_file)

    # Create environment
    log("Creating new environment at", new_venv)
    info("Creating snape environment:", env_name)
    venv.create(new_venv, clear=True, with_pip=True, upgrade_deps=not no_upgrade)

    # Install requirements
    if requirements_file:
        info("Installing requirements")
        process = subprocess.run(
            [str(new_venv / "bin/pip"), "install", "-r", str(requirements_file)],
            capture_output=requirements_quiet
        )
        if process.stdout:
            log(process.stdout.decode())


# The subcommand parser for ``snape new``.
snape_new_parser = subcommands.add_parser("new", help="create a new environment", aliases=["touch"])
# The name of the new environment
snape_new_parser.add_argument(
    "env", nargs="?",
    help="the name of the new environment",
    action="store", default=None
)
# Whether to prompt the user for existing venv
snape_new_parser.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments without prompting first",
    action="store_true", default=False, dest="overwrite"
)
# Whether to update pip (see venv package), this usually takes a while
snape_new_parser.add_argument(
    "-n", "--no-update",
    help="do not update pip after initializing the environment",
    action="store_true", default=False, dest="no_update"
)
# Can be given to specify a requirements.txt file into the new environment
snape_new_parser.add_argument(
    "-r", "--requirements",
    help="install the specified file into the environment",
    action="store", default=None, metavar="FILE", dest="requirements"
)
# If specified with -r, the output of 'pip install -r' will not be printed
snape_new_parser.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing requirements",
    action="store_true", default=False, dest="requirements_quiet"
)
# If specified, a local environment will be created instead of a global one
snape_new_parser.add_argument(
    "-l", "--local", "--here",
    help="create a snape environment in the current directory. "
         "not allowed to provide 'env'.",
    action="store_true", default=False, dest="here"
)
snape_new_parser.set_defaults(func=snape_new)


# ======================================== #
# DELETE                                   #
# ---------------------------------------- #
#    -f no_ask: bool                       #
#    -e ignore_not_exists: bool            #
#    -l here: bool                         #
#    -r ignore_active: bool                #
# ======================================== #

def snape_delete(argv: argparse.Namespace):
    """
    Delete a existing global or local snape environments.

    For argument documentation, see ``snape_delete_parser``.
    """
    env_name: str | None = argv.env
    ignore_not_exists: bool = argv.ignore_not_exists
    here: bool = argv.here
    no_ask: bool = argv.no_ask
    ignore_active: bool = argv.ignore_active

    if here:
        # Delete local environment
        # Uses the default local environment name for snape, so no other name can be provided
        if env_name is not None:
            error(3, "snape delete --here: Cannot provide an environment name")
        env_name = SNAPE_LOCAL_VENV
        old_venv = Path.cwd() / env_name
    else:
        # Delete global environment
        # The name of the environment must be provided
        if env_name is None:
            error(3, "snape delete: No environment name provided")
        old_venv = SNAPE_DIR / env_name

    log("Directory of old venv:", old_venv)

    # If the old_venv does not point to any directory, throw an error
    if not old_venv.is_dir():
        if ignore_not_exists:
            exit(0)
        error(4, f"Directory not found:", old_venv)

    # If a regular folder instead of a venv, throw an error
    if not is_venv(old_venv):
        error(3, f"Not a python virtual environment:", old_venv)

    # Check if the environment which should be deleted is currently active
    if not ignore_active and is_active_venv(old_venv):
        error(1, "The specified environment is currently active. Please deactivate it before deletion.")

    locality = "local" if here else "global"
    if no_ask or ask(f"Are you sure you want to delete the {locality} environment '{env_name}'?", False):
        # Remove everything
        shutil.rmtree(old_venv)
        if not old_venv.is_dir():
            info("Successfully deleted", env_name)
        else:
            info("Partially deleted", env_name)
            exit(1)


# The subcommand parser for ``snape delete``.
snape_delete_parser = subcommands.add_parser("delete", help="delete an existing environment", aliases=["rm"])
# The name of the environment to delete
snape_delete_parser.add_argument(
    "env", nargs="?",
    help="the name of the environment to delete",
    action="store", default=None
)
# Do not prompt before deletion
snape_delete_parser.add_argument(
    "-f", "--no-ask",
    help="do not ask before deleting the environment",
    action="store_true", default=False, dest="no_ask"
)
# Whether to ignore non-existing directories
snape_delete_parser.add_argument(
    "-e", "--ignore-not-exists",
    help="do not throw an error if the environment does not exist",
    action="store_true", default=False, dest="ignore_not_exists"
)
# If specified, a local environment will be deleted instead of a global one
snape_delete_parser.add_argument(
    "-l", "--local", "--here",
    help="remove the snape environment from the current directory. "
         "not allowed to provide 'env'.",
    action="store_true", default=False, dest="here"
)
# Continue if environment is currently active
snape_delete_parser.add_argument(
    "-r", "--ignore-active",
    help="do not exit if the specified environment is currently active",
    action="store_true", default=False, dest="ignore_active"
)
snape_delete_parser.set_defaults(func=snape_delete)

# ======================================== #
# POSSESS                                  #
# ---------------------------------------- #
#       env: str                           #
#    -l here: bool                         #
#    -n global_name: str                   #
#    -r ignore_active: bool                #
#    -a no_ask: bool                       #
#    -o overwrite: bool                    #
#    -d delete_old: bool                   #
#    -q requirements_quiet: bool           #
# ======================================== #


def snape_possess(argv: argparse.Namespace) -> None:
    """
    Make an arbitrary virtual environment available to snape by copying its dependencies into a new environment
    which is then managed by snape.

    For argument documentation, see ``snape_possess_parser``.
    """
    env_name: str = argv.env
    here: bool = argv.here
    global_name: str | None = argv.global_name
    ignore_active: bool = argv.ignore_active
    no_ask: bool = argv.no_ask
    overwrite: bool = argv.overwrite
    delete_old: bool = argv.delete_old
    requirements_quiet: bool = argv.requirements_quiet

    old_venv = Path(env_name).expanduser().resolve().absolute()
    log("Localizing environment:", old_venv)

    # Check whether the original environment even exists
    if not old_venv.is_dir():
        error(1, "Not a directory:", env_name)

    # Check whether the original environment is an environment
    if not is_venv(old_venv):
        error(1, "Not a python virtual environment:", env_name)

    # Check whether the environment is located at snape root (is global environment)
    if old_venv.parent == SNAPE_DIR:
        log("Old environment is already known to snape")
        info("Nothing to do")
        exit(0)

    # Validate the name for a new global environment. If not specified, the old name will be re-used.
    if global_name is None:
        global_name = old_venv.name
    else:
        if here:
            error(1, "Local environment requested, global environment name specified. What should I do now, Potter?")
        if global_name in FORBIDDEN_ENV_NAMES:
            error(1, "Illegal environment name:", global_name)

    # Global environments can have arbitrary names. Local environments must have the default local environment name.
    if here:
        new_venv = old_venv.parent / SNAPE_LOCAL_VENV
    else:
        new_venv = SNAPE_DIR / global_name

    # Check whether the new environment is the same as the old one
    # This can happen for local environments already having the correct name
    if new_venv == old_venv:
        log("New environment points to old name")
        info("Nothing to do")
        exit(0)

    log("New name for venv:", new_venv)

    if new_venv.is_dir():
        # Check whether the directory for the new venv is a normal directory and throw an error if so
        if not is_venv(new_venv):
            error(3, f"Directory '{SNAPE_LOCAL_VENV}' exists and is not a snape environment")

        # Ask whether an old venv should be overwritten
        if not overwrite:
            if not ask(f"Environment '{env_name}' does already exist. Overwrite?", default=False):
                exit(1)

    # If the environment is active, warn the user
    if not ignore_active and is_active_venv(old_venv):
        error(1, "The specified environment is currently active. Please deactivate it before this operation.")

    # Read package list from old environment
    try:
        log("Fetching old packages (pip freeze)")
        old_pip = subprocess.run([old_venv / "bin/pip", "freeze"], capture_output=True)
    except subprocess.CalledProcessError as e:
        log("Failed to fetch package list:", e)
        old_pip = None

    if not old_pip:
        error(1, "Cannot read package list from", old_venv)

    # Create package list
    packages: list[str] = list(filter(lambda x: x, old_pip.stdout.decode().split("\n")))
    log("Package list:", packages)
    if old_pip.stderr:
        log("ERRORS:", old_pip.stderr.decode())
    if len(packages) == 0:
        info(f"Note: No additional packages were installed in '{env_name}'")

    # Create output and prompt
    locality = "local" if here else "global"
    question = f"Do you want to create a new {locality} environment named '{new_venv.name}' with the requirements of '{env_name}'?"
    if not no_ask and not ask(question, default=True):
        exit(1)

    # Create environment
    log("venv.create(...)")
    info("Creating snape environment:", new_venv.name)
    venv.create(new_venv, with_pip=True, upgrade_deps=True, clear=overwrite)
    log("pip install")

    # Install packages
    if packages:
        info("Installing dependencies")
        new_pip = subprocess.run(
            [new_venv / "bin/pip", "install"] + packages,
            capture_output=requirements_quiet
        )
        # Output stdout
        if new_pip.stdout:
            log(new_pip.stdout.decode())
        # Output errors
        if new_pip.returncode != 0:
            info("Could not install all requirements")
            if new_pip.stderr:
                log(new_pip.stderr.decode())

    # Delete old environment
    if delete_old:
        info("Removing old environment")
        shutil.rmtree(old_venv)
        if old_venv.is_dir():
            error(1, "Could not delete old environment")
        else:
            log("Successfully removed old environment")


# The subcommand parser for ``snape possess``.
snape_possess_parser = subcommands.add_parser(
    "possess",
    description="Make a local environment available to snape.\n"
                "Snape will create a new environment it can manage and install all packages from the old venv into it.",
    help="have snape take over a local environment"
)
# The name of the environment to manage
snape_possess_parser.add_argument(
    "env",
    help="the name or path to the environment to make available to snape",
    action="store"
)
# Whether to make the new environment a global one
snape_possess_parser.add_argument(
    "-l", "--local", "--here",
    help="make the new environment local, not global",
    action="store_true", default=False, dest="here"
)
# A new name for the new global environment
snape_possess_parser.add_argument(
    "-n", "--global-name",
    help="give the new environment an other name. without this, it will have the same name as the old environment.",
    action="store", default=None, dest="global_name", metavar="NAME"
)
# Continue if environment is currently active
snape_possess_parser.add_argument(
    "-i", "--ignore-active",
    help="do not exit if the specified environment is currently active",
    action="store_true", default=False, dest="ignore_active"
)
# Whether to prompt the user for existing venv
snape_possess_parser.add_argument(
    "-o", "--overwrite",
    help="overwrite existing environments having the same name as the environment's new name",
    action="store_true", default=False, dest="overwrite"
)
snape_possess_parser.add_argument(
    "-a", "--no-ask",
    help="do not prompt before creating the new environment",
    action="store_true", default=False, dest="no_ask"
)
snape_possess_parser.add_argument(
    "-q", "--quiet",
    help="hide output from pip when installing requirements",
    action="store_true", default=False, dest="requirements_quiet"
)
snape_possess_parser.add_argument(
    "-d", "--delete-old",
    help="delete the old environment after it has been copied successfully",
    action="store_true", default=False, dest="delete_old"
)
snape_possess_parser.set_defaults(func=snape_possess)

# ======================================== #
# FINALIZE                                 #
# ======================================== #

# Mark the names of all snape arguments as illegal venv names
FORBIDDEN_ENV_NAMES.extend(parser._option_string_actions.keys())

# Mark the names of all subcommands as illegal venv names
FORBIDDEN_ENV_NAMES.extend(parser._actions[-1].choices.keys())

def main() -> None:
    """
    Parses all arguments and applies the shell to use (``SHELL`` variable). Afterward, runs the function of a given
    subcommand.
    """
    args = parser.parse_args()

    if args.shell is not None:
        global SHELL
        if args.shell not in shells:
            error(1, "Unsupported shell:", args.shell)
        SHELL = args.shell

    if args.quiet:
        def quiet(*_, **__):
            pass
        global info
        info = quiet

    if args.verbose:
        def verbose(*_args, **_kwargs):
            print("\033[33m+", *_args, "\033[0m", **_kwargs)
        global log
        log = verbose
        log("Debug output enabled")
        if args.quiet:
            log("Informational output hidden")
        log("Enabled shell:", SHELL)

    if args.func != snape_setup_init and SNAPE_DIR is not None and not SNAPE_DIR.is_dir():
        error(1, f"Snape root is not a valid directory ({SNAPE_DIR})")

    # Done preprocessing
    func = args.func
    delattr(args, "shell")
    delattr(args, "func")
    delattr(args, "quiet")
    delattr(args, "verbose")

    log(func.__name__ + '(' + ",".join(map(lambda x: f"{x[0]} = {x[1]}", vars(args).items())) + ')')
    func(args)


if __name__ == "__main__":
    main()

import argparse

from snape import env_var
from snape.config import SHELLS


__all__ = [
    "parser",
    "subcommands"
]


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
    help=f"select a specific shell instead of the current shell (default: {env_var.SHELL})",
    action="store", default=None, metavar="SHELL", choices=list(SHELLS.keys())
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
That function receives all arguments passed to the subcommand and can then process them.
The function must be registered as default for the ``func`` parameter to that subcommand.

All arguments should be copied to local variables at the beginning of a function to make the code more readable.

Example:

    from snape.cli.parser import subcommands
    def snape_foo(...): ...
    snape_foo_parser = subcommands.add_parser(title="foo", ...)
    snape_foo_parser.set_defaults(func=my_func)

With this, the subcommand will work properly with the application.

Naming conventions: snape_name for subcommands, snape_name_parser for corresponding function.
"""

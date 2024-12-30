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
 Snape is a wrapper tool around the "venv" python package.
 It can (de)activate virtual environments for you and manage them.

activate:
  To activate an environment named "my-venv", call "snape my-venv".
  If the environment's name is not provided, snape will activate the default environment.
  If an active snape environment is detected, it will be deactivated before activating the new one.
  Activation can only be done when snape receives a single command line argument.

deactivate:
  To deactivate an active environment, simply run "snape" without any arguments.

global environments:
  By default, snape environments are accessible for your whole system.
  Such environments are called global environments.
  The location of those environments can be modified by setting the SNAPE_ROOT shell variable (default: ~/.snape).
  Snape manages one default global environment whose name can be modified by setting the SNAPE_VENV shell variable (default: snape).

local environments:
  To work with an environment inside the current working directory, most snape commands offer the "--local" switch.
  Each directory can only contain a single local environment managed by snape.
  The name of such environments can be modified by setting the SNAPE_LOCAL_VENV shell variable (default: .snape).

technical:
  Snape manages its environments using the python-virtualenv package.
  When running the snape command, you will call a shell function which handles (de)activating virtual environments.
  Anything else is managed using a python backend.
  Due to this behavior, snape is shell-dependent and requires you to install the python-virtualenv package.\
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument(
    "-s", "--shell",
    help=f"select a specific shell, especially useful for snape setup (current: {env_var.SHELL})",
    action="store", default=None, metavar="SHELL", choices=list(SHELLS.keys())
)

parser_logging = parser.add_argument_group("logging")
parser_logging.add_argument(
    "-q", "--quiet",
    help="disable informational output",
    action="store_true", default=False, dest="quiet"
)
parser_logging.add_argument(
    "-v", "--verbose",
    help="enable debug output",
    action="store_true", default=False, dest="verbose"
)

subcommands = parser.add_subparsers(title="commands", help=None, required=True)
"""
The object containing all subcommands. The application will only run if a subcommand is given.

All subcommands (e.g. new/delete) are defined in separate files (e.g. snape/cli/commands/new.py).
Each of these subcommands can implement custom logic in a function.
That function receives all arguments passed to the subcommand and can then process them.
The function must be registered as default for the ``func`` parameter to that subcommand.

Example:

    from snape.cli._parser import subcommands
    
    def snape_foo(bar: bool):
        print("Bar" if bar else "No bar")
    
    snape_foo_parser = subcommands.add_parser(title="foo", description="...", help="...")
    snape_foo_parser.add_argument("-b", "--foo-bar", action="store_true", dest="bar", default=False)
    snape_foo_parser.set_defaults(func=snape_foo)

With this, the subcommand will work properly with snape's cli.

Naming conventions: snape_name for function, snape_name_parser for corresponding parser.
"""

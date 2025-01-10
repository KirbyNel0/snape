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
  Call snape without any arguments to activate an environment inside the current
  working directory or any of its parent directories.
  To activate a global environment named "my-venv", call "snape my-venv".
  If an active environment is detected, it will be deactivated before activating the new one.
  Activation can only be done when snape receives a single or no command line argument.

deactivate:
  To deactivate an active environment, simply run "snape" without any arguments.

global environments:
  Snape environments which can be activated from anywhere are called global environments.
  The location of those environments can be modified by setting the SNAPE_ROOT shell variable (default: ~/.snape).

local environments:
  Virtual environments managed by snape not located inside the global environment directory are called local
  environments and can only be accessed when inside their directory.
  To work with local environments, most snape subcommands offer the "--local" switch.
  Each directory can only contain a single local environment managed by snape.
  The name of such environments can be modified by setting the SNAPE_VENV shell variable (default: .venv).

technical:
  Snape manages its environments using the venv package (other names: python3-virtualenv, python3-venv).
  When running the snape command, you will call a shell function which handles (de)activating virtual environments.
  Anything else is managed using a python backend.
  Due to this behavior, snape is shell-dependent and requires you to install the venv package.
  To change what python installation is used to run snape, set the SNAPE_PYTHON shell variable (default: /usr/bin/python3).
  That installation must have the venv package installed and should not be located inside a virtual environment.\
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

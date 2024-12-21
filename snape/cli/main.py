from typing import Callable, Any

from snape.cli import parser
from snape.cli.commands import snape_setup_init
from snape.config import FORBIDDEN_ENV_NAMES
from snape.env_var import SNAPE_DIR, SHELL
from snape.util import log, toggle_io

__all__ = [
    "main"
]

# Mark the names of all snape arguments as illegal venv names
FORBIDDEN_ENV_NAMES.extend(parser._option_string_actions.keys())

# Mark the names of all subcommands as illegal venv names
FORBIDDEN_ENV_NAMES.extend(parser._actions[-1].choices.keys())

def main() -> None:
    """
    Parses all arguments and applies the shell to use (``SHELL`` variable). Afterward, runs the function of a given
    subcommand.

    This function will modify objects from other modules to apply certain command line arguments. For example, if
    the user requests a quiet execution, the ``snape.util.info`` function will be redefined to not produce any output.

    This function will continue raising all exceptions each subcommand would raise. Therefor, they must be caught by
    a calling instance.
    """
    args = parser.parse_args()

    toggle_io(informational=not args.quiet, debug=args.verbose)

    if args.shell is not None:
        global SHELL
        SHELL = args.shell
    log("Enabled shell:", SHELL)

    # Ensure the root directory exists, except when snape is initialized for the first time
    if args.func != snape_setup_init and SNAPE_DIR is not None and not SNAPE_DIR.is_dir():
        raise NotADirectoryError(f"Snape root is not a valid directory: {SNAPE_DIR}")

    # Done preprocessing
    func: Callable[[Any, ...], None] = args.func
    delattr(args, "shell")
    delattr(args, "func")
    delattr(args, "quiet")
    delattr(args, "verbose")

    log(func.__name__ + "(" + ", ".join(map(lambda x: f"{x[0]} = {x[1]}", vars(args).items())) + ')')

    func(**vars(args))

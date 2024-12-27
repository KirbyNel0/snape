from typing import Callable, Any

from snape import env_var
from snape.cli._parser import parser
from snape.cli.commands import snape_setup_init
from snape.config import SHELLS
from snape.util import log, toggle_io

__all__ = [
    "main"
]


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
        env_var.__VARS__["SHELL"] = args.shell

    if env_var.SHELL not in SHELLS:
        raise KeyError(f"Snape does not support the shell '{env_var.SHELL}' yet")
    log("Enabled shell:", env_var.SHELL)

    # Ensure the root directory exists, except when snape is initialized for the first time
    if args.func != snape_setup_init and env_var.SNAPE_ROOT_PATH is not None and not env_var.SNAPE_ROOT_PATH.is_dir():
        raise NotADirectoryError(f"Snape root is not a valid directory: {env_var.SNAPE_ROOT_PATH}")

    # Done preprocessing
    func: Callable[[Any, ...], None] = args.func
    delattr(args, "shell")
    delattr(args, "func")
    delattr(args, "quiet")
    delattr(args, "verbose")

    log(func.__name__ + "(" + ", ".join(map(lambda x: f"{x[0]} = {x[1]}", vars(args).items())) + ')')

    func(**vars(args))

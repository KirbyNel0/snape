from typing import Callable, Any

from snape import env_var
from snape.cli._parser import parser
from snape.cli.commands import snape_setup_init
from snape.config import SHELLS
from snape.util import log, toggle_io

__all__ = [
    "main"
]


def main(args: list[str] | None = None) -> None:
    """
    Runs snape's command line interface (cli).

    All arguments passed to the script will be parsed and passed to the subcommand's function as keyword arguments.
    The keys are the attribute names of the ``argparse.Namespace`` object created by ``argparse``. All keys only
    used by snape and not the subcommand are removed. A subcommand may therefor not expect the following names as
    arguments: ``shell``, ``func``, ``quiet``, ``verbose``, ``global-env``, ``local-env``.

    On how to set up a subcommand, see ``snape.cli._parser.subcommands``.

    This function will modify objects from other modules to apply certain command line arguments:
    - The selected shell is saved inside the ``env_var.SHELL`` variable
    - The -v and -q options utilize the ``snape.util.io.toggle_io`` method

    This function will continue raising all exceptions each subcommand would raise. Therefor, they must be caught by
    a calling instance. When calling, consider applying the special meaning of ``snape.annotations.SnapeCancel``.

    :param args: If ``None``, parses the command line arguments (``sys.argv``), the specified arguments otherwise.
    """
    args = parser.parse_args(args=args)

    toggle_io(informational=not args.quiet, debug=args.verbose)

    if args.shell is not None:
        env_var.__VARS__["SHELL"] = args.shell

    if env_var.SHELL not in SHELLS:
        raise KeyError(f"Snape does not support the '{env_var.SHELL}' shell yet")
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

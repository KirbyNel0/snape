import sys

from snape.cli import parser, subcommands
from snape.util import log


def snape_help(
    cmd: list[str]
) -> None:
    """
    Prints out help on snape. Same as ``snape --help``.
    """
    if len(cmd) == 0:
        parser.print_help()
        return

    commands = parser._actions[-1].choices
    for command in cmd:
        if command not in commands:
            print("Subcommand not found:", command, file=sys.stderr)
            continue
        log(commands[command])
        commands[command].print_help()
        print()


# The subcommand parser for ``snape help``.
snape_help_parser = subcommands.add_parser(
    "help",
    description="Print snape's default help",
    help="print this help and exit",
)
snape_help_parser.add_argument(
    "cmd", nargs="*",
    help="can be any snape command to print help for",
    action="store", default=[]
)
snape_help_parser.set_defaults(func=snape_help)

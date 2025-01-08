import argparse
import sys

from snape.cli._parser import parser, subcommands
from snape.util import log

__all__ = [
    "snape_help"
]


def snape_help(
        cmd: list[str]
) -> None:
    """
    Print out help on snape.

    For argument documentation, see ``snape_help_parser``.
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
    description=
    """\
  Print help on snape and its subcommands.

  By default, this command has the same behavior as snape --help.
  By specifying one or multiple subcommands of snape, the help of those subcommands will be printed.\
    """,
    help="print this help and exit",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_help_parser.add_argument(
    "cmd", nargs="*",
    help="can be any snape command to print help for",
    action="store", default=[]
)
snape_help_parser.set_defaults(func=snape_help)

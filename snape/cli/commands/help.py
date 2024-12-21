from snape.cli import parser, subcommands


def snape_help() -> None:
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

import io
import sys

from snape.cli.commands.new import snape_new_parser
from snape.cli.commands import snape_help


def test_basic():
    snape_help([])


def test_commands():
    capture = io.StringIO()
    sys.stdout = capture

    snape_help(["new"])
    help_output = capture.getvalue()

    sys.stdout = sys.__stdout__

    assert help_output.startswith(snape_new_parser.format_help())

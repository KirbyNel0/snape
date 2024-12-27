import snape.config
from snape.cli._parser import parser
from snape.cli.commands import *
from snape.cli.main import main

__all__ = [
    "commands",
    "parser",
    "main"
]

# Mark the names of all snape arguments as illegal venv names
snape.config.FORBIDDEN_ENV_NAMES.extend(parser._option_string_actions.keys())

# Mark the names of all subcommands as illegal venv names
snape.config.FORBIDDEN_ENV_NAMES.extend(parser._actions[-1].choices.keys())

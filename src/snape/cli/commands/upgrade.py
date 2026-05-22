import venv
from typing import Optional

from snape.cli._parser import subcommands
from snape.virtualenv import get_snape_env_path, ensure_virtual_env, get_local_snape_env


def snape_upgrade(env: Optional[str]):
    if env is None:
        snape_env = get_local_snape_env()
    else:
        snape_env = get_snape_env_path(env, False)
    ensure_virtual_env(snape_env)
    print("Upgrading venv at", snape_env)
    venv.main(["--upgrade", str(snape_env)])


snape_upgrade_parser = subcommands.add_parser(
    "upgrade",
    description="Upgrade the environment directory to use this version of Python, assuming Python has been upgraded in-place.",
    help="upgrade the python version used by a venv",
)
snape_upgrade_parser.add_argument(
    "env", nargs="?",
    help="the name of the global environment to upgrade. if omitted, will use a local environment instead.",
    action="store", default=None, metavar="ENV",
)
snape_upgrade_parser.set_defaults(func=snape_upgrade)

from typing import Optional

from snape.cli._parser import subcommands
from snape.virtualenv import get_local_snape_env, get_snape_env_path, ensure_virtual_env, get_env_packages


def snape_freeze(env: Optional[str]) -> list[str]:
    if env is None:
        snape_env = get_local_snape_env()
    else:
        snape_env = get_snape_env_path(env, False)
    ensure_virtual_env(snape_env)
    packages = get_env_packages(snape_env)
    print("# Packages for", snape_env)
    print("\n".join(packages))
    return packages

snape_freeze_parser = subcommands.add_parser(
    "freeze",
    description="Display packages of a virtualenv, just like running 'pip freeze' whilst inside the environment.",
    help="get an environment's package list",
)
snape_freeze_parser.add_argument(
    "env", nargs="?",
    help="the name of the global environment to work on. if omitted, will use a local environment instead.",
    action="store", default=None, metavar="ENV"
)
snape_freeze_parser.set_defaults(func=snape_freeze)

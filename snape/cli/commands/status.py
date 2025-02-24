import argparse
import json
from pathlib import Path
from typing import Any

from snape import env_var
from snape.cli._parser import subcommands
from snape.util import log
from snape.virtualenv import get_global_snape_envs, get_local_snape_envs, get_snape_env_name

__all__ = [
    "snape_status"
]


def snape_status(
        raw: bool
) -> dict[str, Any]:
    """
    Outputs information on the current venv and snape status.

    For argument documentation, see ``snape_status_parser``.
    """
    # Assemble information
    python_venv = env_var.VIRTUAL_ENV

    snape_current_env = env_var.VIRTUAL_ENV.split("/")[-1] if env_var.VIRTUAL_ENV else None
    if snape_current_env and snape_current_env != env_var.SNAPE_VENV and env_var.SNAPE_ROOT_PATH not in Path(python_venv).parents:
        # Neither local nor global snape managed environment
        snape_current_env = None

    snape_global_root = env_var.SNAPE_ROOT_PATH
    snape_global_envs = get_global_snape_envs()
    snape_local_envs = get_local_snape_envs()
    snape_local_name = env_var.SNAPE_VENV

    # All variables constructed locally should be printed out.
    # All functional objects must be removed from the output.
    status = locals()
    status.pop("raw")
    log(json.dumps(status, indent=4, default=str))

    # If requested: Output the collected information as json.
    if raw:
        # Print everything
        print(json.dumps(status, indent=4, default=str))
        return status

    snape_global_envs_str = []
    for env in snape_global_envs:
        if str(env) == python_venv:
            snape_global_envs_str.append(f"    * \033[32m{get_snape_env_name(env)}\033[0m")
        else:
            snape_global_envs_str.append(f"    * {get_snape_env_name(env)}")

    snape_local_envs_str = []
    for env in snape_local_envs:
        if str(env) == python_venv:
            snape_local_envs_str.append(f"    * \033[32m{env.parent}\033[0m")
        else:
            snape_local_envs_str.append(f"    * {env.parent}")

    print("Python venv:")
    print("  Current:       ", python_venv)
    print("  Snape name:    ", get_snape_env_name(python_venv) if python_venv is not None else None)

    if len(snape_local_envs) != 0:
        print()
        print("Local snape environments:")
        print("\n".join(snape_local_envs_str))

    if len(snape_global_envs) != 0:
        print()
        print("Global snape environments:")
        print("  Snape root:   ", snape_global_root)
        print("  Available environments:")
        print("\n".join(snape_global_envs_str))
    return status


snape_status_parser = subcommands.add_parser(
    "status",
    description=
    """\
  List information on the current status of all virtual environments known to snape.\
    """,
    help="list information on the current status of snape",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
snape_status_parser.add_argument(
    "-r", "--raw",
    help="print all information as json",
    action="store_true", default=False, dest="raw"
)
snape_status_parser.set_defaults(func=snape_status)

import argparse
import json
from pathlib import Path
from typing import Any

from snape import env_var
from snape.cli._parser import subcommands
from snape.util import absolute_path
from snape.util import log
from snape.virtualenv import get_global_snape_venvs, is_venv, get_snape_venv_name

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
    local_venv = absolute_path(env_var.SNAPE_VENV)

    python_venv = env_var.VIRTUAL_ENV
    snape_env = env_var.VIRTUAL_ENV.split("/")[-1] if env_var.VIRTUAL_ENV else None
    if snape_env and snape_env != env_var.SNAPE_VENV and env_var.SNAPE_ROOT_PATH not in Path(python_venv).parents:
        # Neither local nor global snape managed environment
        snape_env = None
    snape_dir = env_var.SNAPE_ROOT_PATH
    snape_envs = get_global_snape_venvs()
    local_active = False if python_venv is None else absolute_path(python_venv) == local_venv
    local_exists = bool(local_venv.is_dir() and is_venv(local_venv))
    local_default = env_var.SNAPE_VENV

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

    snape_envs_str = []
    for env in snape_envs:
        env_prefix = "\033[32m*\033[0m" if str(env) == python_venv else "*"
        snape_envs_str.append(f"    {env_prefix} {get_snape_venv_name(env)}")

    if not local_exists:
        local_status = " "
    elif local_active:
        local_status = "\033[32m*\033[0m"
    else:
        local_status = "*"

    local_string = f"    {local_status} {local_venv}"

    print(
f"""\
Python venv:
  Current:       {python_venv}
  Snape name:    {get_snape_venv_name(python_venv) if python_venv is not None else None}
"""
    )

    if local_exists:
        print(
f"""\
Local snape environment:
{local_string}
"""
              )

    if len(snape_envs) != 0:
        print(
f"""\
Global snape environments:
  Snape root:    {snape_dir}
  Available environments:
{'\n'.join(snape_envs_str)}\
"""
              )
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

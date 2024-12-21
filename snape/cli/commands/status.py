import json
from pathlib import Path

from snape import env_var
from snape.util import log
from snape.util import absolute_path
from snape.cli import subcommands
from snape.virtualenv import get_global_snape_venvs, is_venv


def snape_status(
    raw: bool
) -> None:
    """
    Outputs information on the current venv and snape status.

    For argument documentation, see ``snape_status_parser``.
    """

    local_venv = absolute_path(env_var.SNAPE_LOCAL_VENV)

    # Construct information
    python_venv = env_var.VIRTUAL_ENV
    snape_env = env_var.VIRTUAL_ENV.split("/")[-1] if env_var.VIRTUAL_ENV else None
    if snape_env and snape_env != env_var.SNAPE_LOCAL_VENV and env_var.SNAPE_ROOT_PATH not in Path(python_venv).parents:
        # Neither local nor global snape managed environment
        snape_env = None
    snape_dir = env_var.SNAPE_ROOT_PATH
    snape_envs = get_global_snape_venvs()
    snape_default = env_var.SNAPE_VENV
    local_active = False if python_venv is None else absolute_path(python_venv) == local_venv
    local_exists = bool(local_venv.is_dir() and is_venv(local_venv))
    local_default = env_var.SNAPE_LOCAL_VENV

    # All variables constructed locally should be printed out
    # All functional objects must be removed from the output.
    status = locals()
    status.pop("raw")
    log(json.dumps(status, indent=4, default=str))

    # If requested: Output the collected information as json.
    if raw:
        # Print everything
        print(json.dumps(status, indent=4, default=str))
        return

    snape_envs_str = []
    for env in snape_envs:
        prefix = "  \033[32m*\033[0m" if env == snape_env else "  *"
        suffix = "(default)" if env == snape_default else ""
        snape_envs_str.append(f"{prefix} {env.name} {suffix}")

    local_active_status = "\033[32m*\033[0m active" if local_active else "inactive"
    local_exists_status = "exists" if local_exists else "no venv found"

    indent = "\n\t"
    print(
        f"""\
Python venv:
    Current:       {python_venv}

Global snape environments:
    Snape root:    {snape_dir}
    Available environments:
        {indent.join(snape_envs_str)}

Local snape environments:
    Name of local venvs: {local_default}
    Current directory:   {local_exists_status}
    Status:              {local_active_status}"""
    )


# The subcommand parser for ``snape status``
snape_status_parser = subcommands.add_parser(
    "status",
    description="List information on the current snape status.",
    help="list information on the current snape status"
)
# Whether to print out as json
snape_status_parser.add_argument(
    "-r", "--raw",
    help="print all information as json",
    action="store_true", default=False, dest="raw"
)
snape_status_parser.set_defaults(func=snape_status)
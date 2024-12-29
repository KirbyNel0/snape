import json
from typing import Any

from snape import env_var
from snape.cli._parser import subcommands
from snape.util import log, absolute_path
from snape.util.path import get_dir_size
from snape.virtualenv import get_snape_venv_path, get_venv_packages, ensure_venv, is_active_venv, is_venv
from snape.virtualenv.internal import is_global_snape_venv_path


def snape_env(
        env: str | None,
        here: bool,
        raw: bool,
        information: list[str],
):
    if raw:  # Assemble all information in an object
        raw_info = {}

        def add_info(key: str | None, _: str | None, value: Any):
            raw_info[key] = value
    else:
        def add_info(_: str | None, name: str | None, value: Any):
            if isinstance(value, list):
                print(f"{name}:")
                for val in value:
                    print("\t", val)
            elif isinstance(value, bool):
                print(f"{name}:".ljust(12), "Yes" if value else "No")
            else:
                print(f"{name}:".ljust(12), value)

    # Path information
    if env is None and not here:
        if env_var.VIRTUAL_ENV is not None:
            venv_path = absolute_path(env_var.VIRTUAL_ENV)
        else:
            venv_path = None
        if venv_path is None or not is_venv(venv_path):
            raise ValueError("No environment specified and no active environment found")
    else:
        venv_path = get_snape_venv_path(env, here)

    venv = ensure_venv(venv_path)
    add_info("name", "Name", venv.name)

    # Global information
    is_global = is_global_snape_venv_path(venv)
    if raw:
        add_info("global", None, is_global)
    else:
        add_info(None, "Placement", "global" if is_global else "local")

    # Path
    add_info("path", "Path", venv)

    # Active information
    venv_active = is_active_venv(venv)
    add_info("active", "Active", venv_active)

    if env_var.SNAPE_VENV == venv.name and is_global:
        activate_command = "snape"
    else:
        activate_command = venv.name if is_global else "--here"
        activate_command = f"snape {activate_command}"
    add_info("activate_command", "Command", activate_command)

    if "size" in information:  # Information
        log("Collecting size")
        size = get_dir_size(venv) >> 10  # Bytes returned, kilobytes calculated
        add_info("size", "Size (MB)", round(size / 1024, 3))

    if "packages" in information:  # Packages
        packages = get_venv_packages(venv)
        add_info("packages", "Installed packages", packages)

    if raw:  # Output raw
        print(json.dumps(raw_info, indent=4, default=str))


snape_list_parser = subcommands.add_parser(
    "env",
    description="List all information on a single environment",
    help="list information on a snape environment"
)
snape_list_parser.add_argument(
    "env", nargs="?",
    help="the name of the global environment to list information on. "
         "can also be --here to list information on a local environment. "
         "if not specified, lists information on an active environment.",
    action="store", default=None
)
snape_list_parser.add_argument(
    "-l", "--local", "--here",
    help="list information on a local environment",
    action="store_true", default=False, dest="here"
)
snape_list_parser.add_argument(
    "-r", "--raw",
    help="format all output as a single json object",
    action="store_true", default=False, dest="raw"
)
snape_list_parser.set_defaults(func=snape_env)

snape_list_parser_info = snape_list_parser.add_argument_group("information to list")
snape_list_parser_info.add_argument(
    "-a", "--all",
    help="list all information. same as -p.",
    action="store_const", const=["packages", "size"], default=[], dest="information"
)
snape_list_parser_info.add_argument(
    "-p", "--packages",
    help="list installed packages of that environment with version information",
    action="append_const", const="packages", default=None, dest="information"
)
snape_list_parser_info.add_argument(
    "-s", "--size",
    help="print out the size of the environment",
    action="append_const", const="size", default=None, dest="information"
)

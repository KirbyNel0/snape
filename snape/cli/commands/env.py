import argparse
import json
from typing import Any

from snape import env_var
from snape.cli._parser import subcommands
from snape.util import log, absolute_path
from snape.util.path import get_dir_size
from snape.virtualenv import get_snape_env_path, get_env_packages, ensure_virtual_env, is_active_virtual_env, is_virtual_env
from snape.virtualenv.internal import is_global_snape_env_path, get_snape_env_name

__all__ = [
    "snape_env"
]


def snape_env(
        env: str | None,
        here: bool,
        raw: bool,
        information: list[str],
):
    """
    Get information on the current virtual env or any snape environment.

    For argument documentation, see ``snape_env_parser``.
    """
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
            env_path = absolute_path(env_var.VIRTUAL_ENV)
        else:
            env_path = None
        if env_path is None or not is_virtual_env(env_path):
            raise ValueError("No environment specified and no active environment found")
    else:
        env_path = get_snape_env_path(env, here)

    virtual_env = ensure_virtual_env(env_path)
    add_info("name", "Name", get_snape_env_name(virtual_env))

    # Global information
    is_global = is_global_snape_env_path(virtual_env)
    if raw:
        add_info("global", None, is_global)
    else:
        add_info(None, "Placement", "global" if is_global else "local")

    # Path
    add_info("path", "Path", virtual_env)

    # Active information
    env_active = is_active_virtual_env(virtual_env)
    add_info("active", "Active", env_active)

    if not is_global:
        activate_command = "snape"
    else:
        activate_command = get_snape_env_name(virtual_env) if is_global else "--here"
        activate_command = f"snape {activate_command}"
    add_info("activate_command", "Command", activate_command)

    if "size" in information:  # Information
        log("Collecting size")
        size = get_dir_size(virtual_env) >> 10  # Bytes returned, kilobytes calculated
        add_info("size", "Size (MB)", round(size / 1024, 3))

    if "packages" in information:  # Packages
        packages = get_env_packages(virtual_env)
        add_info("packages", "Installed packages", packages)

    if raw:  # Output raw
        print(json.dumps(raw_info, indent=4, default=str))


snape_list_parser = subcommands.add_parser(
    "env",
    description=
    """\
  List information on a single environment.

  By default, list information on the environment which is currently active.
  If a snape-managed environment is specified, list information on that environment (see env parameter).\
    """,
    help="list information on a snape environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
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

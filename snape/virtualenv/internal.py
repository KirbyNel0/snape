import os
import shutil
import venv as python_venv
from pathlib import Path
from typing import cast

from snape import env_var
from snape.util import absolute_path, ask, log, info
from snape.virtualenv import is_venv, is_active_venv
from snape.config import FORBIDDEN_ENV_NAMES
from snape.annotations import VirtualEnv


__all__ = [
    "is_global_snape_venv",
    "get_snape_venv_path",
    "create_new_snape_venv",
    "delete_snape_venv",
    "get_global_snape_venvs"
]


def is_global_snape_venv_path(env: Path) -> bool:
    """
    Checks whether the specified environment path is located at the global snape venv directory.

    :param env: The environment to check.
    :return: Whether ``env`` is a child directory of ``SNAPE_DIR``.
    """
    return absolute_path(env.parent) == env_var.SNAPE_ROOT_PATH and env.is_dir()


def is_global_snape_venv(env: VirtualEnv | Path) -> bool:
    """
    Checks whether the specified environment path is located at the global snape venv directory and is a valid venv.

    :param env: The environment to check.
    :return: Whether ``env`` is a child directory of ``SNAPE_DIR`` and is a virtual environment (see ``is_venv``).
    """
    return is_global_snape_venv_path(env) and is_venv(env)


def get_snape_venv_path(name: str | None, local: bool) -> Path:
    """
    Creates an absolute path pointing to a local or global snape environment with the specified name.

    :param name: The name of the new environment. This will be ignored for local environments and may not be ``None``
        for global environments. It may not be an illegal environment name.
    :param local: Whether the environment should be available globally or locally.
    :return: The absolute path to the new environment.
    :exception NameError: Raised if an illegal environment name was specified for a global environment.
    :exception ValueError: Raised if ``local=False`` and ``name=None``.
    """
    if name in FORBIDDEN_ENV_NAMES:
        raise NameError("Illegal snape venv name: ", name)

    if local:
        return absolute_path(Path.cwd() / env_var.SNAPE_LOCAL_VENV)

    if name is None or len(name) == 0:
        raise ValueError("No name provided for global snape environment")

    return absolute_path(env_var.SNAPE_ROOT_PATH / name)


def create_new_snape_venv(env: Path, overwrite: bool | None, autoupdate: bool) -> VirtualEnv | None:
    """
    Creates a new snape environment at the specified path. If the directory exists and is not a venv, an error is
    raised.

    :param env: The path of the new environment.
    :param overwrite: Whether to overwrite existing environments. If ``None``, the user is prompted whether to
        overwrite existing environments.
    :param autoupdate: Whether to automatically update the environment's ``pip`` after creation.
    :return: The path to the new virtual environment. If an existing environment has not been overwritten, ``None`` is
        returned
    :exception NameError: Raised if the environment has an illegal name.
    :exception IsADirectoryError: Raised if the specified path exists and is not a venv which could be overwritten.
    :exception NotADirectoryError: Raised if the specified path exists and points to a file.
    """
    if env.name in FORBIDDEN_ENV_NAMES:
        raise NameError("Illegal snape venv name: " + env.name)

    if env.is_file():
        raise NotADirectoryError(f"{env} exists and is neither a directory nor a virtual environment")

    if env.is_dir():
        if not is_venv(env):
            raise IsADirectoryError(f"Directory {env} exists and is not an existing environment which could be overwritten")

        if overwrite is None:
            if not ask(f"Environment '{env.name}' does already exist. Overwrite?", False):
                return None
            overwrite = True

    locality = "global" if is_global_snape_venv(env) else "local"
    info(f"Creating {locality} snape environment:", env.name)
    log("Creating virtual environment at", env)
    python_venv.create(env, with_pip=True, clear=overwrite, upgrade_deps=autoupdate)
    return cast(VirtualEnv, absolute_path(env))


def delete_snape_venv(env: VirtualEnv, no_ask: bool, ignore_active: bool) -> None:
    """
    Deletes a snape environment. If it is attempted to delete an active environment, an error is raised.

    :param env: The virtual environment to delete.
    :param no_ask: If ``True``, the user will not be prompted before deleting the environment.
    :param ignore_active: If ``True``, it will be ignored if the environment to delete is active.
    :exception RuntimeError: Raised if the environment is active and ``ignore_active`` is ``False``.
    :exception SystemError: Raised if the environment could not be deleted.
    """
    if not ignore_active and is_active_venv(env):
        raise RuntimeError(f"Environment {env.name} is currently active. Deactivate it before deletion.")

    locality = "global" if is_global_snape_venv(env) else "local"
    if no_ask or ask(f"Are you sure you want to delete the {locality} environment '{env.name}'?", False):
        shutil.rmtree(env)

    if not env.is_dir():
        raise SystemError(f"Could not delete virtual environment: {env}")

    info(f"Deleted {locality} snape environment", env.name)


def get_global_snape_venvs() -> list[VirtualEnv]:
    """
    Creates a list of all virtual environment existing in snape's global scope.

    :return: A list of absolute paths to all global snape environments.
    """
    return [
        cast(VirtualEnv, env_var.SNAPE_ROOT_PATH / snape_venv)
        for snape_venv in os.listdir(env_var.SNAPE_ROOT_PATH)
        if is_venv(env_var.SNAPE_ROOT_PATH / snape_venv)
    ]

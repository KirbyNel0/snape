import os
import shutil
import venv as python_venv
from pathlib import Path
from typing import cast, Generator

from snape import env_var
from snape.annotations import VirtualEnv, SnapeCancel
from snape.config import FORBIDDEN_ENV_NAMES
from snape.util import absolute_path, ask, log, info
from snape.virtualenv.util import is_virtual_env, is_active_virtual_env

__all__ = [
    "is_global_snape_env_path",
    "is_global_snape_env",
    "get_snape_env_path",
    "get_snape_env_name",
    "create_new_snape_env",
    "delete_snape_env",
    "get_local_snape_env",
    "get_local_snape_envs",
    "iter_local_snape_envs",
    "get_global_snape_envs"
]


def is_global_snape_env_path(env: Path, check_exists: bool = True) -> bool:
    """
    Checks whether the specified environment path is located at the global snape venv directory.

    :param env: The environment to check.
    :param check_exists: If ``True``, this method will only return ``True`` if the specified path exists as a directory.
        Otherwise, the path contents will only be compared.
    :return: Whether ``env`` is a child directory of ``SNAPE_DIR``.
    """
    return env_var.SNAPE_ROOT_PATH in absolute_path(env).parents and ((not check_exists) or env.is_dir())


def is_global_snape_env(env: VirtualEnv | Path) -> bool:
    """
    Checks whether the specified environment path is located at the global snape venv directory and is a valid venv.

    :param env: The environment to check.
    :return: Whether ``env`` is a child directory of ``SNAPE_DIR`` and is a virtual environment (see ``is_virtual_env``).
    """
    return is_global_snape_env_path(env) and is_virtual_env(env)


def get_snape_env_path(name: str | None, local: bool, warn_argument_conflicts: bool = True) -> Path:
    """
    Creates an absolute path pointing to a local or global snape environment with the specified name.

    :param name: The name of the new environment. This will be ignored for local environments and may not be ``None``
        for global environments. It may not be an illegal environment name.
    :param local: Whether the environment should be available globally or locally.
    :param warn_argument_conflicts: Raise a ``RuntimeError`` if ``local=False`` and ``name=None``
    :return: The absolute path to the new environment.
    :exception NameError: Raised if an illegal environment name was specified for a global environment.
    :exception ValueError: Raised if no name was provided when required.
    """
    if name in FORBIDDEN_ENV_NAMES:
        raise NameError("Illegal snape venv name: " + str(name))

    if warn_argument_conflicts:
        if name is None and not local:
            raise RuntimeError("No environment name provided for global snape environment")

    if local:
        return absolute_path(Path.cwd() / env_var.SNAPE_VENV)

    if not name:
        raise ValueError("No name provided for global snape environment")

    return absolute_path(env_var.SNAPE_ROOT_PATH / name)


def get_snape_env_name(_env: str | Path | VirtualEnv) -> str | None:
    """
    Evaluates the snape-recognized name of a virtual environment.
    The name is all path components from snape's root directory separated by slashes.
    For local environments, returns None if not managed by snape or the default local venv name.
    
    :param _env: The environment whose name should be evaluated
    :return: `None` if the path points to an environment not managed by snape, its name otherwise.
    """
    if _env is None:
        return None

    _env = absolute_path(_env)

    if is_global_snape_env_path(_env, check_exists=False):
        global_env = _env
        result = []

        while global_env.parent != env_var.SNAPE_ROOT_PATH:
            result.append(global_env.name)
            global_env = global_env.parent

        if global_env.parent is None:
            return None

        result.append(global_env.name)
        return "/".join(reversed(result))

    return _env.name if _env.name == env_var.SNAPE_VENV else None


def create_new_snape_env(env: Path, overwrite: bool | None, autoupdate: bool, prompt: str | None = None, env_name: str = None) -> VirtualEnv | None:
    """
    Creates a new snape environment at the specified path. If the directory exists and is not a venv, an error is
    raised.

    :param env: The path of the new environment.
    :param overwrite: Whether to overwrite existing environments. If ``None``, the user is prompted whether to
        overwrite existing environments.
    :param autoupdate: Whether to automatically update the environment's ``pip`` after creation.
    :param prompt: The prompt string to display while the environment is active. If ``None``, defaults to ``env.name``.
    :param env_name: The name to display when creating the environment. Defaults to ``get_snape_env_name(env)``.
    :return: The path to the new virtual environment. If an existing environment has not been overwritten, ``None`` is
        returned
    :exception NameError: Raised if the environment has an illegal name.
    :exception IsADirectoryError: Raised if the specified path exists and is not a venv which could be overwritten.
    :exception NotADirectoryError: Raised if the specified path exists and points to a file.
    """
    env_name = env_name or get_snape_env_name(env)

    if env.name in FORBIDDEN_ENV_NAMES:
        raise NameError("Illegal snape venv name: " + env.name)

    if env.is_file():
        raise NotADirectoryError(f"{env} exists and is neither a directory nor a virtual environment")

    if env.is_dir():
        if not is_virtual_env(env):
            raise IsADirectoryError(
                f"Directory {env} exists and is not an existing environment which could be overwritten"
            )

        if overwrite is None:
            if not ask(f"Environment '{env_name}' does already exist. Overwrite?", False):
                return None
            overwrite = True

    locality = "global" if is_global_snape_env_path(env, check_exists=False) else "local"
    info(f"Creating {locality} snape environment:", env_name)
    log("Creating virtual environment at", env)
    python_venv.create(env, with_pip=True, clear=overwrite, upgrade_deps=autoupdate, prompt=prompt)
    with open(env / ".gitignore", "w") as gitignore:
        print("*", file=gitignore)
    return cast(VirtualEnv, absolute_path(env))


def delete_snape_env(env: VirtualEnv, do_ask: bool, ignore_active: bool) -> None:
    """
    Deletes a snape environment. If it is attempted to delete an active environment, an error is raised.

    :param env: The virtual environment to delete.
    :param do_ask: If ``False``, the user will not be prompted before deleting the environment.
    :param ignore_active: If ``True``, it will be ignored if the environment to delete is active.
    :exception RuntimeError: Raised if the environment is active and ``ignore_active`` is ``False``.
    :exception SystemError: Raised if the environment could not be deleted.
    """
    env_name = get_snape_env_name(env)

    if not ignore_active and is_active_virtual_env(env):
        raise RuntimeError(f"Environment {env_name} is currently active. Deactivate it before deletion.")

    locality = "global" if is_global_snape_env(env) else "local"
    if (not do_ask) or ask(f"Are you sure you want to delete the {locality} environment '{env_name}'?", False):
        shutil.rmtree(env)
    else:
        raise SnapeCancel()

    if env.is_dir():
        raise SystemError(f"Could not delete virtual environment: {env}")

    info(f"Deleted {locality} snape environment", env_name)


def get_local_snape_envs(cwd: Path | None = None) -> list[VirtualEnv]:
    """
    Creates a list of all environments having the name ``env_var.SNAPE_VENV`` located inside parent directories of
    ``cwd``. The first of these environments would be activated when calling the ``snape`` function.

    :param cwd: If ``None``, evaluates from the current working directory, from ``cwd`` otherwise.
    :return: All local environments located in parent directories of ``cwd``.
    """
    return list(iter_local_snape_envs(cwd))


def get_local_snape_env(cwd: Path | None = None) -> VirtualEnv | None:
    """
    Evaluates the local snape environment which would be activated when calling ``snape``.
    Almost the same as ``get_local_snape_envs()[0]``.

    :param cwd: If ``None``, evaluates from the current working directory, from ``cwd`` otherwise.
    :return: The first local environment to be found inside ``cwd`` or any parent directory.
    """
    generator = iter_local_snape_envs(cwd)
    result = next(generator)
    del generator
    return result


def iter_local_snape_envs(cwd: Path | None = None) -> Generator[VirtualEnv, None, None]:
    """
    Iterates all parent directories of ``cwd`` (including ``cwd`` itself) and checks whether a snape-managed venv
    exists inside of that directory. If so, the path to that environment is yielded.

    :param cwd: If ``None``, evaluates from the current working directory, from ``cwd`` otherwise.
    """
    local_env_dir = cwd or Path.cwd()

    while local_env_dir.parent != local_env_dir:
        local_env = local_env_dir / env_var.SNAPE_VENV
        if is_virtual_env(local_env):
            yield cast(VirtualEnv, local_env)
        local_env_dir = local_env_dir.parent


def get_global_snape_envs() -> list[VirtualEnv]:
    """
    Creates a list of all virtual environment existing in snape's global scope.

    :return: A list of absolute paths to all global snape environments.
    """
    return _get_environments(env_var.SNAPE_ROOT_PATH)


def _get_environments(root: Path) -> list[VirtualEnv]:
    """
    Lists all environments found inside `root` and its nested directories (recursively).

    :param root: The directory to scan for snape venvs
    :return: A list of all found environments in `root` and its nested directories as
        absolute paths.
    """
    result = []

    if not root.is_dir():
        return []

    for env in os.listdir(root):
        full_path = root / env
        if is_virtual_env(full_path):
            result.append(cast(VirtualEnv, full_path))
        elif full_path.is_dir():
            result.extend(_get_environments(full_path))
    return result


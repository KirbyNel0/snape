import subprocess
from pathlib import Path
from typing import cast

from snape import env_var
from snape.annotations import VirtualEnv
from snape.config import SHELLS
from snape.util import absolute_path, log, info

__all__ = [
    "is_virtual_env",
    "is_active_virtual_env",
    "ensure_virtual_env",
    "get_env_packages",
    "install_packages",
    "install_requirements"
]


def is_virtual_env(env: Path) -> bool:
    """
    Checks whether the given path points to a python virtual environment.
    This function is shell dependant and performs its checks depending on the global ``SHELL`` variable.

    :param env: The path to check.
    :return: Whether the specified path points to a directory which contains an activation file and a python binary.
    """
    return env.is_dir() and (env / SHELLS[env_var.SHELL]["activate_file"]).is_file() and (env / "bin/python").is_file()


def is_active_virtual_env(env: VirtualEnv) -> bool:
    """
    Checks whether the specified environment is the currently active python environment.

    :param env: The path to check.
    :return: Whether the specified environment is currently active.
    """
    return env_var.VIRTUAL_ENV is not None and absolute_path(env_var.VIRTUAL_ENV) == absolute_path(env)


def ensure_virtual_env(env: Path) -> VirtualEnv:
    """
    Ensures the specified path is a virtual environment and returns it as an absolute path.

    :param env: A path to the environment to verify.
    :return: The absolute path to the specified environment, if it is one.
    :exception NotADirectoryError: Raised if the path is not a directory.
    :exception SystemError: Raised if the path is not a venv.
    """
    if not env.is_dir():
        raise NotADirectoryError(f"Virtual environment directory not found: {env}")
    if not is_virtual_env(env):
        raise SystemError(f"Not a virtual environment: {env}")
    return cast(VirtualEnv, absolute_path(env))


# Could be used: pip --require-virtualenv [commands...]

def get_env_packages(env: VirtualEnv) -> list[str]:
    """
    Uses the ``pip`` command to list all installed packages of a virtual environment and converts it to a python list.

    Error output of ``pip`` is logged to console in debug mode.

    :param env: The environment whose ``pip`` to use. This will list all packages from that environment.
    :return: A list of all packages installed in the specified virtual environment.
        A common output format is ``package==version``.
    """
    try:
        log("Reading package list from", env)
        process = subprocess.run([env / "bin/pip", "freeze"], capture_output=True)
    except subprocess.CalledProcessError as e:
        log("Failed to fetch package list:", e)
        raise RuntimeError(f"Cannot read package list from {env}")

    if process.returncode != 0:
        if process.stderr:
            log(process.stderr.decode())
        raise RuntimeError(
            f"Cannot read package list, command 'pip freeze' terminated with exit code {process.returncode}"
        )

    # Create package list
    packages: list[str] = list(filter(lambda x: x, process.stdout.decode().split("\n")))
    log("Packages:", ", ".join(packages))

    return packages


def install_packages(env: VirtualEnv, packages: list[str], no_output: bool) -> bool:
    """
    Installs all mentioned packages (with given versions) into the specified virtual environment.

    This function calls ``pip install *packages`` as subprocess. All ``pip`` output is logged in debug mode.

    :param env: The environment to install packages into.
    :param packages: The list of packages (with given versions) to install (see also ``get_venv_packages``).
    :param no_output: If ``True``, all output from ``pip`` will be hidden from console.
    :return: Whether installation succeeded for all packages.
    """
    if len(packages) == 0:
        log("No packages to install")
        return True

    process = subprocess.run([env / "bin/pip", "install"] + packages, capture_output=no_output)

    # Output stdout
    if process.stdout:
        log(process.stdout.decode())
    # Output errors
    if process.returncode != 0:
        if process.stderr:
            log("ERRORS:", process.stderr.decode())
        return False
    return True


def install_requirements(env: VirtualEnv, requirements_file: Path, no_output: bool) -> bool:
    """
    Installs all packages from a requirements file into the specified virtual environment.

    This function calls ``pip install -r requirements_file`` as subprocess. All ``pip`` output is logged in debug mode.

    :param env: The environment to install packages into.
    :param requirements_file: The file to read the package list from.
    :param no_output: If ``True``, all output from ``pip`` will be hidden from console.
    :return: Whether installation succeeded for all packages.
    """
    info("Installing requirements from", requirements_file)
    process = subprocess.run(
        [env / "bin/pip", "install", "-r", str(requirements_file)],
        capture_output=no_output
    )
    if process.stdout:
        log(process.stdout.decode())
    if process.stderr:
        log("ERRORS:", process.stderr.decode())
    return process.returncode == 0

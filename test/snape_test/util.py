import os
from pathlib import Path

import snape


def create_dummy_venv(__path: os.PathLike[str]):
    path = Path(__path)

    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        (path / "bin").mkdir(exist_ok=True)

        (path / "bin/pip3").touch(exist_ok=True)
        (path / "bin/python3").touch(exist_ok=True)

        (path / "bin/pip").touch(exist_ok=True)
        (path / "bin/python").touch(exist_ok=True)

        (path / snape.config.SHELLS[snape.env_var.SHELL]["activate_file"]).touch()


def create_dummy_broken_venv(__path: os.PathLike[str]):
    path = Path(__path)

    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        (path / "bin").mkdir(exist_ok=True)

        (path / "bin/_pip3").touch(exist_ok=True)
        (path / "bin/_python3").touch(exist_ok=True)

        (path / "bin/_pip").touch(exist_ok=True)
        (path / "bin/_python").touch(exist_ok=True)

        (path / snape.config.SHELLS[snape.env_var.SHELL]["activate_file"]).mkdir(parents=True, exist_ok=True)

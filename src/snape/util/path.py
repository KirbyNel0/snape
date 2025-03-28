import os
from pathlib import Path

__all__ = [
    "absolute_path",
    "get_dir_size"
]


def absolute_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve().absolute()


def get_dir_size(path: str | os.PathLike[str]) -> int:
    return sum(os.path.getsize(f) for f in Path(path).glob('**/*') if f.is_file())

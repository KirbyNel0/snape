from pathlib import Path


__all__ = [
    "absolute_path"
]


def absolute_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve().absolute()

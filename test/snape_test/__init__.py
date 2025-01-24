import os
import sys
from pathlib import Path
from typing import Final


__all__ = [
    "cli",

    "SNAPE_REPO",
    "SNAPE_TEST_REPO",

    "TEST_DIR",
    "GLOBAL_ENV_ROOT",
    "WORKING_DIR",
    "OTHER_FILES"
]


SNAPE_REPO: Final[Path] = Path(__file__).absolute().resolve().parent.parent.parent
SNAPE_TEST_REPO: Final[Path] = SNAPE_REPO / "test"

TEST_DIR: Final[Path] = SNAPE_TEST_REPO / "out"

GLOBAL_ENV_ROOT: Final[Path] = TEST_DIR / "snape-global"
WORKING_DIR: Final[Path] = TEST_DIR / "cwd"
OTHER_FILES: Final[Path] = TEST_DIR / "other"


def _setup_snape():
    sys.path.append(str(SNAPE_REPO))
    sys.path.append(str(SNAPE_TEST_REPO))

    GLOBAL_ENV_ROOT.mkdir(parents=True, exist_ok=True)
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    OTHER_FILES.mkdir(parents=True, exist_ok=True)

    os.chdir(WORKING_DIR)

    import snape
    snape.env_var.__VARS__["SNAPE_ROOT"] = str(GLOBAL_ENV_ROOT)
    snape.env_var.SNAPE_ROOT_PATH = GLOBAL_ENV_ROOT


_setup_snape()

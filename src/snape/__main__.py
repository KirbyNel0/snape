#!/bin/python3

if __name__ != "__main__":
    raise ImportError("snape/__main__.py may only be used as main script")

import sys
from pathlib import Path

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    print("At least python 3.7 is required to run snape")
    exit(2)

try:
    import snape
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent.expanduser().resolve().absolute()))

import traceback

from snape.util import log
from snape.annotations import SnapeCancel
from snape.cli import main

try:
    main()
except SnapeCancel:
    exit(0)
except Exception as e:
    log("\n".join(traceback.format_exception(e)))
    print(e, file=sys.stderr)
    exit(1)

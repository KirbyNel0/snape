if __name__ != "__main__":
    raise ImportError("snape/run.py may only be used as main script")

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.expanduser().resolve().absolute()))

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

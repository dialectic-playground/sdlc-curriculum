#!/usr/bin/env python3
"""Launch a reference implementation by tool name: ``run.py dp-cat [ARG]...``.

The black-box runner uses this (``run-tests.py --reference``) to generate and verify every
expected-output fixture. Tool ``dp-foo-bar`` maps to module ``dpref.foo_bar``.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dpref import common  # noqa: E402


def launch() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].startswith("dp-"):
        sys.stderr.write("usage: run.py dp-<tool> [ARG]...\n")
        sys.exit(2)
    tool = sys.argv.pop(1)
    module = importlib.import_module("dpref." + tool[3:].replace("-", "_"))
    common.run(module.main, tool)


if __name__ == "__main__":
    launch()

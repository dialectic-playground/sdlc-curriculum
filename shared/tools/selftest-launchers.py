#!/usr/bin/env python3
"""Self-test: script launchers (`#!` lines) work as tools on every OS, Windows included.

Builds a temporary bin directory whose `dp-hello` is a Python launcher script (delegating to
the reference model) and runs Project 00's public and hidden suites against it with
`run-tests.py --bin-dir`. It is run twice: with `#!/usr/bin/env python` (when `python` is on
PATH) and with an absolute interpreter path.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "shared" / "tools" / "run-tests.py"
SUITES = [
    ROOT / "projects" / "00-hello-world" / "tests" / name
    for name in ("public", "private")
]
LAUNCHER_BODY = """
import runpy, sys
sys.argv = ["run.py", "dp-hello", *sys.argv[1:]]
runpy.run_path({reference!r}, run_name="__main__")
"""


def run_with(shebang: str) -> int:
    with tempfile.TemporaryDirectory(prefix="dp-launchers-") as bin_dir:
        launcher = Path(bin_dir) / "dp-hello"
        launcher.write_text(
            shebang
            + "\n"
            + LAUNCHER_BODY.format(reference=str(ROOT / "reference" / "run.py")),
            encoding="utf-8",
            newline="\n",
        )
        launcher.chmod(
            launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        print(f"== launcher: {shebang}", flush=True)
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "-q",
                "--bin-dir",
                bin_dir,
                *map(str, SUITES),
            ],
            check=False,
        )
        return completed.returncode


def main() -> int:
    forms = [f"#!{sys.executable}"]
    if shutil.which("python"):
        forms.insert(0, "#!/usr/bin/env python")
    else:
        print("note: `python` is not on PATH; skipping the #!/usr/bin/env form")
    status = 0
    for shebang in forms:
        if os.name != "nt" and " " in shebang:
            print(f"note: skipping {shebang!r} (POSIX shebangs cannot contain spaces)")
            continue
        status |= run_with(shebang)
    print("launchers: OK" if status == 0 else "launchers: FAILED")
    return status


if __name__ == "__main__":
    sys.exit(main())

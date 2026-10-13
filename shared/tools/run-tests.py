#!/usr/bin/env python3
"""Black-box acceptance test runner for the SDLC curriculum.

Runs every test in one or more suite directories (``tests/public``, ``tests/private``) against a
built tool and compares stdout, stderr, and exit status byte-for-byte with the expected outputs.
Standard library only; behaves identically on Linux, macOS, and Windows.

Suite layout::

    tests/<suite>/
        test-inputs.txt | hidden-inputs.txt   test definitions (format below)
        fixtures/                             optional files copied into each test's cwd
        expected-outputs/<ID>.stdout          exact expected standard output
        expected-outputs/<ID>.stderr          exact expected standard error
        expected-outputs/<ID>.exit            exit status of each step, one per line
    tests/fixtures/                           optional fixtures shared by every suite

Test definition format (one step per line)::

    # comment
    <ID> [NAME=VALUE]... <tool> [ARG]... [< STDIN-FILE]

* ``<ID>`` is a two-digit test number. Consecutive lines with the same ID are *steps* of one
  test: they share a working directory, their stdout/stderr are concatenated, and each step's
  exit status is recorded on its own line in ``<ID>.exit``.
* The rest of the line is split with POSIX shell quoting rules (``shlex``); no shell runs.
* Leading ``NAME=VALUE`` tokens add environment variables for that step.
* A final ``< FILE`` pair redirects stdin from FILE (relative to the working directory).
* ``{PYTHON}`` in any argument is replaced with the absolute path of this Python interpreter,
  giving tests a portable child process for tools such as dp-env and dp-find.

Each test runs in a fresh temporary copy of the fixtures, with empty stdin unless redirected
and a minimal environment (see shared/CLI-CONVENTIONS.md section 9).

Tools are looked up in --bin-dir as `<tool>` (and, on Windows, `<tool>.exe` first). A tool may
be a native executable or a script that starts with a `#!` line. On Windows, which has no
shebang support, the runner starts the script's interpreter itself (resolved on PATH).

Exit status: 0 all tests passed, 1 a test failed, 2 usage or configuration error.
"""

from __future__ import annotations

import argparse
import difflib
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

INPUT_FILE_NAMES = ("test-inputs.txt", "hidden-inputs.txt")
WINDOWS_ENV_PASSTHROUGH = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP")
IS_WINDOWS = os.name == "nt"
REFERENCE_LAUNCHER = Path(__file__).resolve().parents[2] / "reference" / "run.py"
MAX_DIFF_LINES = 40


class ConfigError(Exception):
    """A suite or invocation problem that prevents tests from running at all."""


@dataclass
class Step:
    line_number: int
    env: dict[str, str]
    tool: str
    args: list[str]
    stdin_path: str | None


@dataclass
class TestCase:
    test_id: str
    steps: list[Step] = field(default_factory=list)


@dataclass
class Result:
    stdout: bytes
    stderr: bytes
    exit_codes: list[int]


def parse_step(line: str, line_number: int) -> tuple[str, Step]:
    """Parse one non-comment line of a test-inputs file into (test ID, step)."""
    try:
        tokens = shlex.split(line, comments=False, posix=True)
    except ValueError as error:
        raise ConfigError(f"line {line_number}: {error}") from None
    if len(tokens) < 2:
        raise ConfigError(f"line {line_number}: expected '<ID> <tool> [ARG]...'")
    test_id, rest = tokens[0], tokens[1:]
    if not (len(test_id) == 2 and test_id.isdigit()):
        raise ConfigError(f"line {line_number}: test ID must be two digits, got {test_id!r}")

    env: dict[str, str] = {}
    while rest and "=" in rest[0] and rest[0].split("=", 1)[0].isidentifier():
        name, value = rest.pop(0).split("=", 1)
        env[name] = value
    stdin_path = None
    if len(rest) >= 2 and rest[-2] == "<":
        stdin_path = rest[-1]
        rest = rest[:-2]
    if not rest:
        raise ConfigError(f"line {line_number}: missing tool name")
    python = sys.executable
    args = [arg.replace("{PYTHON}", python) for arg in rest[1:]]
    return test_id, Step(line_number, env, rest[0], args, stdin_path)


def load_suite(suite_dir: Path) -> list[TestCase]:
    """Read the suite's inputs file into ordered test cases."""
    inputs = next((suite_dir / n for n in INPUT_FILE_NAMES if (suite_dir / n).is_file()), None)
    if inputs is None:
        raise ConfigError(f"{suite_dir}: no {' or '.join(INPUT_FILE_NAMES)}")
    cases: list[TestCase] = []
    seen: set[str] = set()
    text = inputs.read_text(encoding="utf-8")
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        test_id, step = parse_step(line, number)
        if cases and cases[-1].test_id == test_id:
            cases[-1].steps.append(step)
            continue
        if test_id in seen:
            raise ConfigError(f"{inputs}:{number}: steps of test {test_id} must be consecutive")
        seen.add(test_id)
        cases.append(TestCase(test_id, [step]))
    return cases


class ToolResolver:
    """Maps a tool name from a test line to the command that runs it."""

    def __init__(self, bin_dir: Path | None, tool_prefix: list[str] | None):
        self.bin_dir = bin_dir
        self.tool_prefix = tool_prefix

    def command(self, tool: str) -> list[str]:
        if self.tool_prefix is not None:
            return [*self.tool_prefix, tool]
        assert self.bin_dir is not None
        names = [tool + ".exe", tool] if IS_WINDOWS else [tool]
        for name in names:
            candidate = self.bin_dir / name
            if candidate.is_file():
                path = str(candidate.resolve())
                if IS_WINDOWS and not name.endswith(".exe"):
                    return shebang_command(path)
                return [path]
        raise ConfigError(f"tool '{tool}' not found in {self.bin_dir} (did 'make all' run?)")


def shebang_command(script: str) -> list[str]:
    """Windows has no shebang support: run a `#!` launcher script through its interpreter.

    `#!/usr/bin/env [-S] NAME [ARG]...` and `#!/path/to/NAME [ARG]...` both resolve NAME on
    PATH (an absolute interpreter path is used as-is only if it exists). The interpreter is
    started directly, never through cmd.exe, so arguments reach it unmodified.
    """
    with open(script, "rb") as handle:
        first_line = handle.readline().decode("utf-8", "replace").strip()
    if not first_line.startswith("#!"):
        raise ConfigError(f"{script} is neither an .exe nor a script with a #! line")
    words = first_line[2:].split()
    if words and (words[0] == "env" or words[0].endswith("/env")):
        words = words[1:]
        if words and words[0] == "-S":
            words = words[1:]
    if not words:
        raise ConfigError(f"{script}: empty #! line")
    interpreter, *interpreter_args = words
    resolved = interpreter if os.path.isfile(interpreter) else None
    resolved = resolved or shutil.which(interpreter) or shutil.which(os.path.basename(interpreter))
    if resolved is None:
        raise ConfigError(f"{script}: interpreter '{interpreter}' not found on PATH")
    return [resolved, *interpreter_args, script]


def base_environment() -> dict[str, str]:
    env = {"PATH": os.environ.get("PATH", "")}
    if IS_WINDOWS:
        env.update({k: os.environ[k] for k in WINDOWS_ENV_PASSTHROUGH if k in os.environ})
    return env


def populate_workdir(workdir: Path, suite_dir: Path) -> None:
    """Copy shared then suite fixtures into workdir, giving every file a fresh mtime."""
    for source in (suite_dir.parent / "fixtures", suite_dir / "fixtures"):
        if source.is_dir():
            shutil.copytree(source, workdir, dirs_exist_ok=True, copy_function=shutil.copy)


def run_case(case: TestCase, suite_dir: Path, resolver: ToolResolver, timeout: float) -> Result:
    stdout, stderr, exit_codes = bytearray(), bytearray(), []
    workdir = Path(tempfile.mkdtemp(prefix=f"dp-test-{case.test_id}-"))
    try:
        populate_workdir(workdir, suite_dir)
        for step in case.steps:
            env = base_environment()
            env.update(step.env)
            stdin = None
            try:
                if step.stdin_path is not None:
                    stdin = open(workdir / step.stdin_path, "rb")
                completed = subprocess.run(
                    [*resolver.command(step.tool), *step.args],
                    cwd=workdir,
                    env=env,
                    stdin=stdin if stdin is not None else subprocess.DEVNULL,
                    capture_output=True,
                    timeout=timeout,
                )
            except FileNotFoundError as error:
                raise ConfigError(f"line {step.line_number}: {error}") from None
            except subprocess.TimeoutExpired:
                stderr += f"[run-tests] step at line {step.line_number} timed out\n".encode()
                exit_codes.append(-1)
                break
            finally:
                if stdin is not None:
                    stdin.close()
            stdout += completed.stdout
            stderr += completed.stderr
            exit_codes.append(completed.returncode)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return Result(bytes(stdout), bytes(stderr), exit_codes)


def expected_paths(suite_dir: Path, test_id: str) -> dict[str, Path]:
    base = suite_dir / "expected-outputs"
    return {kind: base / f"{test_id}.{kind}" for kind in ("stdout", "stderr", "exit")}


def encode_exit(codes: list[int]) -> bytes:
    return "".join(f"{code}\n" for code in codes).encode()


def show_diff(kind: str, expected: bytes, actual: bytes) -> str:
    def lines(data: bytes) -> list[str]:
        # Split on LF only and show CR explicitly, so line-ending bugs are visible.
        parts = data.decode("utf-8", "backslashreplace").replace("\r", "\\r").split("\n")
        return [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])

    diff = list(difflib.unified_diff(lines(expected), lines(actual), "expected", "actual"))
    rendered = [line if line.endswith("\n") else line + "\\ (no trailing newline)\n"
                for line in diff[:MAX_DIFF_LINES]]
    if len(diff) > MAX_DIFF_LINES:
        rendered.append(f"... ({len(diff) - MAX_DIFF_LINES} more diff lines)\n")
    if not diff:  # identical text after decoding, so the bytes differ in line endings etc.
        rendered = [f"expected {expected!r}\n", f"actual   {actual!r}\n"]
    return f"  --- {kind} ---\n" + "".join("    " + line for line in rendered)


def check_case(case: TestCase, result: Result, suite_dir: Path) -> list[str]:
    """Return human-readable failure reports (empty when the test passes)."""
    actual = {"stdout": result.stdout, "stderr": result.stderr,
              "exit": encode_exit(result.exit_codes)}
    failures = []
    for kind, path in expected_paths(suite_dir, case.test_id).items():
        if not path.is_file():
            failures.append(f"  missing expected file {path}\n")
            continue
        expected = path.read_bytes()
        if expected != actual[kind]:
            failures.append(show_diff(kind, expected, actual[kind]))
    return failures


def write_expected(case: TestCase, result: Result, suite_dir: Path) -> None:
    paths = expected_paths(suite_dir, case.test_id)
    paths["stdout"].parent.mkdir(parents=True, exist_ok=True)
    paths["stdout"].write_bytes(result.stdout)
    paths["stderr"].write_bytes(result.stderr)
    paths["exit"].write_bytes(encode_exit(result.exit_codes))


def run_suite(suite_dir: Path, resolver: ToolResolver, args: argparse.Namespace) -> tuple[int, int]:
    cases = load_suite(suite_dir)
    if args.only:
        cases = [case for case in cases if case.test_id in args.only]
    passed = failed = 0
    print(f"== {suite_dir}")
    for case in cases:
        result = run_case(case, suite_dir, resolver, args.timeout)
        if args.update:
            write_expected(case, result, suite_dir)
            print(f"  WROTE {case.test_id}  exit={result.exit_codes}")
            passed += 1
            continue
        failures = check_case(case, result, suite_dir)
        if failures:
            failed += 1
            print(f"  FAIL  {case.test_id}")
            if args.verbose:
                print("".join(failures), end="")
        else:
            passed += 1
            print(f"  PASS  {case.test_id}")
    return passed, failed


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run curriculum black-box test suites.",
        epilog="Example: run-tests.py --bin-dir build/bin ../tests/public",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bin-dir", type=Path, help="directory containing the built tools")
    source.add_argument("--tool-prefix", help="command prefix (POSIX quoting); the tool name "
                        "is appended")
    source.add_argument("--reference", action="store_true",
                        help="run the curriculum's reference implementations")
    parser.add_argument("suites", nargs="+", type=Path, help="suite directories")
    parser.add_argument("--only", action="append", metavar="ID", help="run only this test ID")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-step timeout (s)")
    parser.add_argument("--update", action="store_true",
                        help="overwrite expected outputs with actual results (maintainers only)")
    parser.add_argument("-q", "--quiet", dest="verbose", action="store_false",
                        help="do not print diffs for failing tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    prefix = shlex.split(args.tool_prefix) if args.tool_prefix else None
    if args.reference:
        prefix = [sys.executable, str(REFERENCE_LAUNCHER)]
    resolver = ToolResolver(args.bin_dir, prefix)
    total_passed = total_failed = 0
    try:
        for suite in args.suites:
            passed, failed = run_suite(suite, resolver, args)
            total_passed += passed
            total_failed += failed
    except ConfigError as error:
        print(f"run-tests: error: {error}", file=sys.stderr)
        return 2
    print(f"{total_passed} passed, {total_failed} failed")
    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())

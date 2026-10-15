"""Reference implementation of dp-env (projects/08-env-run/specs/SRS.md).

Section and requirement numbers in comments refer to SRS-08. The model follows the SRS order of
operations: scan options (no permutation), validate, build the environment, change directory,
resolve the command, spawn it with signal forwarding, and propagate its exit status.
"""

from __future__ import annotations

import errno
import os
import signal
import stat
import subprocess
from dataclasses import dataclass, field

from .common import (
    Option,
    UsageError,
    diagnose,
    encode_arg,
    file_error_reason,
    handle_action,
    out,
    parse_args,
    usage_failure,
    write,
)

TOOL = "dp-env"
IS_WINDOWS = os.name == "nt"

EXIT_FAILURE = 125  # dp-env itself failed (including usage errors)
EXIT_CANNOT_RUN = 126  # COMMAND was found but could not be started
EXIT_NOT_FOUND = 127  # COMMAND was not found
DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD"
FORWARDED_SIGNALS = ("SIGINT", "SIGTERM", "SIGHUP")
WINDOWS_BAD_EXE_FORMAT = 193  # ERROR_BAD_EXE_FORMAT

HELP_TEXT = """\
Usage: dp-env [OPTION]... [-] [NAME=VALUE]... [COMMAND [ARG]...]
Set each NAME to VALUE in the environment and run COMMAND.

Options are recognized only before the first operand. A lone '-' as the first
operand implies -i. Without COMMAND, print the resulting environment, one
NAME=VALUE entry per line, sorted by name.

Options:
  -i, --ignore-environment  start with an empty environment
  -u, --unset=NAME          remove variable NAME from the environment
  -C, --chdir=DIR           change the working directory to DIR before
                              running COMMAND
  -0, --null                end each printed entry with NUL, not newline
      --help                display this help and exit
      --version             output version information and exit

Exit status:
  125  dp-env itself failed
  126  COMMAND was found but could not be run
  127  COMMAND was not found
  otherwise, the exit status of COMMAND (128+N if killed by signal N)
"""

OPTIONS = [
    Option("ignore", short="i", long="ignore-environment"),
    Option("unset", short="u", long="unset", takes_value=True, repeatable=True),
    Option("chdir", short="C", long="chdir", takes_value=True),
    Option("null", short="0", long="null"),
]


class RuntimeFailure(Exception):
    """A non-usage failure: ``str(error)`` is the diagnostic, ``status`` the exit status."""

    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status


# --- environment model (FR-05 .. FR-08) ------------------------------------------------


def name_key(name: str) -> str:
    """Variable names compare case-insensitively on Windows, exactly elsewhere (FR-08)."""
    return name.upper() if IS_WINDOWS else name


@dataclass
class Environment:
    """Ordered name -> value mapping that remembers each entry's spelling."""

    entries: dict[str, tuple[str, str]] = field(
        default_factory=dict
    )  # key -> (name, value)

    @classmethod
    def inherited(cls) -> Environment:
        env = cls()
        # Note: on Windows, os.environ reports names in upper case, so the inherited spelling
        # is not preserved by this model. The black-box suites only print under -i.
        for name, value in os.environ.items():
            if name and not name.startswith("="):
                env.set(name, value)
        return env

    def set(self, name: str, value: str) -> None:
        self.entries.pop(name_key(name), None)
        self.entries[name_key(name)] = (name, value)

    def unset(self, name: str) -> None:
        self.entries.pop(name_key(name), None)

    def get(self, name: str) -> str | None:
        entry = self.entries.get(name_key(name))
        return entry[1] if entry else None

    def sorted_items(self) -> list[tuple[str, str]]:
        return sorted(self.entries.values(), key=lambda item: encode_arg(item[0]))

    def as_dict(self) -> dict[str, str]:
        return dict(self.entries.values())


@dataclass
class Request:
    ignore: bool
    unset: list[str]
    assignments: list[tuple[str, str]]
    chdir: str | None
    null: bool
    command: list[str]


def parse_request(argv: list[str]) -> Request | None:
    """Scan and validate the command line (FR-01 .. FR-04). Returns None after help/version."""
    parsed = parse_args(argv, OPTIONS, permute=False)
    if handle_action(TOOL, parsed, HELP_TEXT):
        return None
    operands = list(parsed.operands)
    ignore = bool(parsed.values.get("ignore"))
    if operands and operands[0] == "-":
        ignore = True
        operands.pop(0)
    unset = [str(name) for name in parsed.values.get("unset", [])]  # type: ignore
    for name in unset:
        if name == "" or "=" in name:
            raise RuntimeFailure(
                f"cannot unset '{name}': Invalid argument", EXIT_FAILURE
            )
    assignments = []
    while operands and "=" in operands[0]:
        name, _, value = operands.pop(0).partition("=")
        if name == "":
            raise RuntimeFailure(
                f"cannot set '={value}': Invalid argument", EXIT_FAILURE
            )
        assignments.append((name, value))
    chdir = parsed.values.get("chdir")
    null = bool(parsed.values.get("null"))
    if null and operands:
        raise UsageError("cannot specify --null (-0) with command")
    if chdir is not None and not operands:
        raise UsageError("must specify command with --chdir (-C)")
    return Request(
        ignore,
        unset,
        assignments,
        None if chdir is None else str(chdir),
        null,
        operands,
    )


def build_environment(request: Request) -> Environment:
    env = Environment() if request.ignore else Environment.inherited()
    for name in request.unset:
        env.unset(name)
    for name, value in request.assignments:
        env.set(name, value)
    return env


def print_environment(env: Environment, null: bool) -> None:
    """FR-09: one NAME=VALUE entry per line (or NUL-terminated), byte-wise sorted by name."""
    terminator = b"\0" if null else b"\n"
    data = b"".join(
        encode_arg(f"{name}={value}") + terminator for name, value in env.sorted_items()
    )
    try:
        write(data)
        out.flush()
    except BrokenPipeError:
        raise
    except OSError:
        raise RuntimeFailure("write error", EXIT_FAILURE) from None


# --- working directory and command resolution (FR-10 .. FR-12) --------------------------


def change_directory(directory: str) -> None:
    try:
        if os.path.exists(directory) and not os.path.isdir(directory):
            raise NotADirectoryError(errno.ENOTDIR, "Not a directory", directory)
        os.chdir(directory)
    except OSError as error:
        reason = file_error_reason(error)
        raise RuntimeFailure(
            f"cannot change directory to '{directory}': {reason}", EXIT_FAILURE
        ) from None


def has_separator(command: str) -> bool:
    if IS_WINDOWS:
        return (
            "/" in command
            or "\\" in command
            or (len(command) >= 2 and command[1] == ":")
        )
    return "/" in command


def pathext(env: Environment) -> list[str]:
    value = env.get("PATHEXT")
    if value is None:
        value = os.environ.get("PATHEXT", DEFAULT_PATHEXT)
    return [ext for ext in value.split(";") if ext]


def candidates(base: str, extensions: list[str]) -> list[str]:
    """The file names tried for one base path: just ``base`` on POSIX (FR-11)."""
    if not IS_WINDOWS:
        return [base]
    name = base.replace("\\", "/").rsplit("/", 1)[-1]
    if any(name.upper().endswith(ext.upper()) for ext in extensions):
        return [base]
    return [base + ext for ext in extensions]


def is_file(path: str) -> bool:
    try:
        return not stat.S_ISDIR(os.stat(path).st_mode)
    except (OSError, ValueError):
        return False


def is_executable(path: str) -> bool:
    return IS_WINDOWS or os.access(path, os.X_OK)


def not_found(command: str) -> RuntimeFailure:
    return RuntimeFailure(f"'{command}': No such file or directory", EXIT_NOT_FOUND)


def cannot_run(command: str, reason: str) -> RuntimeFailure:
    return RuntimeFailure(f"'{command}': {reason}", EXIT_CANNOT_RUN)


def resolve_command(command: str, env: Environment) -> str:
    """Return the file to execute for COMMAND, or raise the FR-11/FR-12 failure."""
    extensions = pathext(env)
    if has_separator(command):
        if os.path.isdir(command):
            raise cannot_run(command, "Is a directory")
        for candidate in candidates(command, extensions):
            if is_file(candidate):
                return candidate
        raise not_found(command)
    if command == "":
        raise not_found(command)
    search_path = env.get("PATH")
    if search_path is None:
        search_path = os.environ.get("PATH", "")
    denied = False
    for directory in search_path.split(os.pathsep):
        if not directory:
            continue
        for candidate in candidates(directory + "/" + command, extensions):
            if not is_file(candidate):
                continue
            if is_executable(candidate):
                return candidate
            denied = True
    if denied:
        raise cannot_run(command, "Permission denied")
    raise not_found(command)


def spawn_failure(command: str, error: OSError) -> RuntimeFailure:
    """FR-12: map a failure to start the selected file to 127 or 126."""
    if isinstance(error, FileNotFoundError):
        return not_found(command)
    if (
        error.errno == errno.ENOEXEC
        or getattr(error, "winerror", None) == WINDOWS_BAD_EXE_FORMAT
    ):
        return cannot_run(command, "Exec format error")
    return cannot_run(command, file_error_reason(error))


# --- execution with signal forwarding (FR-13 .. FR-15) ----------------------------------


class SignalForwarder:
    """Relays SIGINT/SIGTERM/SIGHUP to the child (POSIX) or ignores console events (Windows).

    Handlers are installed before the child is spawned; a signal that arrives before the child
    exists is queued and delivered as soon as it does (FR-14). Signals that were ignored when
    dp-env started stay ignored and are not forwarded.
    """

    def __init__(self) -> None:
        self.child: subprocess.Popen[bytes] | None = None
        self.pending: list[int] = []
        self.previous: dict[int, object] = {}

    def install(self) -> None:
        names = ("SIGINT", "SIGBREAK") if IS_WINDOWS else FORWARDED_SIGNALS
        for name in names:
            number = getattr(signal, name, None)
            if number is None or signal.getsignal(number) == signal.SIG_IGN:
                continue
            handler = signal.SIG_IGN if IS_WINDOWS else self.forward
            self.previous[number] = signal.signal(number, handler)

    def attach(self, child: subprocess.Popen[bytes]) -> None:
        self.child = child
        for number in self.pending:
            self._send(number)
        self.pending.clear()

    def restore(self) -> None:
        for number, handler in self.previous.items():
            signal.signal(number, handler)  # type: ignore

    def forward(self, number: int, _frame: object) -> None:
        if self.child is None:
            self.pending.append(number)
        else:
            self._send(number)

    def _send(self, number: int) -> None:
        assert self.child is not None
        if self.child.returncode is None:
            try:
                os.kill(self.child.pid, number)
            except ProcessLookupError:
                pass


def exit_status(returncode: int) -> int:
    """FR-15: a POSIX signal death N becomes 128+N; Windows codes pass through unchanged."""
    if returncode < 0:
        return 128 - returncode
    if IS_WINDOWS and returncode > 0x7FFFFFFF:
        return returncode - 0x100000000  # same 32-bit value, as a signed C int
    return returncode


def run_command(command: list[str], executable: str, env: Environment) -> int:
    forwarder = SignalForwarder()
    forwarder.install()
    try:
        try:
            child = subprocess.Popen(command, executable=executable, env=env.as_dict())
        except OSError as error:
            raise spawn_failure(command[0], error) from None
        forwarder.attach(child)
        return exit_status(child.wait())
    finally:
        forwarder.restore()


def main(argv: list[str]) -> int:
    try:
        request = parse_request(argv)
        if request is None:
            return 0
        env = build_environment(request)
        if not request.command:
            print_environment(env, request.null)
            return 0
        if request.chdir is not None:
            change_directory(request.chdir)
        executable = resolve_command(request.command[0], env)
        return run_command(request.command, executable, env)
    except UsageError as error:
        usage_failure(TOOL, error)
        return EXIT_FAILURE
    except RuntimeFailure as failure:
        diagnose(TOOL, str(failure))
        return failure.status

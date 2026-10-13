"""Shared helpers for the reference implementations (shared/CLI-CONVENTIONS.md).

Every reference tool is a module in this package that exposes ``main(argv) -> int``, where
``argv`` excludes the program name. Tools use :func:`parse_args` for CONV-07..CONV-15 option
handling, write bytes through :data:`out` / :data:`err` (never text-mode streams, CONV-03), and
are started through :func:`run` (CONV-24, CONV-25).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import BinaryIO, Callable

SPEC_VERSION = "1.0.0"


class UsageError(Exception):
    """A CONV-13 usage error; ``str(error)`` is the message without the tool prefix."""


@dataclass(frozen=True)
class Option:
    """One command-line option. ``dest`` names the key in :attr:`Parsed.values`."""

    dest: str
    short: str | None = None
    long: str | None = None
    takes_value: bool = False
    repeatable: bool = False  # collect every value into a list instead of last-wins

    def spelled(self, used_long: bool) -> str:
        return f"--{self.long}" if used_long else f"-{self.short}"


@dataclass
class Parsed:
    values: dict[str, object] = field(default_factory=dict)
    operands: list[str] = field(default_factory=list)
    action: str | None = None  # "help" or "version" when requested (CONV-12)
    spelled: dict[str, str] = field(default_factory=dict)  # dest -> option as last written


HELP = Option("__help", long="help")
VERSION = Option("__version", long="version")


def parse_args(argv: list[str], options: list[Option], *, permute: bool = True) -> Parsed:
    """Parse ``argv`` per CONV-07..CONV-13.

    Flags store True, valued options store their string (or a list when ``repeatable``).
    With ``permute=False``, the first operand ends option processing (used by dp-env).
    Raises :class:`UsageError` for malformed options; value validation is left to the tool,
    which can report it with :func:`invalid_argument` using ``parsed.spelled[dest]``.
    """
    all_options = [*options, HELP, VERSION]
    by_short = {o.short: o for o in all_options if o.short}
    by_long = {o.long: o for o in all_options if o.long}
    parsed = Parsed()

    def store(option: Option, value: object, spelled: str) -> bool:
        if option is HELP or option is VERSION:
            parsed.action = "help" if option is HELP else "version"
            return True
        if option.repeatable:
            parsed.values.setdefault(option.dest, []).append(value)  # type: ignore[union-attr]
        else:
            parsed.values[option.dest] = value
        parsed.spelled[option.dest] = spelled
        return False

    index = 0
    while index < len(argv):
        token = argv[index]
        index += 1
        if token == "--":
            parsed.operands.extend(argv[index:])
            break
        if token.startswith("--"):
            name, has_inline, inline = token[2:].partition("=")
            option = by_long.get(name)
            if option is None:
                raise UsageError(f"unrecognized option '{token}'")
            if option.takes_value:
                if has_inline:
                    value = inline
                elif index < len(argv):
                    value = argv[index]
                    index += 1
                else:
                    raise UsageError(f"option '--{name}' requires an argument")
            elif has_inline:
                raise UsageError(f"option '--{name}' doesn't allow an argument")
            else:
                value = True
            if store(option, value, f"--{name}"):
                return parsed
            continue
        if token.startswith("-") and token != "-":
            position = 1
            while position < len(token):
                letter = token[position]
                position += 1
                option = by_short.get(letter)
                if option is None:
                    raise UsageError(f"invalid option -- '{letter}'")
                if not option.takes_value:
                    if store(option, True, f"-{letter}"):
                        return parsed
                    continue
                if position < len(token):
                    value = token[position:]
                elif index < len(argv):
                    value = argv[index]
                    index += 1
                else:
                    raise UsageError(f"option requires an argument -- '{letter}'")
                store(option, value, f"-{letter}")
                break
            continue
        parsed.operands.append(token)
        if not permute:
            parsed.operands.extend(argv[index:])
            break
    return parsed


def invalid_argument(value: str, spelled_option: str) -> UsageError:
    return UsageError(f"invalid argument '{value}' for '{spelled_option}'")


def parse_count(value: str, spelled_option: str, minimum: int = 0,
                maximum: int | None = None) -> int:
    """Parse an ASCII-decimal integer option value within [minimum, maximum]."""
    if not value or not all("0" <= c <= "9" for c in value):
        raise invalid_argument(value, spelled_option)
    number = int(value)
    if number < minimum or (maximum is not None and number > maximum):
        raise invalid_argument(value, spelled_option)
    return number


# --- byte-oriented output (CONV-03) ------------------------------------------------------

out: BinaryIO = sys.stdout.buffer
err: BinaryIO = sys.stderr.buffer


def encode_arg(text: str) -> bytes:
    """UTF-8 bytes of a command-line argument exactly as the user supplied it (CONV-05)."""
    if os.name == "nt":
        return text.encode("utf-8", "surrogatepass")
    return os.fsencode(text)


def write(data: bytes | str) -> None:
    out.write(data if isinstance(data, bytes) else encode_arg(data))


def diagnose(tool: str, message: str) -> None:
    """Write ``<tool>: <message>`` plus LF to standard error."""
    err.write(encode_arg(f"{tool}: {message}\n"))


def usage_failure(tool: str, error: UsageError) -> int:
    """Report a usage error per CONV-13/CONV-14 and return exit status 2."""
    diagnose(tool, str(error))
    err.write(encode_arg(f"Try '{tool} --help' for more information.\n"))
    return 2


def version_line(tool: str) -> bytes:
    return f"{tool} (dialectic-playground) {SPEC_VERSION}\n".encode()


def handle_action(tool: str, parsed: Parsed, help_text: str) -> bool:
    """Print help/version if requested (CONV-22/23). Returns True when the tool should exit 0."""
    if parsed.action == "help":
        write(help_text.encode())
        return True
    if parsed.action == "version":
        write(version_line(tool))
        return True
    return False


def file_error_reason(error: OSError, path: str | None = None) -> str:
    """Map an OSError to the fixed CONV-16 reason text."""
    if path is not None and os.path.isdir(path) and not isinstance(error, FileNotFoundError):
        return "Is a directory"
    if isinstance(error, FileNotFoundError):
        return "No such file or directory"
    if isinstance(error, IsADirectoryError):
        return "Is a directory"
    if isinstance(error, NotADirectoryError):
        return "Not a directory"
    if isinstance(error, PermissionError):
        return "Permission denied"
    return "Input/output error"


def file_failure(tool: str, path: str, error: OSError) -> None:
    diagnose(tool, f"{path}: {file_error_reason(error, path)}")


def open_input(path: str) -> BinaryIO:
    """Open a file operand for binary reading; ``-`` is standard input (CONV-10).

    Directories raise IsADirectoryError on every platform (Windows would say EACCES).
    """
    if path == "-":
        return sys.stdin.buffer
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    return open(path, "rb")


def _silence_stdout() -> None:
    """Point stdout at the null device so the interpreter's exit-time flush stays quiet."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())


def run(main: Callable[[list[str]], int], tool: str) -> None:
    """Process entry point: run ``main`` and exit, honouring CONV-24/CONV-25."""
    try:
        status = main(sys.argv[1:])
        out.flush()
    except BrokenPipeError:
        _silence_stdout()  # CONV-25: stop quietly
        status = 1
    except OSError:
        _silence_stdout()  # CONV-24: e.g. disk full; report instead of a traceback
        diagnose(tool, "write error")
        status = 1
    except KeyboardInterrupt:
        status = 130
    sys.exit(status)

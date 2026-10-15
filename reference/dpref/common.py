"""Shared helpers for the reference implementations (shared/CLI-CONVENTIONS.md).

Every reference tool is a module in this package that exposes ``main(argv) -> int``, where
``argv`` excludes the program name. Tools use :func:`parse_args` for CONV-07..CONV-15 option
handling, write bytes through :data:`out` / :data:`err` (never text-mode streams, CONV-03), and
are started through :func:`run` (CONV-24, CONV-25).
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import BinaryIO

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
    spelled: dict[str, str] = field(
        default_factory=dict
    )  # dest -> option as last written


HELP = Option("__help", long="help")
VERSION = Option("__version", long="version")


def parse_args(
    argv: list[str], options: list[Option], *, permute: bool = True
) -> Parsed:
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
            parsed.values.setdefault(option.dest, []).append(value)  # type: ignore
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


def parse_count(
    value: str, spelled_option: str, minimum: int = 0, maximum: int | None = None
) -> int:
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
    if (
        path is not None
        and os.path.isdir(path)
        and not isinstance(error, FileNotFoundError)
    ):
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


# --- data input, numbers, prompts, and randomness (CONV-32 … CONV-38) -------------------

WHITESPACE = b" \t\n\v\f\r"
_INTEGER = re.compile(rb"[+-]?[0-9]+\Z")
_REAL = re.compile(rb"[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?\Z")
INT64_MIN, INT64_MAX = -(2**63), 2**63 - 1


class DataError(Exception):
    """A CONV-34 data diagnostic: ``<source>:<line>: <message>`` (message may hold raw bytes)."""

    def __init__(self, source: str, line: int, message: bytes | str):
        super().__init__(message)
        self.source = source
        self.line = line
        self.message = message if isinstance(message, bytes) else message.encode()


@dataclass(frozen=True)
class Token:
    text: bytes
    line: int


def strip_eof_marker(data: bytes) -> bytes:
    """Drop a trailing run of 0x1A bytes from text data (CONV-37)."""
    return data.rstrip(b"\x1a")


def tokenize(data: bytes) -> list[Token]:
    """Split ``data`` into whitespace-separated tokens with line numbers (CONV-32)."""
    tokens = []
    line = 1
    start = None
    for index, byte in enumerate(data):
        if byte in WHITESPACE:
            if start is not None:
                tokens.append(Token(data[start:index], line))
                start = None
            if byte == 0x0A:
                line += 1
        elif start is None:
            start = index
            token_line = line
    if start is not None:
        tokens.append(Token(data[start:], token_line))
    return tokens


def end_line(data: bytes) -> int:
    """The end-of-input line number (CONV-32)."""
    return data.count(b"\n") + 1


def parse_int_token(
    token: Token, source: str, minimum: int = INT64_MIN, maximum: int = INT64_MAX
) -> int:
    """An *integer* token (CONV-33), optionally range-restricted (``value out of range``)."""
    if not _INTEGER.match(token.text) or not INT64_MIN <= int(token.text) <= INT64_MAX:
        raise DataError(source, token.line, b"invalid integer '" + token.text + b"'")
    value = int(token.text)
    if not minimum <= value <= maximum:
        raise DataError(source, token.line, b"value out of range '" + token.text + b"'")
    return value


def parse_real_token(token: Token, source: str) -> float:
    """A *real* token (CONV-33): nearest binary64, overflow to infinity is invalid."""
    if _REAL.match(token.text):
        value = float(token.text)
        if value not in (float("inf"), float("-inf")):
            return value
    raise DataError(source, token.line, b"invalid number '" + token.text + b"'")


def unexpected_end(source: str, data: bytes) -> DataError:
    return DataError(source, end_line(data), "unexpected end of input")


def data_failure(tool: str, error: DataError) -> int:
    """Write a CONV-34 diagnostic and return exit status 1."""
    err.write(
        encode_arg(f"{tool}: {error.source}:{error.line}: ") + error.message + b"\n"
    )
    return 1


def fix(value: float, digits: int) -> str:
    """``FIX(x, n)`` (CONV-35): correctly rounded fixed point, no negative zero."""
    text = f"{value:.{digits}f}"
    if text.startswith("-") and not text.strip("-0."):
        text = text[1:]
    return text


def gen(value: float, precision: int) -> str:
    """``GEN(x, p)`` (CONV-35): C's ``%.pg``, no negative zero."""
    text = f"{value:.{precision}g}"
    return "0" if text in ("-0", "0") else text


def prompt(enabled: bool, text: str | bytes) -> None:
    """Write a CONV-36 prompt to standard error (only with --prompt) and flush."""
    if enabled:
        err.write(text if isinstance(text, bytes) else text.encode())
        err.flush()


PROMPT = Option("prompt", short="p", long="prompt")
MAX_SEED = 2**32 - 1


def parse_seed(parsed: Parsed, dest: str = "seed") -> int:
    """The CONV-38 seed: default 1, ASCII digits 0 … 4294967295."""
    if dest not in parsed.values:
        return 1
    return parse_count(str(parsed.values[dest]), parsed.spelled[dest], 0, MAX_SEED)


class AnsiRand:
    """The ANSI C standard's portable rand() example (CONV-38)."""

    def __init__(self, seed: int = 1):
        self.state = seed & 0xFFFFFFFF

    def next(self) -> int:
        self.state = (self.state * 1103515245 + 12345) & 0xFFFFFFFF
        return (self.state // 65536) % 32768


def read_all(path: str) -> bytes:
    """Read a whole input (``-`` is standard input); raises OSError per open_input."""
    handle = open_input(path)
    try:
        return handle.read()
    finally:
        if handle is not sys.stdin.buffer:
            handle.close()


class InputError(Exception):
    """A failure while *reading* an input, kept apart from output failures (CONV-25)."""

    def __init__(self, error: OSError):
        super().__init__(error)
        self.error = error


class InputStream:
    """Incremental reader of tokens (CONV-32) and lines from one input.

    Data is requested with ``read1``, so a token or line is returned as soon as it is complete
    and an interactive dialog never waits for input it does not need. With ``eof_marker``
    (the default), a run of 0x1A bytes that reaches the end of the input is ignored (CONV-37).
    :attr:`line` is 1 plus the number of LF bytes consumed so far; once the input is
    exhausted it is the end-of-input line number. Read failures raise :class:`InputError`.
    """

    CHUNK_SIZE = 65536

    def __init__(self, handle: BinaryIO, *, eof_marker: bool = True):
        self.handle = handle
        self.eof_marker = eof_marker
        self.buffer = bytearray()
        self.position = 0
        self.at_eof = False
        self.line = 1

    def _fill(self) -> bool:
        """Read more data; False (and CONV-37 applied) once the input is exhausted."""
        if self.at_eof:
            return False
        try:
            chunk = self.handle.read1(self.CHUNK_SIZE)  # type: ignore
        except OSError as error:
            raise InputError(error) from error
        if chunk:
            del self.buffer[: self.position]
            self.position = 0
            self.buffer += chunk
            return True
        self.at_eof = True
        if self.eof_marker:
            end = len(self.buffer)
            while end > self.position and self.buffer[end - 1] == 0x1A:
                end -= 1
            del self.buffer[end:]
        return False

    def token(self) -> Token | None:
        """The next whitespace-delimited token, or None at the end of the input."""
        while True:
            while (
                self.position < len(self.buffer)
                and self.buffer[self.position] in WHITESPACE
            ):
                if self.buffer[self.position] == 0x0A:
                    self.line += 1
                self.position += 1
            if self.position < len(self.buffer) or not self._fill():
                break
        if self.position >= len(self.buffer):
            return None
        start, scan = self.position, self.position
        while True:
            while scan < len(self.buffer) and self.buffer[scan] not in WHITESPACE:
                scan += 1
            if scan < len(self.buffer):
                break
            offset = scan - self.position
            if not self._fill():
                scan = len(self.buffer)
                break
            start, scan = self.position, self.position + offset
        if scan <= start:  # the token was a 0x1A run reaching the end of the input
            self.position = len(self.buffer)
            return None
        text = bytes(self.buffer[start:scan])
        self.position = scan
        return Token(text, self.line)

    def read_line(self) -> Token | None:
        """The next line without its LF (any CR is kept), or None at the end of the input.

        A final segment without LF is a line if it is not empty.
        """
        while True:
            newline = self.buffer.find(b"\n", self.position)
            if newline >= 0:
                text = bytes(self.buffer[self.position : newline])
                self.position = newline + 1
                number = self.line
                self.line += 1
                return Token(text, number)
            if not self._fill():
                break
        if self.position >= len(self.buffer):
            return None
        text = bytes(self.buffer[self.position :])
        self.position = len(self.buffer)
        return Token(text, self.line)

    def require(self, source: str) -> Token:
        """The next token; ``unexpected end of input`` (CONV-34) if there is none."""
        token = self.token()
        if token is None:
            raise self.unexpected_end(source)
        return token

    def unexpected_end(self, source: str) -> DataError:
        return DataError(source, self.line, "unexpected end of input")

"""Reference implementation of dp-echo (projects/01-echo/specs/SRS.md).

dp-echo deliberately does not use :func:`common.parse_args`: like POSIX/GNU ``echo`` it
recognizes only *leading* option tokens made of ``-`` and the letters ``n``, ``e``, ``E``
(SRS FR-02), and ``--help`` / ``--version`` only when they are the sole argument (FR-03).
It therefore has no usage errors. Escape processing (FR-07) works on the UTF-8 bytes of each
operand, so non-ASCII text passes through unchanged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from . import common
from .common import encode_arg, version_line, write

TOOL = "dp-echo"
OPTION_LETTERS = frozenset("neE")

HELP_TEXT = r"""Usage: dp-echo [SHORT-OPTION]... [STRING]...
  or:  dp-echo --help
  or:  dp-echo --version
Write the STRINGs to standard output, separated by single spaces and followed
by a line feed (LF) on every platform.

Only leading arguments made of '-' and the letters n, e, E are options. The
first other argument and every argument after it is printed as given; '--' is
not special. --help and --version are recognized only as the sole argument.

Options:
  -n             do not output the trailing line feed
  -e             enable interpretation of backslash escapes
  -E             disable interpretation of backslash escapes (default)
      --help     display this help and exit
      --version  output version information and exit

When -e is in effect, the following sequences are recognized:
  \\      backslash
  \a      alert (BEL, 0x07)
  \b      backspace (0x08)
  \c      produce no further output, not even the line feed
  \e      escape (0x1B)
  \f      form feed (0x0C)
  \n      line feed (LF, 0x0A)
  \r      carriage return (CR, 0x0D)
  \t      horizontal tab (0x09)
  \v      vertical tab (0x0B)
  \0NNN   byte with octal value NNN (0 to 3 octal digits)
  \xHH    byte with hexadecimal value HH (1 to 2 hex digits)
Any other backslash is printed as is. To print a CRLF line ending, use
-ne 'text\r\n'.
"""

SIMPLE_ESCAPES = {
    ord("\\"): b"\\",
    ord("a"): b"\x07",
    ord("b"): b"\x08",
    ord("e"): b"\x1b",
    ord("f"): b"\x0c",
    ord("n"): b"\n",
    ord("r"): b"\r",
    ord("t"): b"\t",
    ord("v"): b"\x0b",
}
OCTAL_DIGITS = frozenset(b"01234567")
HEX_DIGITS = frozenset(b"0123456789abcdefABCDEF")
BACKSLASH = ord("\\")


@dataclass
class Settings:
    newline: bool = True
    escapes: bool = False


def is_option_token(arg: str) -> bool:
    """True for ``-`` followed by one or more of the letters n, e, E (FR-02)."""
    return len(arg) >= 2 and arg[0] == "-" and all(c in OPTION_LETTERS for c in arg[1:])


def split_arguments(argv: list[str]) -> tuple[Settings, list[str]]:
    """Consume the leading option tokens; return the settings and the operands."""
    settings = Settings()
    index = 0
    while index < len(argv) and is_option_token(argv[index]):
        for letter in argv[index][1:]:
            if letter == "n":
                settings.newline = False
            else:
                settings.escapes = letter == "e"  # last of -e / -E wins
        index += 1
    return settings, argv[index:]


def take_digits(data: bytes, start: int, allowed: frozenset[int], limit: int) -> int:
    """Return the end index of the run of at most ``limit`` digits starting at ``start``."""
    end = start
    while end < len(data) and end - start < limit and data[end] in allowed:
        end += 1
    return end


def expand_escapes(data: bytes) -> tuple[bytes, bool]:
    """Interpret FR-07 escapes in one operand. Returns (bytes, stop) where stop means ``\\c``."""
    result = bytearray()
    index = 0
    while index < len(data):
        byte = data[index]
        if byte != BACKSLASH or index + 1 == len(data):
            result.append(byte)  # ordinary byte, or a trailing lone backslash
            index += 1
            continue
        code = data[index + 1]
        index += 2
        if code in SIMPLE_ESCAPES:
            result += SIMPLE_ESCAPES[code]
        elif code == ord("c"):
            return bytes(result), True
        elif code == ord("0"):
            end = take_digits(data, index, OCTAL_DIGITS, 3)
            result.append(int(data[index:end] or b"0", 8) % 256)
            index = end
        elif code == ord("x") and index < len(data) and data[index] in HEX_DIGITS:
            end = take_digits(data, index, HEX_DIGITS, 2)
            result.append(int(data[index:end], 16))
            index = end
        else:
            result += bytes((BACKSLASH, code))  # unknown escape: printed literally
    return bytes(result), False


def emit(settings: Settings, operands: list[str]) -> None:
    """Write the operands (FR-05..FR-08); returns early after ``\\c``."""
    for position, operand in enumerate(operands):
        if position:
            write(b" ")
        data = encode_arg(operand)
        if settings.escapes:
            data, stop = expand_escapes(data)
            write(data)
            if stop:
                return
        else:
            write(data)
    if settings.newline:
        write(b"\n")


def discard_pending_output() -> None:
    """Point stdout at the null device so the unwritable buffered bytes are dropped quietly.

    common.run flushes stdout once more after main returns; without this, that flush would
    fail again and the interpreter would print a traceback (CONV-24).
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, common.out.fileno())
    os.close(devnull)


def main(argv: list[str]) -> int:
    if argv == ["--help"]:
        write(HELP_TEXT.encode())
        return 0
    if argv == ["--version"]:
        write(version_line(TOOL))
        return 0
    settings, operands = split_arguments(argv)
    try:
        emit(settings, operands)
        common.out.flush()
    except BrokenPipeError:
        raise  # CONV-25: common.run terminates quietly
    except OSError:
        common.diagnose(TOOL, "write error")  # FR-10
        discard_pending_output()
        return 1
    return 0

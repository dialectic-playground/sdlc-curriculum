"""Logic shared by dp-head and dp-tail (projects/03-head-tail/specs/SRS.md).

Covers the NUM grammar (SRS FR-03), the multi-file header rules (FR-05), the per-operand
driver with CONV-16/CONV-17 error handling, and the bounded-memory slicing primitives used by
both tools (NFR-02, NFR-03): fixed-size block copies, a backwards block scan that locates the
start of the last N lines of a seekable regular file, and streaming fallbacks that retain only
a bounded window for non-seekable input.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from typing import BinaryIO, Callable

from .common import diagnose, encode_arg, file_error_reason, invalid_argument, open_input, write

BLOCK_SIZE = 64 * 1024
MAX_AMOUNT = 2**63 - 1
SUFFIXES = {"K": 1024, "M": 1024**2, "G": 1024**3}
STDIN_NAME = "standard input"
LF = b"\n"


# --- option values -----------------------------------------------------------------------

@dataclass(frozen=True)
class Amount:
    """A parsed NUM: ``sign`` is '' (none), '-' or '+'; ``count`` is lines or bytes."""

    sign: str
    count: int
    lines: bool


def parse_amount(value: str, spelled: str, signs: str) -> Amount:
    """Parse ``[SIGN]DIGITS[SUFFIX]`` (SRS FR-03); ``signs`` lists the accepted signs."""
    body = value
    sign = ""
    if body and body[0] in signs:
        sign, body = body[0], body[1:]
    multiplier = 1
    if body and body[-1] in SUFFIXES:
        multiplier, body = SUFFIXES[body[-1]], body[:-1]
    if not body or not all("0" <= c <= "9" for c in body):
        raise invalid_argument(value, spelled)
    count = int(body) * multiplier
    if count > MAX_AMOUNT:
        raise invalid_argument(value, spelled)
    return Amount(sign, count, spelled in ("-n", "--lines"))


def headers_wanted(spelled_mode: str | None, operand_count: int) -> bool:
    """FR-05: -q never, -v always (the later of the two wins), otherwise when 2+ operands."""
    if spelled_mode in ("-q", "--quiet"):
        return False
    if spelled_mode in ("-v", "--verbose"):
        return True
    return operand_count > 1


def display_name(operand: str) -> str:
    return STDIN_NAME if operand == "-" else operand


@dataclass
class HeaderWriter:
    enabled: bool
    written: bool = False
    last: object = None  # identity of the input whose header was written most recently

    def emit(self, name: str, key: object) -> None:
        if not self.enabled:
            return
        prefix = b"\n" if self.written else b""
        write(prefix + b"==> " + encode_arg(name) + b" <==\n")
        self.written = True
        self.last = key


# --- per-operand driver ------------------------------------------------------------------

@dataclass
class Input:
    operand: str
    name: str
    stream: BinaryIO
    keep_open: bool = False
    position: int = 0  # follow mode: offset of the next unread byte


def report(tool: str, item_operand: str, error: OSError) -> None:
    path = None if item_operand == "-" else item_operand
    diagnose(tool, f"{display_name(item_operand)}: {file_error_reason(error, path)}")


def process_operands(tool: str, operands: list[str], headers: HeaderWriter,
                     handle: Callable[[Input], None]) -> bool:
    """Open each operand in order, write its header, and slice it with ``handle``.

    Failures are reported per CONV-16 and processing continues (CONV-17). A failed open
    writes no header. ``handle`` may set ``keep_open`` to retain the stream (tail -f).
    Returns True when every operand succeeded.
    """
    ok = True
    for operand in operands or ["-"]:
        try:
            stream = open_input(operand)
        except OSError as error:
            report(tool, operand, error)
            ok = False
            continue
        item = Input(operand, display_name(operand), stream)
        try:
            headers.emit(item.name, item)
            handle(item)
        except BrokenPipeError:
            raise
        except OSError as error:
            report(tool, operand, error)
            item.keep_open = False
            ok = False
        finally:
            if not item.keep_open and operand != "-":
                stream.close()
    return ok


# --- byte primitives ---------------------------------------------------------------------

def regular_region(stream: BinaryIO) -> tuple[int, int] | None:
    """Return (current offset, size) when ``stream`` is a seekable regular file, else None."""
    try:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            return None
        start = stream.tell()
    except (OSError, ValueError):
        return None
    return start, max(start, info.st_size)


def blocks(stream: BinaryIO):
    """Yield the remaining content of ``stream`` in blocks of at most BLOCK_SIZE bytes."""
    while True:
        block = stream.read1(BLOCK_SIZE)  # type: ignore[attr-defined]
        if not block:
            return
        yield block


def copy_rest(stream: BinaryIO) -> None:
    for block in blocks(stream):
        write(block)


def copy_count(stream: BinaryIO, count: int) -> None:
    """Copy at most ``count`` bytes from the current position."""
    while count > 0:
        block = stream.read1(min(BLOCK_SIZE, count))  # type: ignore[attr-defined]
        if not block:
            return
        write(block)
        count -= len(block)


def skip_count(stream: BinaryIO, count: int) -> None:
    """Advance past ``count`` bytes: by seeking when possible, otherwise by reading."""
    region = regular_region(stream)
    if region is not None:
        start, size = region
        stream.seek(min(size, start + count))
        return
    while count > 0:
        block = stream.read1(min(BLOCK_SIZE, count))  # type: ignore[attr-defined]
        if not block:
            return
        count -= len(block)


def copy_lines(stream: BinaryIO, count: int) -> None:
    """Copy the first ``count`` lines (through the count-th LF, or to end of input)."""
    if count == 0:
        return
    for block in blocks(stream):
        index = -1
        while count > 0:
            index = block.find(LF, index + 1)
            if index < 0:
                break
            count -= 1
        if count == 0:
            write(block[:index + 1])
            return
        write(block)


def skip_lines(stream: BinaryIO, count: int) -> None:
    """Discard the first ``count`` lines, then copy the rest of the input."""
    for block in blocks(stream):
        if count == 0:
            write(block)
            continue
        index = -1
        while count > 0:
            index = block.find(LF, index + 1)
            if index < 0:
                break
            count -= 1
        if count == 0:
            write(block[index + 1:])


def last_lines_offset(stream: BinaryIO, start: int, end: int, count: int) -> int:
    """Offset in [start, end] where the last ``count`` lines begin (seekable files only).

    Reads backwards from ``end`` in fixed-size blocks, so memory use is independent of the
    file size. A final line without LF counts as a line (SRS FR-02).
    """
    if count == 0 or end <= start:
        return end
    needed = count
    position = end
    first = True
    while position > start:
        size = min(BLOCK_SIZE, position - start)
        position -= size
        stream.seek(position)
        block = stream.read(size)
        if first:
            first = False
            if block.endswith(LF):
                needed += 1  # the last line's own terminator is not a boundary
        index = len(block)
        while True:
            index = block.rfind(LF, 0, index)
            if index < 0:
                break
            needed -= 1
            if needed == 0:
                return position + index + 1
    return start


def split_lines(stream: BinaryIO):
    """Yield the lines of ``stream`` (each with its LF; a final unterminated line as is)."""
    partial = bytearray()
    for block in blocks(stream):
        begin = 0
        while True:
            index = block.find(LF, begin)
            if index < 0:
                break
            if partial:
                partial += block[begin:index + 1]
                yield bytes(partial)
                partial.clear()
            else:
                yield block[begin:index + 1]
            begin = index + 1
        partial += block[begin:]
    if partial:
        yield bytes(partial)

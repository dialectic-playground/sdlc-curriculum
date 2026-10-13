"""Reference implementation of dp-cat (projects/02-cat/specs/SRS.md).

The operands are treated as one continuous byte stream (SRS FR-05): line numbering, blank-line
squeezing, and the "CR before LF" rule of ``-E`` all carry their state from one operand to the
next. Input is processed in fixed-size chunks, so memory use does not depend on file size.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from .common import (Option, UsageError, file_failure, handle_action, open_input, out,
                     parse_args, usage_failure, write)

TOOL = "dp-cat"
BUFFER_SIZE = 128 * 1024
HELP_TEXT = """\
Usage: dp-cat [OPTION]... [FILE]...
Concatenate FILE(s) to standard output.

With no FILE, or when FILE is -, read standard input.

Options:
  -A, --show-all           equivalent to -vET
  -b, --number-nonblank    number nonempty output lines, overrides -n
  -E, --show-ends          display $ at end of each line, and a CR before it as ^M
  -n, --number             number all output lines
  -s, --squeeze-blank      suppress repeated empty output lines
  -T, --show-tabs          display TAB characters as ^I
  -v, --show-nonprinting   use ^ and M- notation, except for LF and TAB
      --help               display this help and exit
      --version            output version information and exit
"""

OPTIONS = [
    Option("show_all", short="A", long="show-all"),
    Option("number_nonblank", short="b", long="number-nonblank"),
    Option("show_ends", short="E", long="show-ends"),
    Option("number", short="n", long="number"),
    Option("squeeze_blank", short="s", long="squeeze-blank"),
    Option("show_tabs", short="T", long="show-tabs"),
    Option("show_nonprinting", short="v", long="show-nonprinting"),
]

LF = 0x0A
TAB = 0x09
CR = b"\r"


@dataclass(frozen=True)
class Settings:
    number: bool = False            # -n: number every output line
    number_nonblank: bool = False   # -b: number non-empty lines (overrides -n)
    squeeze_blank: bool = False     # -s
    show_nonprinting: bool = False  # -v
    show_ends: bool = False         # -E
    show_tabs: bool = False         # -T

    @property
    def transforms(self) -> bool:
        """False when output is a byte-for-byte copy of the input (FR-06)."""
        return any((self.number, self.number_nonblank, self.squeeze_blank,
                    self.show_nonprinting, self.show_ends, self.show_tabs))


def caret_notation(value: int) -> bytes:
    """``-v`` rendering of one 7-bit value that is not LF or TAB (FR-11)."""
    if value < 0x20:
        return b"^" + bytes([value + 0x40])
    if value == 0x7F:
        return b"^?"
    return bytes([value])


def build_table(settings: Settings) -> list[bytes]:
    """Map each content byte value (never LF) to its rendered bytes (FR-11, FR-12)."""
    table = [bytes([value]) for value in range(256)]
    if settings.show_nonprinting:
        for value in range(256):
            if value in (TAB, LF):
                continue
            if value >= 0x80:
                table[value] = b"M-" + caret_notation(value - 0x80)
            else:
                table[value] = caret_notation(value)
    if settings.show_tabs:
        table[TAB] = b"^I"
    return table


class Formatter:
    """Stateful streaming transformation of the concatenated input (FR-07 ... FR-13)."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.table = build_table(settings)
        self.identity = not (settings.show_nonprinting or settings.show_tabs)
        # -E without -v must hold back a CR at the end of a chunk until the next byte is known.
        self.defer_cr = settings.show_ends and not settings.show_nonprinting
        self.end_marker = b"$\n" if settings.show_ends else b"\n"
        self.line_number = 0
        self.at_line_start = True   # no byte of the current line has been seen yet
        self.previous_blank = False  # the last complete line was empty
        self.pending_cr = False      # a deferred CR that is the latest byte of the stream

    def _render(self, data: bytes) -> bytes:
        if self.identity:
            return data
        table = self.table
        return b"".join(table[value] for value in data)

    def _line_number(self) -> bytes:
        self.line_number += 1
        return f"{self.line_number:>6}\t".encode("ascii")

    def _segment(self, segment: bytes, terminated: bool, output: list[bytes]) -> None:
        """Handle the bytes of one line that lie in the current chunk.

        ``segment`` holds content bytes only; ``terminated`` says whether an LF follows it.
        """
        settings = self.settings
        if self.at_line_start:
            if not segment:
                if not terminated:
                    return
                # A complete empty line (FR-08, FR-09, FR-10).
                if settings.squeeze_blank and self.previous_blank:
                    return
                self.previous_blank = True
                if settings.number and not settings.number_nonblank:
                    output.append(self._line_number())
                output.append(self.end_marker)
                return
            if settings.number or settings.number_nonblank:
                output.append(self._line_number())
            self.at_line_start = False
        if self.pending_cr:
            self.pending_cr = False
            # A CR directly before LF is shown as ^M under -E (FR-13); otherwise it is data.
            output.append(b"^M" if terminated and not segment else CR)
        if self.defer_cr and segment.endswith(CR):
            output.append(self._render(segment[:-1]))
            if terminated:
                output.append(b"^M")
            else:
                self.pending_cr = True
        else:
            output.append(self._render(segment))
        if terminated:
            output.append(self.end_marker)
            self.at_line_start = True
            self.previous_blank = False

    def feed(self, chunk: bytes) -> bytes:
        if not self.settings.transforms:
            return chunk
        output: list[bytes] = []
        segments = chunk.split(b"\n")
        for segment in segments[:-1]:
            self._segment(segment, True, output)
        self._segment(segments[-1], False, output)
        return b"".join(output)

    def finish(self) -> bytes:
        """Bytes still owed at the end of the whole stream (a deferred, unterminated CR)."""
        if self.pending_cr:
            self.pending_cr = False
            return CR
        return b""


def emit(data: bytes) -> None:
    """Write and flush at once (NFR-04, FR-17).

    A failing write raises OSError, which common.run reports as ``write error`` (FR-16), or
    BrokenPipeError, which it handles silently (CONV-25).
    """
    if data:
        write(data)
        out.flush()


def copy_operand(path: str, formatter: Formatter) -> bool:
    """Copy one operand through the formatter; report failures per CONV-16 (FR-14, FR-15)."""
    try:
        stream = open_input(path)
    except OSError as error:
        file_failure(TOOL, path, error)
        return False
    try:
        while True:
            try:
                chunk = stream.read1(BUFFER_SIZE)
            except OSError as error:
                file_failure(TOOL, path, error)
                return False
            if not chunk:
                return True
            emit(formatter.feed(chunk))
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()


def settings_from(values: dict[str, object]) -> Settings:
    show_all = bool(values.get("show_all"))
    return Settings(
        number=bool(values.get("number")),
        number_nonblank=bool(values.get("number_nonblank")),
        squeeze_blank=bool(values.get("squeeze_blank")),
        show_nonprinting=show_all or bool(values.get("show_nonprinting")),
        show_ends=show_all or bool(values.get("show_ends")),
        show_tabs=show_all or bool(values.get("show_tabs")),
    )


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
    except UsageError as error:
        return usage_failure(TOOL, error)
    if handle_action(TOOL, parsed, HELP_TEXT):
        return 0
    formatter = Formatter(settings_from(parsed.values))
    status = 0
    for path in parsed.operands or ["-"]:
        if not copy_operand(path, formatter):
            status = 1
    emit(formatter.finish())
    return status

"""Reference implementation of dp-wc (projects/04-wc/specs/SRS.md).

Counting is streamed in fixed-size chunks so memory does not grow with input size. Character
counting uses an incremental UTF-8 decoder: a multibyte sequence split across two chunks is held
back until it is complete, and every byte that is not part of a well-formed sequence (SRS FR-06)
counts as one character. With ``errors="surrogateescape"`` Python's decoder maps each such byte
to exactly one lone surrogate, which yields that rule directly.
"""

from __future__ import annotations

import codecs
from dataclasses import dataclass
from typing import BinaryIO

from .common import (
    Option,
    UsageError,
    encode_arg,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    usage_failure,
    write,
)

TOOL = "dp-wc"
CHUNK_SIZE = 64 * 1024
HELP_TEXT = """\
Usage: dp-wc [OPTION]... [FILE]...
Print line, word, character, and byte counts for each FILE, and a total line
if more than one FILE is given.

With no FILE, read standard input.  The FILE '-' also means standard input.
A word is a maximal run of bytes other than space, tab, LF, VT, FF, and CR.
Characters are UTF-8 code points; each byte of an invalid sequence counts as
one character.  Counts are printed in the order lines, words, characters,
bytes, maximum line length.  With no option, -l -w -c is assumed.

Options:
  -l, --lines             print the line (LF) counts
  -w, --words             print the word counts
  -m, --chars             print the character counts
  -c, --bytes             print the byte counts
  -L, --max-line-length   print the maximum line length in characters
      --help              display this help and exit
      --version           output version information and exit
"""

# Column order is fixed (SRS FR-02) regardless of the order options are given in.
COLUMNS = ("lines", "words", "chars", "bytes", "max_line_length")
OPTIONS = [
    Option("lines", short="l", long="lines"),
    Option("words", short="w", long="words"),
    Option("chars", short="m", long="chars"),
    Option("bytes", short="c", long="bytes"),
    Option("max_line_length", short="L", long="max-line-length"),
]
DEFAULT_COLUMNS = ("lines", "words", "bytes")


@dataclass
class Counts:
    lines: int = 0
    words: int = 0
    chars: int = 0
    bytes: int = 0
    max_line_length: int = 0

    def add(self, other: Counts) -> None:
        """Accumulate into a total: sums, except max line length which takes the maximum."""
        self.lines += other.lines
        self.words += other.words
        self.chars += other.chars
        self.bytes += other.bytes
        self.max_line_length = max(self.max_line_length, other.max_line_length)

    def select(self, columns: tuple[str, ...]) -> list[int]:
        return [getattr(self, name) for name in columns]


class Counter:
    """Streaming counter: feed chunks of any size, then call :meth:`finish`."""

    def __init__(self) -> None:
        self.counts = Counts()
        self._in_word = False
        self._line_length = 0
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="surrogateescape")

    def feed(self, chunk: bytes) -> None:
        if not chunk:
            return
        counts = self.counts
        counts.bytes += len(chunk)
        counts.lines += chunk.count(b"\n")
        # bytes.split() with no argument splits on exactly b" \t\n\v\f\r" (SRS FR-05).
        words = len(chunk.split())
        if words and self._in_word and not chunk[:1].isspace():
            words -= 1  # the first run continues a word begun in the previous chunk
        counts.words += words
        self._in_word = not chunk[-1:].isspace()
        self._count_text(self._decoder.decode(chunk))

    def finish(self) -> Counts:
        self._count_text(self._decoder.decode(b"", final=True))
        self.counts.max_line_length = max(
            self.counts.max_line_length, self._line_length
        )
        return self.counts

    def _count_text(self, text: str) -> None:
        if not text:
            return
        self.counts.chars += len(text)
        segments = text.split("\n")
        self._line_length += len(segments[0])
        for segment in segments[1:]:
            self.counts.max_line_length = max(
                self.counts.max_line_length, self._line_length
            )
            self._line_length = len(segment)


def count_stream(stream: BinaryIO, chunk_size: int = CHUNK_SIZE) -> Counts:
    counter = Counter()
    while chunk := stream.read(chunk_size):
        counter.feed(chunk)
    return counter.finish()


def count_bytes(data: bytes, chunk_size: int = CHUNK_SIZE) -> Counts:
    """Count an in-memory buffer by feeding it in ``chunk_size`` pieces (for self-checks)."""
    counter = Counter()
    for start in range(0, len(data), chunk_size):
        counter.feed(data[start : start + chunk_size])
    return counter.finish()


def format_report(rows: list[tuple[list[int], bytes | None]]) -> bytes:
    """Right-align every number to the digit count of the largest value printed (FR-09)."""
    width = max((len(str(value)) for values, _ in rows for value in values), default=1)
    lines = []
    for values, name in rows:
        line = b" ".join(str(value).rjust(width).encode("ascii") for value in values)
        if name is not None:
            line += b" " + name
        lines.append(line + b"\n")
    return b"".join(lines)


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
    except UsageError as error:
        return usage_failure(TOOL, error)

    columns = (
        tuple(name for name in COLUMNS if parsed.values.get(name)) or DEFAULT_COLUMNS
    )
    operands: list[str | None] = list(parsed.operands) or [
        None
    ]  # None = implicit stdin
    rows: list[tuple[list[int], bytes | None]] = []
    total = Counts()
    stdin_consumed = False
    status = 0

    for operand in operands:
        path = "-" if operand is None else operand
        if path == "-" and stdin_consumed:
            counts = Counts()  # FR-12: stdin is read to EOF only once
        else:
            try:
                stream = open_input(path)
                try:
                    counts = count_stream(stream)
                finally:
                    if path != "-":
                        stream.close()
            except OSError as error:
                file_failure(TOOL, path, error)
                status = 1
                continue
            finally:
                if path == "-":
                    stdin_consumed = True
        total.add(counts)
        rows.append(
            (counts.select(columns), None if operand is None else encode_arg(operand))
        )

    if len(operands) > 1:
        rows.append((total.select(columns), b"total"))
    write(format_report(rows))
    return status

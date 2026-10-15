"""Reference implementation of dp-page (projects/36-page/specs/SRS.md).

The inputs are one continuous byte stream, copied in fixed-size chunks so that memory does
not grow with the input size or the line length. A page header is written only when the
first byte of the page's first line is known to exist, so no empty page is ever produced.
"""

from __future__ import annotations

from typing import BinaryIO

from . import common
from .common import (
    INT64_MAX,
    Option,
    UsageError,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    parse_count,
    usage_failure,
)

TOOL = "dp-page"
CHUNK_SIZE = 64 * 1024
DEFAULT_LINES = 52
FORM_FEED = b"\x0c"
HELP_TEXT = """\
Usage: dp-page [OPTION]... [FILE]...
Break the concatenation of the FILEs into numbered pages for printing.

With no FILE, or when FILE is -, read standard input.  Each page starts with
the header line 'Page     N' (five spaces before the page number) and a blank
line, holds the next 52 input lines exactly as read, and ends with a form
feed character.  A last line without a newline is copied without one.  No
page is written for an empty input.

Options:
  -l, --lines=N   put N input lines on each page instead of 52
                    (1 to 9223372036854775807)
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS = [Option("lines", short="l", long="lines", takes_value=True)]


class Paginator:
    """Copies bytes, inserting a header before each page and a form feed after it."""

    def __init__(self, page_length: int):
        self.page_length = page_length
        self.page_number = 0
        self.lines_on_page = 0
        self.page_open = False

    def feed(self, data: bytes) -> None:
        start = 0
        while start < len(data):
            if not self.page_open:
                self.page_number += 1
                self.page_open = True
                self.lines_on_page = 0
                common.write(f"Page     {self.page_number}\n\n".encode())
            newline = data.find(b"\n", start)
            if newline < 0:
                common.write(data[start:])
                return
            common.write(data[start : newline + 1])
            start = newline + 1
            self.lines_on_page += 1
            if self.lines_on_page == self.page_length:
                common.write(FORM_FEED)
                self.page_open = False

    def finish(self) -> None:
        if self.page_open:
            common.write(FORM_FEED)
            self.page_open = False


def copy(handle: BinaryIO, paginator: Paginator) -> None:
    while True:
        chunk = handle.read(CHUNK_SIZE)
        if not chunk:
            return
        paginator.feed(chunk)


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        page_length = DEFAULT_LINES
        if "lines" in parsed.values:
            page_length = parse_count(
                str(parsed.values["lines"]), parsed.spelled["lines"], 1, INT64_MAX
            )
    except UsageError as error:
        return usage_failure(TOOL, error)

    paginator = Paginator(page_length)
    status = 0
    for operand in parsed.operands or ["-"]:
        try:
            handle = open_input(operand)
        except OSError as error:
            file_failure(TOOL, operand, error)
            status = 1
            continue
        try:
            copy(handle, paginator)
        except OSError as error:
            file_failure(TOOL, operand, error)
            status = 1
        finally:
            if operand != "-":
                handle.close()
    paginator.finish()
    return status

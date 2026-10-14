"""Reference implementation of dp-sort-child (projects/34-parallel-sort/specs/SRS.md)."""

from __future__ import annotations

from . import common
from ._parallel_sort_worker import read_request, reply_lines, selection_sort
from .common import (DataError, InputError, Option, UsageError, data_failure, file_failure,
                     handle_action, open_input, parse_args, usage_failure)

TOOL = "dp-sort-child"
HELP_TEXT = """\
Usage: dp-sort-child [OPTION]... [FILE]
Serve one sort request: read a count and that many integers, and write them
sorted in non-decreasing order, one per line.

With no FILE, or when FILE is -, read standard input.  The count (0-100000)
and the integers are separated by whitespace.  Input after the last integer
is not read.  This is the worker of dp-sort-host.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        values = read_request(handle, source)
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as error:
        file_failure(TOOL, source, error.error)
        return 1
    finally:
        if source != "-":
            handle.close()
    selection_sort(values)
    common.write(b"".join(reply_lines(values)))
    return 0

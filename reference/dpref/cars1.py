"""Reference implementation of dp-cars1 (projects/26-cars/specs/SRS.md).

The input is read one token at a time, so the tool can be used interactively; the report is
written only after the day's input is complete. The dialog and the report live in _cars.py,
which dp-cars2 (Project 28) shares.
"""

from __future__ import annotations

import sys

from ._cars import read_day, render_report
from .common import (PROMPT, DataError, InputError, InputStream, UsageError, data_failure,
                     file_failure, handle_action, open_input, parse_args, usage_failure,
                     write)

TOOL = "dp-cars1"
HELP_TEXT = """\
Usage: dp-cars1 [OPTION]... [FILE]
Record one day of car sales for 12 brands and print the daily report.

Read whitespace-separated whole numbers from FILE, or from standard input when
FILE is absent or -: first the opening stock of brands 0 to 11 (0-999999
each), then each sale as a brand and a quantity, until a negative brand or the
end of the input.  A sale of an unknown brand, of a negative quantity, or of
more cars than are left in stock is reported and not recorded.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
"""


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        stream = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        stock, sales, rejected = read_day(InputStream(stream), source,
                                          bool(parsed.values.get("prompt")), TOOL)
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    write(render_report(stock, sales))
    return 1 if rejected else 0

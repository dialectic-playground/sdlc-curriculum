"""Reference implementation of dp-cars2 (projects/28-cars-modular/specs/SRS.md).

Without --totals and --save it behaves exactly like dp-cars1 (SRS-28 FR-01): both tools use
the dialog and the report of _cars.py. --totals feeds saved totals straight into the report
component, and --save writes the totals that the report was rendered from.
"""

from __future__ import annotations

import os
import sys

from ._cars import BRANDS, MAX_STOCK, read_day, render_report
from .common import (PROMPT, DataError, InputError, InputStream, Option, UsageError,
                     data_failure, file_failure, handle_action, invalid_argument, open_input,
                     out, parse_args, parse_int_token, read_all, strip_eof_marker, tokenize,
                     unexpected_end, usage_failure, write)

TOOL = "dp-cars2"
HELP_TEXT = """\
Usage: dp-cars2 [OPTION]... [FILE]
Record one day of car sales for 12 brands and print the daily report.

Read whitespace-separated whole numbers from FILE, or from standard input when
FILE is absent or -: first the opening stock of brands 0 to 11 (0-999999
each), then each sale as a brand and a quantity, until a negative brand or the
end of the input.  A sale of an unknown brand, of a negative quantity, or of
more cars than are left in stock is reported and not recorded.

With --totals, read the day's totals instead: for each brand from 0 to 11, its
opening stock and the number of cars sold, as written by --save.

Options:
  -p, --prompt       write prompts to standard error before reading (ignored
                       with --totals)
  -s, --save=FILE    after the report, write the day's totals to FILE
  -t, --totals       read the day's totals instead of the stock and the sales
      --help         display this help and exit
      --version      output version information and exit
"""
OPTIONS = [PROMPT, Option("save", short="s", long="save", takes_value=True),
           Option("totals", short="t", long="totals")]


def read_totals(data: bytes, source: str) -> tuple[list[int], list[int]]:
    """Exactly 12 pairs (opening stock, cars sold), validated in input order."""
    data = strip_eof_marker(data)
    tokens = tokenize(data)
    stock: list[int] = []
    sales: list[int] = []
    for brand in range(BRANDS):
        if len(tokens) <= 2 * brand:
            raise unexpected_end(source, data)
        stock.append(parse_int_token(tokens[2 * brand], source, 0, MAX_STOCK))
        if len(tokens) <= 2 * brand + 1:
            raise unexpected_end(source, data)
        sales.append(parse_int_token(tokens[2 * brand + 1], source, 0, stock[brand]))
    if len(tokens) > 2 * BRANDS:
        extra = tokens[2 * BRANDS]
        raise DataError(source, extra.line, b"extra data '" + extra.text + b"'")
    return stock, sales


def render_totals(stock: list[int], sales: list[int]) -> bytes:
    return "".join(f"{start} {sold}\n" for start, sold in zip(stock, sales)).encode()


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        save = parsed.values.get("save")
        if save is not None and save in ("", "-"):
            raise invalid_argument(str(save), parsed.spelled["save"])
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    rejected = False
    try:
        if parsed.values.get("totals"):
            stock, sales = read_totals(read_all(source), source)
        else:
            stream = open_input(source)
            try:
                stock, sales, rejected = read_day(InputStream(stream), source,
                                                  bool(parsed.values.get("prompt")), TOOL)
            finally:
                if stream is not sys.stdin.buffer:
                    stream.close()
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    write(render_report(stock, sales))
    if save is not None:
        out.flush()
        path = str(save)
        try:
            if os.path.isdir(path):
                raise IsADirectoryError(path)
            with open(path, "wb") as handle:
                handle.write(render_totals(stock, sales))
        except OSError as error:
            file_failure(TOOL, path, error)
            return 1
    return 1 if rejected else 0

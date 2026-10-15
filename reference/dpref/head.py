"""Reference implementation of dp-head (projects/03-head-tail/specs/SRS.md)."""

from __future__ import annotations

from collections import deque

from . import _headtail_common as ht
from .common import Option, UsageError, handle_action, parse_args, usage_failure, write

TOOL = "dp-head"
DEFAULT_LINES = 10
HELP_TEXT = """\
Usage: dp-head [OPTION]... [FILE]...
Print the first 10 lines of each FILE to standard output.

With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

NUM is a decimal integer with an optional multiplier suffix:
K (1024), M (1024*1024), or G (1024*1024*1024).

Options:
  -c, --bytes=[-]NUM    print the first NUM bytes of each file;
                          with a leading '-', print all but the last NUM bytes
  -n, --lines=[-]NUM    print the first NUM lines instead of the first 10;
                          with a leading '-', print all but the last NUM lines
  -q, --quiet           never print headers giving file names
  -v, --verbose         always print headers giving file names
      --help            display this help and exit
      --version         output version information and exit
"""

# -n/-c share one destination, as do -q/-v, so the last one written wins (SRS FR-03, FR-05).
OPTIONS = [
    Option("amount", short="c", long="bytes", takes_value=True),
    Option("amount", short="n", long="lines", takes_value=True),
    Option("headers", short="q", long="quiet"),
    Option("headers", short="v", long="verbose"),
]


def head_all_but_last_bytes(stream, count: int) -> None:
    region = ht.regular_region(stream)
    if region is not None:
        start, size = region
        ht.copy_count(stream, max(0, size - start - count))
        return
    window = bytearray()  # never holds more than count + one block
    for block in ht.blocks(stream):
        window += block
        if len(window) > count:
            surplus = len(window) - count
            write(bytes(window[:surplus]))
            del window[:surplus]


def head_all_but_last_lines(stream, count: int) -> None:
    if count == 0:
        ht.copy_rest(stream)
        return
    region = ht.regular_region(stream)
    if region is not None:
        start, size = region
        stop = ht.last_lines_offset(stream, start, size, count)
        stream.seek(start)
        ht.copy_count(stream, stop - start)
        return
    window: deque[bytes] = (
        deque()
    )  # the most recent `count` lines, not yet known to print
    for line in ht.split_lines(stream):
        window.append(line)
        if len(window) > count:
            write(window.popleft())


def slice_head(stream, amount: ht.Amount) -> None:
    if amount.lines:
        if amount.sign == "-":
            head_all_but_last_lines(stream, amount.count)
        else:
            ht.copy_lines(stream, amount.count)
    elif amount.sign == "-":
        head_all_but_last_bytes(stream, amount.count)
    else:
        ht.copy_count(stream, amount.count)


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        amount = ht.Amount("", DEFAULT_LINES, True)
        if "amount" in parsed.values:
            amount = ht.parse_amount(
                str(parsed.values["amount"]), parsed.spelled["amount"], signs="-"
            )
    except UsageError as error:
        return usage_failure(TOOL, error)

    operands = parsed.operands
    headers = ht.HeaderWriter(
        ht.headers_wanted(parsed.spelled.get("headers"), max(1, len(operands)))
    )
    ok = ht.process_operands(
        TOOL, operands, headers, lambda item: slice_head(item.stream, amount)
    )
    return 0 if ok else 1

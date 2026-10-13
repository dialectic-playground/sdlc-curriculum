"""Reference implementation of dp-tail (projects/03-head-tail/specs/SRS.md)."""

from __future__ import annotations

import os
import re
import time
from collections import deque

from . import _headtail_common as ht
from .common import (Option, UsageError, diagnose, handle_action, invalid_argument, out,
                     parse_args, parse_count, usage_failure, write)

TOOL = "dp-tail"
DEFAULT_LINES = 10
DEFAULT_SLEEP = 1.0
MAX_SLEEP = 86400
SECONDS_PATTERN = re.compile(r"[0-9]+(\.[0-9]+)?")
HELP_TEXT = """\
Usage: dp-tail [OPTION]... [FILE]...
Print the last 10 lines of each FILE to standard output.

With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

NUM is a decimal integer with an optional multiplier suffix:
K (1024), M (1024*1024), or G (1024*1024*1024).

Options:
  -c, --bytes=[+]NUM    output the last NUM bytes;
                          or use -c +NUM to output starting with byte NUM
  -n, --lines=[+]NUM    output the last NUM lines, instead of the last 10;
                          or use -n +NUM to output starting with line NUM
  -f, --follow          output appended data as regular files grow
  -s, --sleep-interval=SECONDS
                        with -f, wait SECONDS between polls
                          (default 1, at most 86400)
      --max-polls=N     with -f, stop after N polls instead of running forever
  -q, --quiet           never print headers giving file names
  -v, --verbose         always print headers giving file names
      --help            display this help and exit
      --version         output version information and exit
"""

# -n/-c share one destination, as do -q/-v, so the last one written wins (SRS FR-03, FR-05).
OPTIONS = [
    Option("amount", short="c", long="bytes", takes_value=True),
    Option("amount", short="n", long="lines", takes_value=True),
    Option("follow", short="f", long="follow"),
    Option("sleep", short="s", long="sleep-interval", takes_value=True),
    Option("max_polls", long="max-polls", takes_value=True),
    Option("headers", short="q", long="quiet"),
    Option("headers", short="v", long="verbose"),
]


def parse_seconds(value: str, spelled: str) -> float:
    if not SECONDS_PATTERN.fullmatch(value) or float(value) > MAX_SLEEP:
        raise invalid_argument(value, spelled)
    return float(value)


# --- initial output ----------------------------------------------------------------------

def tail_bytes(stream, count: int) -> None:
    region = ht.regular_region(stream)
    if region is not None:
        start, size = region
        stream.seek(max(start, size - count))
        ht.copy_rest(stream)
        return
    window = bytearray()  # bounded ring: at most count + one block
    for block in ht.blocks(stream):
        window += block
        if len(window) > count:
            del window[:len(window) - count]
    write(bytes(window))


def tail_lines(stream, count: int) -> None:
    region = ht.regular_region(stream)
    if region is not None:
        start, size = region
        stream.seek(ht.last_lines_offset(stream, start, size, count))
        ht.copy_rest(stream)
        return
    if count == 0:
        for _ in ht.blocks(stream):
            pass
        return
    window: deque[bytes] = deque(maxlen=count)  # bounded ring of the last `count` lines
    window.extend(ht.split_lines(stream))
    write(b"".join(window))


def slice_tail(stream, amount: ht.Amount) -> None:
    start_at = max(amount.count, 1) - 1  # +0 and +1 both mean "from the beginning"
    if amount.lines:
        if amount.sign == "+":
            ht.skip_lines(stream, start_at)
        else:
            tail_lines(stream, amount.count)
    elif amount.sign == "+":
        ht.skip_count(stream, start_at)
        ht.copy_rest(stream)
    else:
        tail_bytes(stream, amount.count)


# --- follow mode -------------------------------------------------------------------------

def poll_once(followed: list[ht.Input], headers: ht.HeaderWriter) -> bool:
    """Output whatever was appended to each followed file; drop files that fail."""
    ok = True
    for item in list(followed):
        try:
            size = os.fstat(item.stream.fileno()).st_size
            if size < item.position:
                diagnose(TOOL, f"{item.name}: file truncated")
                item.position = 0
            if size > item.position:
                item.stream.seek(item.position)
                first = True
                for block in ht.blocks(item.stream):
                    if first and headers.last is not item:
                        headers.emit(item.name, item)
                    first = False
                    write(block)
                item.position = item.stream.tell()
        except BrokenPipeError:
            raise
        except OSError as error:
            ht.report(TOOL, item.operand, error)
            followed.remove(item)
            item.stream.close()
            ok = False
    return ok


def follow(followed: list[ht.Input], headers: ht.HeaderWriter, interval: float,
           max_polls: int | None) -> bool:
    ok = True
    polls = 0
    while followed and (max_polls is None or polls < max_polls):
        out.flush()
        time.sleep(interval)
        polls += 1
        ok = poll_once(followed, headers) and ok
    for item in followed:
        item.stream.close()
    return ok


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        amount = ht.Amount("", DEFAULT_LINES, True)
        if "amount" in parsed.values:
            amount = ht.parse_amount(str(parsed.values["amount"]), parsed.spelled["amount"],
                                     signs="+-")
        interval = DEFAULT_SLEEP
        if "sleep" in parsed.values:
            interval = parse_seconds(str(parsed.values["sleep"]), parsed.spelled["sleep"])
        max_polls = None
        if "max_polls" in parsed.values:
            max_polls = parse_count(str(parsed.values["max_polls"]),
                                    parsed.spelled["max_polls"], maximum=ht.MAX_AMOUNT)
    except UsageError as error:
        return usage_failure(TOOL, error)

    following = bool(parsed.values.get("follow"))
    operands = parsed.operands
    headers = ht.HeaderWriter(ht.headers_wanted(parsed.spelled.get("headers"),
                                                max(1, len(operands))))
    followed: list[ht.Input] = []

    def handle(item: ht.Input) -> None:
        slice_tail(item.stream, amount)
        if following and item.operand != "-" and ht.regular_region(item.stream) is not None:
            item.keep_open = True
            item.position = item.stream.tell()
            followed.append(item)

    ok = ht.process_operands(TOOL, operands, headers, handle)
    if following:
        ok = follow(followed, headers, interval, max_polls) and ok
    return 0 if ok else 1

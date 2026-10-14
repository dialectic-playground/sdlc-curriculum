"""Reference implementation of dp-assert-sort (projects/49-assert-sort/specs/SRS.md).

Selection sort instrumented with a bounds assertion and the loop invariant
sorted(a, i, n) checked after every pass; --fault corrupts one step of a pass so that the
checks can be seen to fire.
"""

from __future__ import annotations

import re

from . import common
from .common import (DataError, Option, UsageError, data_failure, file_failure, handle_action,
                     invalid_argument, parse_args, parse_int_token, read_all, strip_eof_marker,
                     tokenize, usage_failure, INT64_MAX)

TOOL = "dp-assert-sort"
HELP_TEXT = """\
Usage: dp-assert-sort [OPTION]... [FILE]
Sort integers by selection sort, checking assertions after every pass.

With no FILE, or when FILE is -, read standard input.  The input is a list of
whole numbers separated by whitespace.  After each pass i the tool asserts
that the index of the minimum is within the array and that a[0..i] is sorted
with every later element at least a[i].  The sorted numbers are written one
per line.  A failed assertion is reported and the exit status is 1.

FAULT is KIND or KIND:PASS, where KIND is skip-swap (omit the swap),
off-by-one (use the index after the minimum), or search-from-next (start the
search for the minimum at i+1).  The fault is injected in pass PASS (counted
from 0), or in every pass when PASS is omitted.

Options:
  -t, --trace        write one line to standard error for every invariant check
                       that holds
  -f, --fault=FAULT  inject the fault FAULT into the sort
      --help         display this help and exit
      --version      output version information and exit
"""

OPTIONS: list[Option] = [
    Option("trace", short="t", long="trace"),
    Option("fault", short="f", long="fault", takes_value=True),
]
KINDS = ("skip-swap", "off-by-one", "search-from-next")
_FAULT = re.compile(r"(?P<kind>[a-z-]+)(?::(?P<pass>[0-9]+))?\Z")


class AssertionFailure(Exception):
    """A failed assertion; ``str(error)`` is the diagnostic without the tool prefix."""


def parse_fault(value: str, spelled: str) -> tuple[str, int | None]:
    match = _FAULT.match(value)
    if match is None or match["kind"] not in KINDS:
        raise invalid_argument(value, spelled)
    if match["pass"] is None:
        return match["kind"], None
    number = int(match["pass"])
    if number > INT64_MAX:
        raise invalid_argument(value, spelled)
    return match["kind"], number


def check_invariant(a: list[int], i: int) -> str | None:
    """sorted(a, i, n): return None when it holds, else the detail of the first violation."""
    for k in range(1, i + 1):
        if a[k - 1] > a[k]:
            return f"a[{k - 1}] = {a[k - 1]} > a[{k}] = {a[k]}"
    for j in range(i + 1, len(a)):
        if a[j] < a[i]:
            return f"a[{j}] = {a[j]} < a[{i}] = {a[i]}"
    return None


def selection_sort(a: list[int], trace: bool, fault: tuple[str, int | None] | None) -> None:
    n = len(a)
    for i in range(n - 1):
        kind = None
        if fault is not None and (fault[1] is None or fault[1] == i):
            kind = fault[0]
        start = i + 1 if kind == "search-from-next" else i
        min_ind = start
        for j in range(start + 1, n):
            if a[j] < a[min_ind]:
                min_ind = j
        if kind == "off-by-one":
            min_ind += 1
        if not (0 <= min_ind < n):
            raise AssertionFailure(f"assertion failed in pass {i}: min_ind >= 0 && min_ind < n"
                                   f" (min_ind = {min_ind}, n = {n})")
        if kind != "skip-swap":
            a[i], a[min_ind] = a[min_ind], a[i]
        detail = check_invariant(a, i)
        if detail is not None:
            raise AssertionFailure(f"assertion failed in pass {i}: sorted(a, {i}, {n})"
                                   f" ({detail})")
        if trace:
            values = " ".join(str(v) for v in a)
            common.err.write(f"pass {i}: min_ind = {min_ind} in bounds; a = {values};"
                             f" sorted(a, {i}, {n}) holds\n".encode())


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        fault = None
        if "fault" in parsed.values:
            fault = parse_fault(str(parsed.values["fault"]), parsed.spelled["fault"])
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        data = strip_eof_marker(read_all(source))
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        a = [parse_int_token(token, source) for token in tokenize(data)]
    except DataError as error:
        return data_failure(TOOL, error)
    try:
        selection_sort(a, bool(parsed.values.get("trace")), fault)
    except AssertionFailure as failure:
        common.diagnose(TOOL, str(failure))
        return 1
    common.write("".join(f"{v}\n" for v in a).encode())
    return 0

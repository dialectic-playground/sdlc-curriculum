"""Reference implementation of dp-chk-sort (projects/17-stream-filters/specs/SRS.md).

Integers are read one token at a time; reading stops at the first inversion, so nothing after
it is read or validated. The answer is also the exit status (0 sorted, 1 not sorted), and every
failure exits with status 2, like ``sort -c`` (SRS-17 section 3.7).
"""

from __future__ import annotations

from . import common
from .common import (
    DataError,
    InputError,
    InputStream,
    Option,
    UsageError,
    data_failure,
    diagnose,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    parse_int_token,
    usage_failure,
)

TOOL = "dp-chk-sort"
TROUBLE = 2
HELP_TEXT = """\
Usage: dp-chk-sort [OPTION]... [FILE]
Check whether the integers in FILE are in non-decreasing order.

With no FILE, or when FILE is -, read standard input.  Integers are separated
by whitespace.  Print 'file is sorted' and exit with status 0 if no integer
is less than the one before it; otherwise print 'file is not sorted' as soon
as the first such integer is read, stop reading, and exit with status 1.
Any error exits with status 2.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def check(handle, source: str) -> bool:
    """True if the tokens are non-decreasing; stops at the first inversion."""
    previous = None
    stream = InputStream(handle)
    while (token := stream.token()) is not None:
        value = parse_int_token(token, source)
        if previous is not None and value < previous:
            return False
        previous = value
    return True


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
        return TROUBLE
    try:
        in_order = check(handle, source)
    except DataError as error:
        data_failure(TOOL, error)
        return TROUBLE
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return TROUBLE
    finally:
        if source != "-":
            handle.close()

    try:
        common.write(b"file is sorted\n" if in_order else b"file is not sorted\n")
        common.out.flush()
    except BrokenPipeError:
        raise
    except OSError:
        common._silence_stdout()  # the buffered bytes now go to the null device
        diagnose(TOOL, "write error")
        return TROUBLE
    return 0 if in_order else 1

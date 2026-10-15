"""Reference implementation of dp-divide (projects/50-fault-recovery/specs/SRS.md).

Pairs of reals are tokenized incrementally (CONV-32), so each quotient is written, and
standard output flushed, as soon as its pair is complete. An arithmetic fault (zero divisor
or a quotient that overflows) is raised by the division routine and caught by the recovery
point in main(), which writes the two recovery lines and ends the run with status 0.
"""

from __future__ import annotations

import math

from . import common
from .common import (
    PROMPT,
    DataError,
    InputError,
    InputStream,
    Option,
    UsageError,
    data_failure,
    file_failure,
    fix,
    handle_action,
    open_input,
    parse_args,
    parse_real_token,
    prompt,
    usage_failure,
)

TOOL = "dp-divide"
PROMPT_TEXT = "Two floats: "
SIGNAL_STATUS = 8
HELP_TEXT = """\
Usage: dp-divide [OPTION]... [FILE]
Divide pairs of numbers, recovering from an arithmetic fault.

With no FILE, or when FILE is -, read standard input.  The input is a list of
real numbers separated by whitespace, taken two at a time.  For each pair
a b the line 'a / b == q' is written, with six digits after the decimal
point.  A zero divisor, or a quotient too large to represent, is a fault: the
tool writes 'Signal status == 8.' and 'At jump point and about to exit...',
ignores the rest of the input, and exits with status 0.

Options:
  -p, --prompt    write the prompt 'Two floats: ' to standard error before
                    each pair is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]


class ArithmeticFault(Exception):
    """Raised by divide(); carries the signal status written by the recovery point."""

    def __init__(self, status: int):
        super().__init__(status)
        self.status = status


def divide(dividend: float, divisor: float) -> float:
    if divisor == 0.0:
        raise ArithmeticFault(SIGNAL_STATUS)
    quotient = dividend / divisor
    if math.isinf(quotient):
        raise ArithmeticFault(SIGNAL_STATUS)
    return quotient


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
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        stream = InputStream(handle)
        while True:
            prompt(prompting, PROMPT_TEXT)
            first = stream.token()
            if first is None:
                return 0
            dividend = parse_real_token(first, source)
            second = stream.require(source)
            divisor = parse_real_token(second, source)
            try:
                quotient = divide(dividend, divisor)
            except ArithmeticFault as fault:  # the recovery point
                common.write(
                    f"Signal status == {fault.status}.\n"
                    "At jump point and about to exit...\n".encode()
                )
                common.out.flush()
                return 0
            common.write(
                f"{fix(dividend, 6)} / {fix(divisor, 6)} == {fix(quotient, 6)}\n".encode()
            )
            common.out.flush()
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if source != "-":
            handle.close()

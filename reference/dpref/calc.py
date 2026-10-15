"""Reference implementation of dp-calc (projects/37-calc/specs/SRS.md).

Input is read one line at a time, so each result is written (and standard output flushed)
before the next line is read: the tool works interactively. A line is evaluated left to right
on a copy of the accumulator, which is committed only when the whole line is valid.
"""

from __future__ import annotations

from . import common
from .common import (
    INT64_MAX,
    INT64_MIN,
    PROMPT,
    WHITESPACE,
    InputError,
    InputStream,
    Option,
    UsageError,
    encode_arg,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    prompt,
    usage_failure,
)

TOOL = "dp-calc"
BANNER = b" **** End of Calculation ****\n"
STOP = b"!"
OPERATORS = (b"+", b"-", b"*", b"/", b"%")
HELP_TEXT = """\
Usage: dp-calc [OPTION]... [FILE]
Evaluate lines of operator-operand pairs left to right on an accumulator.

With no FILE, or when FILE is -, read standard input.  The accumulator starts
at 0.  Each line holds pairs such as '+ 10 * 3', separated by whitespace; the
operators are + - * / % and the operands are whole numbers.  Each pair is
applied in turn, without precedence, and a valid line prints
'OLD LINE == NEW'.  Division truncates toward zero.  A line with an error is
reported and leaves the accumulator unchanged.  The operator ! ends the
calculation.

Options:
  -p, --prompt    write the accumulator and a space to standard error before
                    each line is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]


class LineError(Exception):
    """A rejected line; the message is the CONV-34 message part (bytes)."""

    def __init__(self, message: bytes):
        super().__init__(message)
        self.message = message


def split_tokens(line: bytes) -> list[bytes]:
    tokens: list[bytes] = []
    current = bytearray()
    for byte in line:
        if byte in WHITESPACE:
            if current:
                tokens.append(bytes(current))
                current.clear()
        else:
            current.append(byte)
    if current:
        tokens.append(bytes(current))
    return tokens


def parse_operand(token: bytes) -> int:
    body = token[1:] if token[:1] in (b"+", b"-") else token
    if body and all(0x30 <= b <= 0x39 for b in body):
        value = int(token)
        if INT64_MIN <= value <= INT64_MAX:
            return value
    raise LineError(b"invalid integer '" + token + b"'")


def apply(accumulator: int, operator: bytes, operand: int) -> int:
    if operator in (b"/", b"%") and operand == 0:
        raise LineError(b"division by zero")
    if operator == b"+":
        result = accumulator + operand
    elif operator == b"-":
        result = accumulator - operand
    elif operator == b"*":
        result = accumulator * operand
    else:
        quotient = abs(accumulator) // abs(operand)
        if (accumulator < 0) != (operand < 0):
            quotient = -quotient
        result = quotient if operator == b"/" else accumulator - operand * quotient
    if not INT64_MIN <= result <= INT64_MAX:
        raise LineError(b"integer overflow")
    return result


def evaluate(accumulator: int, tokens: list[bytes]) -> tuple[int, int, bool]:
    """Return (new accumulator, number of evaluated tokens, stop seen)."""
    index = 0
    while index < len(tokens):
        operator = tokens[index]
        if operator == STOP:
            return accumulator, index, True
        if operator not in OPERATORS:
            raise LineError(b"invalid operator '" + operator + b"'")
        if index + 1 == len(tokens):
            raise LineError(b"missing operand after '" + operator + b"'")
        accumulator = apply(accumulator, operator, parse_operand(tokens[index + 1]))
        index += 2
    return accumulator, index, False


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
    accumulator = 0
    status = 0
    try:
        lines = InputStream(handle)
        while True:
            prompt(prompting, f"{accumulator} ")
            line = lines.read_line()
            if line is None:
                return status
            tokens = split_tokens(line.text)
            if not tokens:
                continue
            try:
                result, used, stop = evaluate(accumulator, tokens)
            except LineError as error:
                common.err.write(
                    encode_arg(f"{TOOL}: {source}:{line.line}: ")
                    + error.message
                    + b"\n"
                )
                common.err.flush()
                status = 1
                continue
            if used:
                common.write(
                    f"{accumulator} ".encode()
                    + b" ".join(tokens[:used])
                    + f" == {result}\n".encode()
                )
                accumulator = result
            if stop:
                common.write(BANNER)
                common.out.flush()
                return status
            common.out.flush()
    except InputError as error:
        file_failure(TOOL, source, error.error)
        return 1
    finally:
        if source != "-":
            handle.close()

"""Reference implementation of dp-infix (projects/46-infix/specs/SRS.md).

The input is a dialog of lines read one at a time: an infix expression, then an answer to
``Another? (y/n)``, then (after ``y``) the next expression, and so on. Each expression is
converted with the shunting-yard algorithm while it is checked, left to right, so the first
error in a line is the one reported. A bad expression is reported and the dialog goes on; a
bad answer ends it.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from . import common
from .common import (PROMPT, DataError, Option, UsageError, data_failure, file_failure,
                     handle_action, open_input, parse_args, prompt, usage_failure)

TOOL = "dp-infix"
EXPRESSION_PROMPT = "Enter infix expression: "
ANSWER_PROMPT = "Another? (y/n) "
HELP_TEXT = """\
Usage: dp-infix [OPTION]... [FILE]
Convert infix expressions to postfix (reverse Polish) notation.

Read FILE, or standard input when FILE is absent or -.  Lines alternate
between an infix expression and the answer to 'Another? (y/n)': y or Y asks
for another expression; n, N, or the end of the input ends the session.
Operands are runs of letters and digits; the operators are + - * / % (all
left-associative, * / % before + -), and parentheses group.

Options:
  -p, --prompt    write the prompts to standard error before each read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]
BLANKS = b" \t"
OPERATORS = {ord("+"): 1, ord("-"): 1, ord("*"): 2, ord("/"): 2, ord("%"): 2}
LEFT, RIGHT = ord("("), ord(")")


class ExpressionError(Exception):
    """An invalid expression; ``message`` is the CONV-34 message bytes."""

    def __init__(self, message: bytes):
        super().__init__(message)
        self.message = message


def read_lines(handle: BinaryIO) -> Iterator[tuple[bytes, int]]:
    """Yield (line without LF and final CR, line number) one line at a time (CONV-37)."""
    number = 0
    while True:
        line = handle.readline()
        if not line:
            return
        number += 1
        if line.endswith(b"\n"):
            line = line[:-1]
        else:  # the unterminated last line: a trailing 0x1A run is not data
            line = line.rstrip(b"\x1a")
            if not line:
                return
        if line.endswith(b"\r"):
            line = line[:-1]
        yield line, number


def is_operand_byte(byte: int) -> bool:
    return (0x30 <= byte <= 0x39) or (0x41 <= byte <= 0x5A) or (0x61 <= byte <= 0x7A)


def shown(byte: int) -> bytes:
    """A byte as it appears in a diagnostic: itself if printable ASCII, else \\xHH."""
    if 0x21 <= byte <= 0x7E:
        return bytes([byte])
    return b"\\x%02X" % byte


def to_postfix(expression: bytes) -> list[bytes]:
    """Convert one expression; raise ExpressionError at the first error, left to right."""
    output: list[bytes] = []
    stack: list[int] = []
    expect_operand = True
    seen_token = False
    index = 0
    while index < len(expression):
        byte = expression[index]
        if byte in BLANKS:
            index += 1
            continue
        seen_token = True
        if is_operand_byte(byte):
            end = index
            while end < len(expression) and is_operand_byte(expression[end]):
                end += 1
            operand = expression[index:end]
            index = end
            if not expect_operand:
                raise ExpressionError(b"unexpected operand '" + operand + b"'")
            output.append(operand)
            expect_operand = False
            continue
        index += 1
        if byte == LEFT:
            if not expect_operand:
                raise ExpressionError(b"unexpected '('")
            stack.append(byte)
        elif byte == RIGHT:
            if expect_operand:
                raise ExpressionError(b"unexpected ')'")
            while stack and stack[-1] != LEFT:
                output.append(bytes([stack.pop()]))
            if not stack:
                raise ExpressionError(b"unmatched ')'")
            stack.pop()
        elif byte in OPERATORS:
            if expect_operand:
                raise ExpressionError(b"unexpected operator '" + bytes([byte]) + b"'")
            while stack and stack[-1] != LEFT and OPERATORS[stack[-1]] >= OPERATORS[byte]:
                output.append(bytes([stack.pop()]))
            stack.append(byte)
            expect_operand = True
        else:
            raise ExpressionError(b"invalid character '" + shown(byte) + b"'")
    if not seen_token:
        raise ExpressionError(b"empty expression")
    if expect_operand:
        raise ExpressionError(b"unexpected end of expression")
    while stack:
        top = stack.pop()
        if top == LEFT:
            raise ExpressionError(b"unmatched '('")
        output.append(bytes([top]))
    return output


def record(expression: bytes, postfix: list[bytes]) -> bytes:
    return (b"Infix:   " + expression.strip(BLANKS) + b"\n"
            + b"Postfix: " + b" ".join(postfix) + b"\n")


def session(lines: Iterator[tuple[bytes, int]], source: str, prompting: bool) -> int:
    status = 0
    while True:
        prompt(prompting, EXPRESSION_PROMPT)
        item = next(lines, None)
        if item is None:
            return status
        expression, number = item
        try:
            common.write(record(expression, to_postfix(expression)))
            common.out.flush()
        except ExpressionError as error:
            data_failure(TOOL, DataError(source, number, error.message))
            status = 1
        prompt(prompting, ANSWER_PROMPT)
        item = next(lines, None)
        if item is None:
            return status
        answer, number = item
        word = answer.strip(BLANKS)
        if word in (b"n", b"N"):
            return status
        if word not in (b"y", b"Y"):
            raise DataError(source, number, b"invalid answer '" + word + b"'")


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
        return session(read_lines(handle), source, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except BrokenPipeError:
        raise
    except OSError as error:  # the input could not be read
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()

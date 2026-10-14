"""Reference implementation of dp-matmult (projects/30-matmult/specs/SRS.md).

The input is read incrementally, one token at a time, so the tool works interactively: the
first matrix is written as soon as its last element is complete, before the second matrix is
read. A run of 0x1A bytes is held back until the next byte shows whether it reaches the end of
the input (CONV-37).
"""

from __future__ import annotations

import sys

from .common import (INT64_MAX, INT64_MIN, PROMPT, DataError, InputError, InputStream,
                     UsageError, data_failure, diagnose, file_failure, handle_action,
                     open_input, out, parse_args, parse_int_token, prompt, usage_failure,
                     write)

TOOL = "dp-matmult"
MAX_SIZE = 20
SIZE_PROMPT = "Input matrix size: "
FIRST_PROMPT = "Input first matrix by row\n"
SECOND_PROMPT = "Input second matrix by row\n"
HELP_TEXT = """\
Usage: dp-matmult [OPTION]... [FILE]
Multiply two square matrices of integers.

Read whitespace-separated integers from FILE, or from standard input when FILE
is absent or -: the size N (1-20), then the N*N elements of the first matrix
row by row, then the N*N elements of the second.  Print both matrices and
their product.  Elements and results are 64-bit signed integers; a product
that does not fit is reported as an error.

Options:
  -p, --prompt    write prompts to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
"""


class OverflowFailure(Exception):
    """A product element (1-based row and column) that does not fit in 64 bits."""

    def __init__(self, row: int, column: int):
        super().__init__(row, column)
        self.row = row
        self.column = column


Matrix = list[list[int]]


def read_matrix(reader: InputStream, source: str, size: int) -> Matrix:
    """Read size*size integer elements in row-major order, validating each as it arrives."""
    return [[parse_int_token(reader.require(source), source) for _ in range(size)]
            for _ in range(size)]


def format_matrix(title: str, matrix: Matrix) -> str:
    rows = "".join(" ".join(str(value) for value in row) + "\n" for row in matrix)
    return f"{title}\n{rows}"


def checked(value: int) -> bool:
    return INT64_MIN <= value <= INT64_MAX


def multiply(first: Matrix, second: Matrix) -> Matrix:
    """The product, with every term and every partial sum (ascending k) checked for overflow."""
    size = len(first)
    product: Matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            total = 0
            for k in range(size):
                term = first[i][k] * second[k][j]
                total += term
                if not checked(term) or not checked(total):
                    raise OverflowFailure(i + 1, j + 1)
            row.append(total)
        product.append(row)
    return product


def session(reader: InputStream, source: str, prompts: bool) -> None:
    prompt(prompts, SIZE_PROMPT)
    size = parse_int_token(reader.require(source), source, 1, MAX_SIZE)
    prompt(prompts, FIRST_PROMPT)
    first = read_matrix(reader, source, size)
    write(format_matrix("Matrix m1:", first))
    out.flush()
    prompt(prompts, SECOND_PROMPT)
    second = read_matrix(reader, source, size)
    write(format_matrix("Matrix m2:", second))
    out.flush()
    product = multiply(first, second)
    write(format_matrix("Product m3:", product))
    out.flush()


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
        session(InputStream(stream), source, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except OverflowFailure as failure:
        diagnose(TOOL, f"integer overflow in product row {failure.row}, "
                       f"column {failure.column}")
        return 1
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0

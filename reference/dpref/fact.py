"""Reference implementation of dp-fact (projects/23-recursion/specs/SRS.md).

The factorial is computed by a recursive function, as SRS-23 NFR-05 requires of
implementations; the input loop is shared with the project's other tools.
"""

from __future__ import annotations

from ._recursion_stream import run_tool
from .common import Token, parse_int_token, write

TOOL = "dp-fact"
PROMPT_TEXT = "Enter a nonnegative integer: "
MAX_N = 20  # 20! is the largest factorial below 2**63
HELP_TEXT = """\
Usage: dp-fact [OPTION]... [FILE]
Print the factorial of each number in FILE, computed by recursion.

With no FILE, or when FILE is -, read standard input.  Numbers are whole
numbers from 0 to 20, separated by whitespace, and are read until the end of
the input.  For each number N the line 'N! = VALUE' is printed.

Options:
  -p, --prompt    write the prompt 'Enter a nonnegative integer: ' to standard
                    error before each number is read
      --help      display this help and exit
      --version   output version information and exit
"""


def factorial(n: int) -> int:
    """0! = 1 and n! = n * (n-1)! for n > 0."""
    if n == 0:
        return 1
    return n * factorial(n - 1)


def answer(token: Token, source: str) -> None:
    n = parse_int_token(token, source, 0, MAX_N)
    write(f"{n}! = {factorial(n)}\n".encode("ascii"))


def main(argv: list[str]) -> int:
    return run_tool(argv, TOOL, HELP_TEXT, PROMPT_TEXT, answer)

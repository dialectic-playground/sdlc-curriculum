"""Reference implementation of dp-walk-r (projects/23-recursion/specs/SRS.md).

W(d) is computed by plain tree recursion with no memory of earlier results (SRS-23 NFR-05),
so its run time grows like W(d) itself; tests keep d small.
"""

from __future__ import annotations

from ._recursion_stream import run_tool
from ._recursion_walk import PROMPT_TEXT, answerer

TOOL = "dp-walk-r"
MAX_DISTANCE = 45
HELP_TEXT = """\
Usage: dp-walk-r [OPTION]... [FILE]
Count the ways a robot can walk a distance in steps of 1 and 2 meters, by
plain recursion.

With no FILE, or when FILE is -, read standard input.  Distances are whole
numbers from 1 to 45, separated by whitespace.  The count is computed from
W(1) = 1, W(2) = 2, W(d) = W(d-1) + W(d-2) by recursion that remembers no
earlier result, so its run time grows exponentially with the distance; see
dp-walk-nr for distances up to 91.

Options:
  -p, --prompt    write the prompt 'Enter distance: ' to standard error before
                    each distance is read
      --help      display this help and exit
      --version   output version information and exit
"""


def walk(distance: int) -> int:
    """W(d) by naive tree recursion, for d >= 1."""
    if distance <= 2:
        return distance
    return walk(distance - 1) + walk(distance - 2)


def main(argv: list[str]) -> int:
    return run_tool(argv, TOOL, HELP_TEXT, PROMPT_TEXT, answerer(walk, MAX_DISTANCE))

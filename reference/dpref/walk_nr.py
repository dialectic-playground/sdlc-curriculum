"""Reference implementation of dp-walk-nr (projects/23-recursion/specs/SRS.md).

W(d) is computed by a loop that keeps only the last two values (SRS-23 NFR-05).
"""

from __future__ import annotations

from ._recursion_stream import run_tool
from ._recursion_walk import PROMPT_TEXT, answerer

TOOL = "dp-walk-nr"
MAX_DISTANCE = 91  # W(91) = 7540113804746346429 is the largest count below 2**63
HELP_TEXT = """\
Usage: dp-walk-nr [OPTION]... [FILE]
Count the ways a robot can walk a distance in steps of 1 and 2 meters, by
iteration.

With no FILE, or when FILE is -, read standard input.  Distances are whole
numbers from 1 to 91, separated by whitespace.  The count is computed from
W(1) = 1, W(2) = 2, W(d) = W(d-1) + W(d-2) by a loop that keeps only the last
two counts, so its run time grows linearly with the distance.

Options:
  -p, --prompt    write the prompt 'Enter distance: ' to standard error before
                    each distance is read
      --help      display this help and exit
      --version   output version information and exit
"""


def walk(distance: int) -> int:
    """W(d) by iteration, for d >= 1."""
    if distance <= 2:
        return distance
    previous, current = 1, 2
    for _ in range(distance - 2):
        previous, current = current, previous + current
    return current


def main(argv: list[str]) -> int:
    return run_tool(argv, TOOL, HELP_TEXT, PROMPT_TEXT, answerer(walk, MAX_DISTANCE))

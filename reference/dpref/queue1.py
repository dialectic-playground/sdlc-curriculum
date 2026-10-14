"""Reference implementation of dp-queue1 (projects/45-queue-stack/specs/SRS.md)."""

from __future__ import annotations

from ._queue_stack_driver import QUEUE, ArrayQueue, run_tool

TOOL = "dp-queue1"
HELP_TEXT = """\
Usage: dp-queue1 [OPTION]... [FILE]
Run a queue of bank customers stored in a circular array of 100 places.

Read commands from FILE, or from standard input when FILE is absent or -.
1 inserts the customer whose last name, first name, account number, and
balance (at most 2 decimal places) follow; 2 removes the customer at the
front; 3 displays the queue from front to rear; 0 or the end of the input
quits.  Inserting into a full queue prints QUEUE FULL, and removing from an
empty one prints QUEUE EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
"""


def main(argv: list[str]) -> int:
    return run_tool(TOOL, HELP_TEXT, QUEUE, ArrayQueue, argv)

"""Reference implementation of dp-stack1 (projects/45-queue-stack/specs/SRS.md)."""

from __future__ import annotations

from ._queue_stack_driver import STACK, ArrayStack, run_tool

TOOL = "dp-stack1"
HELP_TEXT = """\
Usage: dp-stack1 [OPTION]... [FILE]
Run a stack of cafeteria trays stored in an array of 100 places.

Read commands from FILE, or from standard input when FILE is absent or -.
1 pushes the tray whose color and id follow; 2 pops the tray on top; 3
displays the stack from top to bottom; 0 or the end of the input quits.
Pushing onto a full stack prints STACK FULL, and popping an empty one prints
STACK EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
"""


def main(argv: list[str]) -> int:
    return run_tool(TOOL, HELP_TEXT, STACK, ArrayStack, argv)

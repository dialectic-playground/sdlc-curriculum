"""Reference implementation of dp-elephnt1 (projects/43-linked-list/specs/SRS.md).

Three nodes are created individually and linked by explicit assignments, then traversed.
"""

from __future__ import annotations

from ._linked_list_elephants import Node, print_elephants
from .common import UsageError, handle_action, parse_args, usage_failure

TOOL = "dp-elephnt1"
HELP_TEXT = """\
Usage: dp-elephnt1 [OPTION]...
Build a linked list of three elephants (Edna, Elmer, Eloise) and print it.

The three nodes are linked by hand and the list is printed by walking it from
its first node to its end, one line per elephant.  No input is read.

Options:
      --help       display this help and exit
      --version    output version information and exit
"""


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [])
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    first = Node(b"Edna")
    second = Node(b"Elmer")
    third = Node(b"Eloise")
    first.next = second
    second.next = third
    third.next = None
    print_elephants(first)
    return 0

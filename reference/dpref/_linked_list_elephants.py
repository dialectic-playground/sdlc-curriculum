"""Linked-list helpers shared by dp-elephnt1 and dp-elephnt2 (projects/43-linked-list).

A node holds a name (bytes) and a link to its successor; ``None`` marks the end of the list.
The one traversal function writes ``Elephant number N is NAME.`` for every node, counting as
it walks.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import common


@dataclass
class Node:
    name: bytes
    next: "Node | None" = None


def print_elephants(head: Node | None) -> None:
    """Walk the list from ``head`` to the end marker, writing one line per node."""
    count = 1
    current = head
    while current is not None:
        common.write(b"Elephant number " + str(count).encode() + b" is " + current.name
                     + b".\n")
        current = current.next
        count += 1

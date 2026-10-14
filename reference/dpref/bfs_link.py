"""Reference implementation of dp-bfs-link (projects/47-bfs/specs/SRS.md).

The graph is held as adjacency lists built by insertion at the head, so each vertex's
neighbors are examined in the reverse of the order in which its edges are listed
(SRS-47 FR-07).
"""

from __future__ import annotations

from ._bfs_graph import Graph, run_bfs

TOOL = "dp-bfs-link"
HELP_TEXT = """\
Usage: dp-bfs-link [OPTION]...
Search a graph breadth-first, using adjacency lists, and print each vertex as
it is visited.

Without --graph, search the built-in graph of the seven deadly sins.  The
neighbors of a vertex are examined in the reverse of the order in which its
edges are listed.

Options:
  -g, --graph=FILE      read the graph from FILE; - means standard input
  -s, --start=VERTEX    start at vertex number VERTEX (0-999, default 0)
      --help            display this help and exit
      --version         output version information and exit
"""


def build_lists(graph: Graph) -> list[list[int]]:
    lists: list[list[int]] = [[] for _ in graph.names]
    for u, v in graph.edges:
        lists[u].insert(0, v)
        lists[v].insert(0, u)
    return lists


def main(argv: list[str]) -> int:
    return run_bfs(TOOL, HELP_TEXT, argv, build_lists)

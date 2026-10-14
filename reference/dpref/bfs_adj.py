"""Reference implementation of dp-bfs-adj (projects/47-bfs/specs/SRS.md).

The graph is held as an adjacency matrix, so each vertex's neighbors are examined in
ascending order of vertex number (SRS-47 FR-06).
"""

from __future__ import annotations

from ._bfs_graph import Graph, run_bfs

TOOL = "dp-bfs-adj"
HELP_TEXT = """\
Usage: dp-bfs-adj [OPTION]...
Search a graph breadth-first, using an adjacency matrix, and print each
vertex as it is visited.

Without --graph, search the built-in graph of the seven deadly sins.  The
neighbors of a vertex are examined in ascending order of vertex number.

Options:
  -g, --graph=FILE      read the graph from FILE; - means standard input
  -s, --start=VERTEX    start at vertex number VERTEX (0-999, default 0)
      --help            display this help and exit
      --version         output version information and exit
"""


def build_matrix(graph: Graph) -> list[list[int]]:
    size = len(graph.names)
    matrix = [[0] * size for _ in range(size)]
    for u, v in graph.edges:
        matrix[u][v] = matrix[v][u] = 1
    return [[v for v in range(size) if row[v]] for row in matrix]


def main(argv: list[str]) -> int:
    return run_bfs(TOOL, HELP_TEXT, argv, build_matrix)

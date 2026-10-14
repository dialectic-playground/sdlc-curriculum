"""Graph input, BFS, and command line shared by dp-bfs-adj and dp-bfs-link.

Specified in projects/47-bfs/specs/SRS.md. The two tools differ only in how each vertex's
neighbors are ordered (FR-06 and FR-07); everything else is common.
"""

from __future__ import annotations

from collections import deque
from typing import Callable

from . import common
from .common import (DataError, Option, Token, UsageError, data_failure, file_failure,
                     handle_action, invalid_argument, parse_args, parse_count,
                     parse_int_token, read_all, strip_eof_marker, tokenize, unexpected_end,
                     usage_failure)

MAX_VERTICES = 1000
MAX_START = MAX_VERTICES - 1

BUILTIN_GRAPH = b"""\
7
Anger Lust Envy Gluttony Pride Sloth Covetousness
9
0 1
0 2
0 3
1 2
1 4
2 4
3 5
4 6
5 6
"""

OPTIONS = [
    Option("graph", short="g", long="graph", takes_value=True),
    Option("start", short="s", long="start", takes_value=True),
]


class Graph:
    """Vertex names and the edges in the order the input lists them."""

    def __init__(self, names: list[bytes], edges: list[tuple[int, int]]):
        self.names = names
        self.edges = edges


def parse_graph(data: bytes, source: str) -> Graph:
    """Parse and validate a whole graph description (SRS-47 FR-02, FR-03)."""
    tokens = tokenize(strip_eof_marker(data))
    position = 0

    def take() -> Token:
        nonlocal position
        if position >= len(tokens):
            raise unexpected_end(source, data)
        position += 1
        return tokens[position - 1]

    count = parse_int_token(take(), source, 1, MAX_VERTICES)
    names = [take().text for _ in range(count)]
    edge_count = parse_int_token(take(), source, 0, count * (count - 1) // 2)
    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for _ in range(edge_count):
        first = take()
        u = parse_int_token(first, source, 0, count - 1)
        second = take()
        v = parse_int_token(second, source, 0, count - 1)
        spelled = first.text + b" " + second.text
        if u == v:
            raise DataError(source, second.line, b"self-loop '" + spelled + b"'")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise DataError(source, second.line, b"duplicate edge '" + spelled + b"'")
        seen.add(key)
        edges.append((u, v))
    if position < len(tokens):
        extra = tokens[position]
        raise DataError(source, extra.line, b"unexpected token '" + extra.text + b"'")
    return Graph(names, edges)


def bfs(neighbors: list[list[int]], start: int) -> list[int]:
    """Vertices in discovery order, examining each vertex's neighbors in the given order."""
    visited = [False] * len(neighbors)
    visited[start] = True
    order = [start]
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in neighbors[u]:
            if not visited[v]:
                visited[v] = True
                order.append(v)
                queue.append(v)
    return order


def run_bfs(tool: str, help_text: str, argv: list[str],
            build: Callable[[Graph], list[list[int]]]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(tool, parsed, help_text):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
        source = parsed.values.get("graph")
        if source == "":
            raise invalid_argument("", parsed.spelled["graph"])
        start_text = str(parsed.values.get("start", "0"))
        start = parse_count(start_text, parsed.spelled.get("start", "-s"), 0, MAX_START)
    except UsageError as error:
        return usage_failure(tool, error)

    if source is None:
        graph = parse_graph(BUILTIN_GRAPH, "(built-in)")
    else:
        try:
            data = read_all(str(source))
        except OSError as error:
            file_failure(tool, str(source), error)
            return 1
        try:
            graph = parse_graph(data, str(source))
        except DataError as error:
            return data_failure(tool, error)
    if start >= len(graph.names):
        common.diagnose(tool, f"start vertex '{start_text}' out of range 0-{len(graph.names) - 1}")
        return 1
    for vertex in bfs(build(graph), start):
        common.write(graph.names[vertex] + b" has been visited.\n")
    return 0

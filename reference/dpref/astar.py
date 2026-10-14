"""Reference implementation of dp-astar (projects/48-astar/specs/SRS.md).

Both data files are read and validated completely before the start city is read; the
search itself cannot fail, so the report is written only after it has finished.
"""

from __future__ import annotations

import sys

from . import common
from .common import (PROMPT, WHITESPACE, DataError, Option, Token, UsageError, data_failure,
                     file_failure, handle_action, invalid_argument, parse_args,
                     parse_int_token, prompt, read_all, strip_eof_marker, tokenize,
                     unexpected_end, usage_failure)

TOOL = "dp-astar"
PROMPT_TEXT = "Enter start city: "
DEFAULT_NAMES = "names.dat"
DEFAULT_DISTANCES = "distance.dat"
DEFAULT_GOAL = "vienna"
NO_ROAD = 1000
MAX_CITIES = 1000
MAX_VALUE = 1000000
HELP_TEXT = """\
Usage: dp-astar [OPTION]... [CITY]
Find the shortest road route from CITY to Vienna with the A* search.

With no CITY, or when CITY is -, read the start city from standard input.
City names are matched without regard to ASCII case.  The cities and their
estimated distances to the goal are read from names.dat, and the road
distances from distance.dat, where 1000 means that there is no road.

Options:
  -n, --names=FILE      read the cities and estimates from FILE
                          (default names.dat)
  -d, --distances=FILE  read the road distances from FILE
                          (default distance.dat)
  -g, --goal=CITY       find a route to CITY instead of vienna
  -t, --trace           show every step of the search before the result
  -p, --prompt          write the prompt 'Enter start city: ' to standard
                          error before the start city is read
      --help            display this help and exit
      --version         output version information and exit
"""

OPTIONS = [
    Option("names", short="n", long="names", takes_value=True),
    Option("distances", short="d", long="distances", takes_value=True),
    Option("goal", short="g", long="goal", takes_value=True),
    Option("trace", short="t", long="trace"),
    PROMPT,
]


def fold(name: bytes) -> bytes:
    """ASCII-only case folding (A-Z to a-z); every other byte is unchanged."""
    return name.lower() if name.isascii() else bytes(
        b + 32 if 0x41 <= b <= 0x5A else b for b in name)


def parse_names(data: bytes, source: str) -> tuple[list[bytes], list[int]]:
    tokens = tokenize(strip_eof_marker(data))
    names: list[bytes] = []
    estimates: list[int] = []
    seen: set[bytes] = set()
    for index in range(0, len(tokens), 2):
        name = tokens[index]
        if len(names) == MAX_CITIES:
            raise DataError(source, name.line, "too many cities")
        if fold(name.text) in seen:
            raise DataError(source, name.line, b"duplicate city '" + name.text + b"'")
        if index + 1 == len(tokens):
            raise unexpected_end(source, data)
        estimates.append(parse_int_token(tokens[index + 1], source, 0, MAX_VALUE))
        seen.add(fold(name.text))
        names.append(name.text)
    if not names:
        raise unexpected_end(source, data)
    return names, estimates


def parse_distances(data: bytes, source: str, count: int) -> list[list[int]]:
    tokens = tokenize(strip_eof_marker(data))
    needed = count * count
    if len(tokens) < needed:
        for token in tokens:
            parse_int_token(token, source, 0, MAX_VALUE)
        raise unexpected_end(source, data)
    values = [parse_int_token(token, source, 0, MAX_VALUE) for token in tokens[:needed]]
    if len(tokens) > needed:
        extra = tokens[needed]
        raise DataError(source, extra.line, b"unexpected token '" + extra.text + b"'")
    return [values[row * count:(row + 1) * count] for row in range(count)]


def read_start_token() -> tuple[Token | None, int]:
    """The first token of standard input, read no further than needed (CONV-32, CONV-37).

    Returns the token (None at the end of the input) and the line number reached.
    """
    handle = sys.stdin.buffer
    line = 1
    current = bytearray()
    token_line = 1
    while True:
        chunk = handle.read1(65536)  # type: ignore[attr-defined]
        if not chunk:
            break
        for byte in chunk:
            if byte in WHITESPACE:
                if current:
                    return Token(bytes(current), token_line), line
                if byte == 0x0A:
                    line += 1
            else:
                if not current:
                    token_line = line
                current.append(byte)
    text = bytes(current).rstrip(b"\x1a")
    return (Token(text, token_line) if text else None), line


def display(name: bytes) -> bytes:
    """The goal's name with its first byte capitalized if it is an ASCII lowercase letter."""
    if name and 0x61 <= name[0] <= 0x7A:
        return bytes([name[0] - 32]) + name[1:]
    return name


def search(start: int, goal: int, estimates: list[int], roads: list[list[int]],
           trace: list[bytes], names: list[bytes]) -> tuple[list[int], int] | None:
    count = len(names)
    g = [0] * count
    f = [0] * count
    back = [-1] * count
    state = ["new"] * count  # new, open, closed

    def note(word: str, city: int, via: int | None) -> None:
        line = f"{word} ".encode() + names[city] + f" g={g[city]} f={f[city]}".encode()
        if via is not None:
            line += b" via " + names[via]
        trace.append(line + b"\n")

    g[start], f[start], state[start] = 0, estimates[start], "open"
    note("open", start, None)
    while True:
        candidates = [city for city in range(count) if state[city] == "open"]
        if not candidates:
            return None
        u = min(candidates, key=lambda city: (f[city], city))
        note("select", u, None)
        if u == goal:
            break
        state[u] = "closed"
        for v in range(count):
            if v == u or roads[u][v] == NO_ROAD:
                continue
            new_g = g[u] + roads[u][v]
            if state[v] == "new":
                word = "open"
            elif new_g < g[v]:
                word = "update" if state[v] == "open" else "reopen"
            else:
                continue
            g[v], f[v], back[v], state[v] = new_g, new_g + estimates[v], u, "open"
            note(word, v, u)
    path = [goal]
    while path[-1] != start:
        path.append(back[path[-1]])
    path.reverse()
    return path, g[goal]


def file_value(parsed: common.Parsed, dest: str, default: str) -> str:
    value = str(parsed.values.get(dest, default))
    if value in ("", "-"):
        raise invalid_argument(value, parsed.spelled[dest])
    return value


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
        names_file = file_value(parsed, "names", DEFAULT_NAMES)
        distances_file = file_value(parsed, "distances", DEFAULT_DISTANCES)
        goal_name = str(parsed.values.get("goal", DEFAULT_GOAL))
        if goal_name == "":
            raise invalid_argument("", parsed.spelled["goal"])
    except UsageError as error:
        return usage_failure(TOOL, error)

    try:
        names_data = read_all(names_file)
    except OSError as error:
        file_failure(TOOL, names_file, error)
        return 1
    try:
        names, estimates = parse_names(names_data, names_file)
    except DataError as error:
        return data_failure(TOOL, error)
    try:
        distance_data = read_all(distances_file)
    except OSError as error:
        file_failure(TOOL, distances_file, error)
        return 1
    try:
        roads = parse_distances(distance_data, distances_file, len(names))
    except DataError as error:
        return data_failure(TOOL, error)

    index = {fold(name): number for number, name in enumerate(names)}
    goal = index.get(fold(common.encode_arg(goal_name)))
    if goal is None:
        common.diagnose(TOOL, f"unknown goal city '{goal_name}'")
        return 1

    if parsed.operands and parsed.operands[0] != "-":
        start_text = common.encode_arg(parsed.operands[0])
        start = index.get(fold(start_text))
        if start is None:
            common.err.write(f"{TOOL}: unknown start city '".encode() + start_text + b"'\n")
            return 1
    else:
        prompt(bool(parsed.values.get("prompt")), PROMPT_TEXT)
        try:
            token, line = read_start_token()
        except OSError as error:
            file_failure(TOOL, "-", error)
            return 1
        if token is None:
            return data_failure(TOOL, DataError("-", line, "unexpected end of input"))
        start = index.get(fold(token.text))
        if start is None:
            return data_failure(TOOL, DataError(
                "-", token.line, b"unknown start city '" + token.text + b"'"))

    trace: list[bytes] = []
    result = search(start, goal, estimates, roads, trace, names)
    if parsed.values.get("trace"):
        common.write(b"".join(trace))
    if result is None:
        common.write(b"No path from " + names[start] + b" to " + display(names[goal]) + b".\n")
        return 0
    path, total = result
    common.write(b"Optimal path to " + display(names[goal]) + b":\n")
    common.write(b" -> ".join(names[city] for city in path) + b"\n")
    common.write(f"Total distance: {total} kilometers\n".encode())
    return 0

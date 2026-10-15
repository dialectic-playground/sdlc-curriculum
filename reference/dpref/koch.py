"""Reference implementation of dp-koch (projects/51-koch/specs/SRS.md).

The figure is computed exactly as FR-04 prescribes: sqrt(3)/2 once, the segment length by
repeated division by 3, and coordinates accumulated segment by segment in binary64, so every
conforming implementation prints the same digits. Dialog tokens are read incrementally
(CONV-32) so that each figure is written before the next answer is awaited.
"""

from __future__ import annotations

import math
from collections.abc import Iterator

from . import common
from .common import (
    PROMPT,
    DataError,
    InputError,
    InputStream,
    Option,
    UsageError,
    data_failure,
    file_failure,
    fix,
    handle_action,
    open_input,
    parse_args,
    parse_count,
    parse_int_token,
    prompt,
    usage_failure,
)

TOOL = "dp-koch"
LEVEL_PROMPT = "Enter level (0-6): "
ANOTHER_PROMPT = "Do another (y = yes, n = no)? "
MAX_LEVEL = 6
DEFAULT_LENGTH = 729
MAX_LENGTH = 1_000_000
SNOWFLAKE_SIDES = (0, 4, 2)
DIGITS = 6
HELP_TEXT = """\
Usage: dp-koch [OPTION]... [FILE]
Draw the von Koch curve or snowflake as a list of vertex coordinates.

Reads a dialog from FILE (standard input with no FILE, or when FILE is -):
a level from 0 to 6, then, after each figure, an answer y or n to the
question whether to draw another.  With --level, draws one figure and
reads no input.  The curve starts at (0, 0) and runs in the +x direction.

Options:
  -l, --level=LEVEL    draw one figure of level LEVEL (0-6) and read no input
  -s, --snowflake      draw the closed snowflake (three curves), not one curve
  -L, --length=LENGTH  length of the base segment (1-1000000, default 729)
      --svg            write each figure as an SVG document
  -p, --prompt         write prompts to standard error before each read
      --help           display this help and exit
      --version        output version information and exit
"""

OPTIONS: list[Option] = [
    Option("level", short="l", long="level", takes_value=True),
    Option("snowflake", short="s", long="snowflake"),
    Option("length", short="L", long="length", takes_value=True),
    Option("svg", long="svg"),
    PROMPT,
]


def directions(level: int, base: int) -> Iterator[int]:
    """Direction codes of the 4**level segments of a curve whose base direction is ``base``."""
    if level == 0:
        yield base
        return
    for turn in (0, 1, 5, 0):
        yield from directions(level - 1, (base + turn) % 6)


def vertices(level: int, length: int, snowflake: bool) -> list[tuple[float, float]]:
    """Vertex coordinates per FR-04, starting at (0, 0)."""
    half_root3 = math.sqrt(3.0) / 2.0
    side = float(length)
    for _ in range(level):
        side = side / 3.0
    half = side / 2.0
    rise = side * half_root3
    delta = [
        (side, 0.0),
        (half, rise),
        (-half, rise),
        (-side, 0.0),
        (-half, -rise),
        (half, -rise),
    ]
    x = y = 0.0
    points = [(x, y)]
    for base in SNOWFLAKE_SIDES if snowflake else (0,):
        for code in directions(level, base):
            dx, dy = delta[code]
            x = x + dx
            y = y + dy
            points.append((x, y))
    return points


def heading(level: int, snowflake: bool) -> str:
    segments = (3 if snowflake else 1) * 4**level
    noun = "segment" if segments == 1 else "segments"
    return f"Koch {'snowflake' if snowflake else 'curve'}, level {level}: {segments} {noun}"


def render_text(level: int, snowflake: bool, points: list[tuple[float, float]]) -> str:
    lines = [heading(level, snowflake)]
    lines += [f"{fix(x, DIGITS)} {fix(y, DIGITS)}" for x, y in points]
    return "\n".join(lines) + "\n"


def render_svg(level: int, snowflake: bool, points: list[tuple[float, float]]) -> str:
    xs = [x for x, _ in points]
    ys = [-y for _, y in points]
    left = math.floor(min(xs)) - 1
    top = math.floor(min(ys)) - 1
    width = math.ceil(max(xs)) + 1 - left
    height = math.ceil(max(ys)) + 1 - top
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left} {top} {width} {height}">',
        f"<title>{heading(level, snowflake)}</title>",
        (
            '<polyline fill="none" stroke="black" stroke-width="1" '
            'vector-effect="non-scaling-stroke" points="'
        ),
    ]
    lines += [f"{fix(x, DIGITS)},{fix(-y, DIGITS)}" for x, y in points]
    lines += ['"/>', "</svg>"]
    return "\n".join(lines) + "\n"


def draw(level: int, length: int, snowflake: bool, svg: bool) -> None:
    points = vertices(level, length, snowflake)
    render = render_svg if svg else render_text
    common.write(render(level, snowflake, points).encode())
    common.out.flush()


def dialog(
    stream: InputStream,
    source: str,
    prompting: bool,
    length: int,
    snowflake: bool,
    svg: bool,
) -> int:
    while True:
        prompt(prompting, LEVEL_PROMPT)
        level = parse_int_token(stream.require(source), source, 0, MAX_LEVEL)
        draw(level, length, snowflake, svg)
        prompt(prompting, ANOTHER_PROMPT)
        token = stream.token()
        if token is None or token.text in (b"n", b"N"):
            return 0
        if token.text not in (b"y", b"Y"):
            raise DataError(source, token.line, b"invalid answer '" + token.text + b"'")


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        level = None
        if "level" in parsed.values:
            level = parse_count(
                str(parsed.values["level"]), parsed.spelled["level"], 0, MAX_LEVEL
            )
        length = DEFAULT_LENGTH
        if "length" in parsed.values:
            length = parse_count(
                str(parsed.values["length"]), parsed.spelled["length"], 1, MAX_LENGTH
            )
        if level is not None and parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    snowflake = bool(parsed.values.get("snowflake"))
    svg = bool(parsed.values.get("svg"))
    if level is not None:
        draw(level, length, snowflake, svg)
        return 0

    source = parsed.operands[0] if parsed.operands else "-"
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        return dialog(InputStream(handle), source, prompting, length, snowflake, svg)
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as error:
        file_failure(TOOL, source, error.error)
        return 1
    finally:
        if source != "-":
            handle.close()

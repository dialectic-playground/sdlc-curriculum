"""Reference implementation of dp-hello (projects/00-hello-world/specs/SRS.md)."""

from __future__ import annotations

from .common import (Option, UsageError, handle_action, parse_args, parse_count,
                     invalid_argument, usage_failure, write)

TOOL = "dp-hello"
MAX_COUNT = 1000
HELP_TEXT = """\
Usage: dp-hello [OPTION]...
Print a greeting to standard output.

Options:
  -n, --name=NAME     greet NAME instead of World
  -c, --count=COUNT   print the greeting COUNT times (1-1000, default 1)
      --help          display this help and exit
      --version       output version information and exit
"""

OPTIONS = [
    Option("name", short="n", long="name", takes_value=True),
    Option("count", short="c", long="count", takes_value=True),
]


def build_greeting(name: str) -> str:
    return f"Hello, {name}!\n"


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
        name = str(parsed.values.get("name", "World"))
        if name == "":
            raise invalid_argument(name, parsed.spelled["name"])
        count = 1
        if "count" in parsed.values:
            count = parse_count(str(parsed.values["count"]), parsed.spelled["count"],
                                minimum=1, maximum=MAX_COUNT)
    except UsageError as error:
        return usage_failure(TOOL, error)
    write(build_greeting(name) * count)
    return 0

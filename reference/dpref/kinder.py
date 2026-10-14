"""Reference implementation of dp-kinder (projects/11-kinder/specs/SRS.md)."""

from __future__ import annotations

from .common import Option, UsageError, handle_action, parse_args, usage_failure, write

TOOL = "dp-kinder"
MESSAGE = b"ANSI--A kinder and gentler C!\n"
HELP_TEXT = """\
Usage: dp-kinder [OPTION]...
Print the message 'ANSI--A kinder and gentler C!' to standard output.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)
    write(MESSAGE)
    return 0

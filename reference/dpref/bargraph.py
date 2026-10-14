"""Reference implementation of dp-bargraph (projects/16-bargraph/specs/SRS.md)."""

from __future__ import annotations

from ._bargraph import run_bargraph

TOOL = "dp-bargraph"
HELP_TEXT = """\
Usage: dp-bargraph [OPTION]... [FILE]
Draw a bar graph: for each record, print its title, then a bar of one '*' for
every 2 units of its value.

With no FILE, or when FILE is -, read standard input.  Lines alternate between
a title and a value; a value is a whole number from 0 to 10000 on a line of
its own.  Blank lines after the last record are ignored.

Options:
      --help       display this help and exit
      --version    output version information and exit
"""


def main(argv: list[str]) -> int:
    return run_bargraph(TOOL, HELP_TEXT, argv)

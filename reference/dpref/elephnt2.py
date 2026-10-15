"""Reference implementation of dp-elephnt2 (projects/43-linked-list/specs/SRS.md).

The dialog is line-oriented and read incrementally, so prompts appear before each read at a
keyboard; a run of 0x1A bytes reaching the end of the input is ignored (CONV-37). The list is
printed only after the dialog has ended without error.
"""

from __future__ import annotations

import sys

from ._linked_list_elephants import Node, print_elephants
from .common import (
    PROMPT,
    WHITESPACE,
    DataError,
    InputError,
    InputStream,
    Token,
    UsageError,
    data_failure,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    parse_int_token,
    prompt,
    usage_failure,
)

TOOL = "dp-elephnt2"
HELP_TEXT = """\
Usage: dp-elephnt2 [OPTION]... [FILE]
Build a linked list of elephant names from a dialog, then print the list.

Read the dialog from FILE, or from standard input when FILE is absent or -.
Lines alternate between a name and an answer: 1 adds another elephant, 0 (or
the end of the input) ends the list.  Spaces and tabs around a name or an
answer are ignored.  Then print 'Elephant number N is NAME.' for each name.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
"""
NAME_PROMPT = "\n\tNAME:\t"
ANSWER_PROMPT = "\n\tAdd another? (1 == yes, 0 == no)\t"


def read_trimmed(reader: InputStream) -> Token | None:
    """The next line without its LF, trimmed of whitespace bytes; None at end of input."""
    line = reader.read_line()
    return None if line is None else Token(line.text.strip(WHITESPACE), line.line)


def build_list(reader: InputStream, source: str, prompts: bool) -> Node | None:
    head: Node | None = None
    tail: Node | None = None
    while True:
        prompt(prompts, NAME_PROMPT)
        line = read_trimmed(reader)
        if line is None:
            raise reader.unexpected_end(source)
        if not line.text:
            raise DataError(source, line.line, "empty name")
        node = Node(line.text)
        if tail is None:
            head = node
        else:
            tail.next = node
        tail = node
        prompt(prompts, ANSWER_PROMPT)
        line = read_trimmed(reader)
        if line is None or parse_int_token(line, source, 0, 1) == 0:
            tail.next = None
            return head


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        stream = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        head = build_list(
            InputStream(stream), source, bool(parsed.values.get("prompt"))
        )
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    print_elephants(head)
    return 0

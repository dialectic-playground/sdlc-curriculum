"""Reference implementation of dp-elephnt2 (projects/43-linked-list/specs/SRS.md).

The dialog is line-oriented and read incrementally, one byte at a time, so prompts appear
before each read at a keyboard. A run of 0x1A bytes is held back until the next byte shows
whether it reaches the end of the input (CONV-37). The list is printed only after the dialog
has ended without error.
"""

from __future__ import annotations

import sys
from typing import BinaryIO

from ._linked_list_elephants import Node, print_elephants
from .common import (PROMPT, WHITESPACE, DataError, Token, UsageError, data_failure,
                     file_failure, handle_action, open_input, parse_args, parse_int_token,
                     prompt, usage_failure)

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
CTRL_Z = b"\x1a"


class InputError(Exception):
    """A read failure on the input (as opposed to a write failure on standard output)."""

    def __init__(self, error: OSError):
        super().__init__(error)
        self.error = error


class LineReader:
    """Lines read one byte at a time, with CONV-37 applied on the fly."""

    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.pushback = b""
        self.line = 1  # 1 + LF bytes consumed so far

    def _raw(self) -> bytes:
        if self.pushback:
            byte, self.pushback = self.pushback[:1], self.pushback[1:]
            return byte
        try:
            return self.stream.read(1)
        except OSError as error:
            raise InputError(error) from error

    def _byte(self) -> bytes:
        byte = self._raw()
        if byte != CTRL_Z:
            return byte
        run = byte
        while True:
            following = self._raw()
            if following == b"":
                return b""  # the run reaches the end of input: ignored
            if following != CTRL_Z:
                self.pushback = run[1:] + following + self.pushback
                return CTRL_Z
            run += following

    def read_line(self) -> Token | None:
        """The next line without its LF, trimmed of whitespace bytes; None at end of input."""
        byte = self._byte()
        if not byte:
            return None
        number, text = self.line, bytearray()
        while byte and byte != b"\n":
            text += byte
            byte = self._byte()
        if byte == b"\n":
            self.line += 1
        return Token(bytes(text).strip(WHITESPACE), number)


def build_list(reader: LineReader, source: str, prompts: bool) -> Node | None:
    head: Node | None = None
    tail: Node | None = None
    while True:
        prompt(prompts, NAME_PROMPT)
        line = reader.read_line()
        if line is None:
            raise DataError(source, reader.line, "unexpected end of input")
        if not line.text:
            raise DataError(source, line.line, "empty name")
        node = Node(line.text)
        if tail is None:
            head = node
        else:
            tail.next = node
        tail = node
        prompt(prompts, ANSWER_PROMPT)
        line = reader.read_line()
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
        head = build_list(LineReader(stream), source, bool(parsed.values.get("prompt")))
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

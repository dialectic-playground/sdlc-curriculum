"""Reference implementation of dp-line-ed (projects/44-line-editor/specs/SRS.md).

The buffer is modelled as a Python list with a cursor index, where index 0 stands for the
[BOF] sentinel and index k for the k-th text line; the SRS requires a linked list of a real
implementation, which is a design property that black-box tests cannot observe. Commands are
read from standard input one line at a time, so the editor works interactively.
"""

from __future__ import annotations

import os
import re
import sys
from typing import BinaryIO, Iterator

from . import common
from .common import (INT64_MAX, PROMPT, DataError, Option, UsageError, data_failure,
                     file_failure, handle_action, parse_args, prompt, usage_failure)

TOOL = "dp-line-ed"
SOURCE = "-"
COMMAND_PROMPT = "*"
BOF_DISPLAY = b"[BOF]"
HELP_TEXT = """\
Usage: dp-line-ed [OPTION]... FILE
Edit FILE with a line editor that reads its commands from standard input.

A missing FILE starts an empty buffer, and the current line starts at [BOF],
the position before the first line.  Commands, one per line:
  i              insert the lines that follow after the current line, up to
                   a line consisting of a single .
  d [N]          delete N lines (default 1) after the current line
  t .            type the current line
  t b            go to [BOF] and type the first line
  t e            go to the last line and type it
  t N            type the N lines after the current line
  m N            move forward N lines and type the new current line
  f 'PAT'        find the next line containing PAT and type it
  s 'OLD' 'NEW'  replace the first OLD in the current line by NEW; type it
  q              write the buffer to FILE and quit
Any punctuation character can be used in place of ' around PAT, OLD, NEW.
At the end of the input without q, the editor quits without writing FILE.

Options:
  -p, --prompt    write the prompt * to standard error before each command
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]
BLANKS = b" \t"
_INTEGER = re.compile(rb"[+-]?[0-9]+\Z")
_COMMAND = re.compile(rb"([^ \t]+)[ \t]*(.*)\Z", re.DOTALL)


class CommandError(Exception):
    """A failed command; ``message`` is the CONV-34 message bytes."""

    def __init__(self, message: bytes | str):
        super().__init__(message)
        self.message = message if isinstance(message, bytes) else message.encode()


class LineReader:
    """Standard input as lines (LF removed, then one final CR), with CONV-37 at the end."""

    def __init__(self, handle: BinaryIO):
        self.handle = handle
        self.number = 0  # line number of the last line returned
        self.lf_count = 0

    def next(self) -> bytes | None:
        line = self.handle.readline()
        if not line:
            return None
        if line.endswith(b"\n"):
            self.lf_count += 1
            line = line[:-1]
        else:
            line = line.rstrip(b"\x1a")
            if not line:
                return None
        self.number += 1
        if line.endswith(b"\r"):
            line = line[:-1]
        return line

    def end_line(self) -> int:
        return self.lf_count + 1


def load(path: str) -> list[bytes]:
    """The file's lines; a missing file is an empty buffer (raises other OSErrors)."""
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except FileNotFoundError:
        return []
    data = data.rstrip(b"\x1a")
    if not data:
        return []
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def save(path: str, lines: list[bytes]) -> None:
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    with open(path, "wb") as handle:
        handle.write(b"".join(line + b"\n" for line in lines))


def split_words(text: bytes) -> list[bytes]:
    return [word for word in re.split(rb"[ \t]+", text) if word]


def parse_count(word: bytes) -> int:
    if not _INTEGER.match(word) or int(word) > INT64_MAX or int(word) < -INT64_MAX - 1:
        raise CommandError(b"invalid integer '" + word + b"'")
    value = int(word)
    if value < 1:
        raise CommandError(b"value out of range '" + word + b"'")
    return value


def is_delimiter(byte: int) -> bool:
    return 0x21 <= byte <= 0x7E and not chr(byte).isalnum()


def take_string(text: bytes) -> tuple[bytes, bytes]:
    """Parse one delimited string at the start of ``text``; return (string, rest)."""
    if not text:
        raise CommandError("missing argument")
    if not is_delimiter(text[0]):
        raise CommandError("missing delimiter")
    end = text.find(text[0:1], 1)
    if end < 0:
        raise CommandError("unterminated string")
    return text[1:end], text[end + 1:].lstrip(BLANKS)


def no_more(rest: bytes) -> None:
    words = split_words(rest)
    if words:
        raise CommandError(b"extra argument '" + words[0] + b"'")


class Editor:
    def __init__(self, lines: list[bytes]):
        self.lines = lines
        self.current = 0  # 0 is [BOF]

    def display(self, index: int) -> None:
        common.write((self.lines[index - 1] if index else BOF_DISPLAY) + b"\n")

    def last(self) -> int:
        return len(self.lines)

    def insert(self, reader: LineReader) -> None:
        while True:
            line = reader.next()
            if line is None or line == b".":
                return
            self.lines.insert(self.current, line)
            self.current += 1

    def run(self, word: bytes, rest: bytes, reader: LineReader) -> bool:
        """Execute one command; return True for q."""
        if word in (b"i", b"q"):
            no_more(rest)
            if word == b"q":
                return True
            self.insert(reader)
        elif word == b"d":
            words = split_words(rest)
            count = parse_count(words[0]) if words else 1
            no_more(b" ".join(words[1:]))
            del self.lines[self.current:self.current + count]
        elif word in (b"t", b"m"):
            words = split_words(rest)
            if not words:
                raise CommandError("missing argument")
            target = words[0]
            if word == b"t" and target in (b".", b"b", b"e"):
                no_more(b" ".join(words[1:]))
                if target == b".":
                    self.display(self.current)
                elif target == b"b":
                    self.current = 0
                    if self.lines:
                        self.display(1)
                else:
                    self.current = self.last()
                    self.display(self.current)
                return False
            count = parse_count(target)
            no_more(b" ".join(words[1:]))
            if word == b"t":
                for index in range(self.current + 1, min(self.current + count, self.last()) + 1):
                    self.display(index)
            else:
                self.current = min(self.current + count, self.last())
                self.display(self.current)
        elif word == b"f":
            pattern, rest = take_string(rest)
            if not pattern:
                raise CommandError("empty pattern")
            no_more(rest)
            for index in range(self.current + 1, self.last() + 1):
                if pattern in self.lines[index - 1]:
                    self.current = index
                    self.display(index)
                    return False
            raise CommandError("pattern not found")
        elif word == b"s":
            old, rest = take_string(rest)
            if not old:
                raise CommandError("empty pattern")
            new, rest = take_string(rest)
            no_more(rest)
            if self.current == 0:
                raise CommandError("no current line")
            line = self.lines[self.current - 1]
            if old not in line:
                raise CommandError("pattern not found")
            self.lines[self.current - 1] = line.replace(old, new, 1)
            self.display(self.current)
        else:
            raise CommandError(b"unknown command '" + word + b"'")
        return False


def edit(path: str, editor: Editor, reader: LineReader, prompting: bool) -> int:
    status = 0
    while True:
        prompt(prompting, COMMAND_PROMPT)
        line = reader.next()
        if line is None:
            raise DataError(SOURCE, reader.end_line(), "unexpected end of input")
        text = line.strip(BLANKS)
        if not text:
            continue
        match = _COMMAND.match(text)
        word, rest = match.group(1), match.group(2)
        number = reader.number
        try:
            quit_now = editor.run(word, rest, reader)
        except CommandError as error:
            data_failure(TOOL, DataError(SOURCE, number, error.message))
            status = 1
            continue
        finally:
            common.out.flush()
        if quit_now:
            try:
                save(path, editor.lines)
            except OSError as error:
                file_failure(TOOL, path, error)
                return 1
            return status


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if not parsed.operands:
            raise UsageError("missing operand")
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    path = parsed.operands[0]
    try:
        editor = Editor(load(path))
    except OSError as error:
        file_failure(TOOL, path, error)
        return 1
    reader = LineReader(sys.stdin.buffer)
    try:
        return edit(path, editor, reader, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except BrokenPipeError:
        raise
    except OSError as error:  # standard input could not be read
        file_failure(TOOL, SOURCE, error)
        return 1

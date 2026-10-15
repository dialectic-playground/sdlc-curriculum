"""Reference implementation of dp-grep (projects/05-grep-lite/specs/SRS.md).

Pattern parsing, validation, and matching live in ``_grep_pattern``; this module handles the
command line, input traversal, and output formatting.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from typing import BinaryIO

from . import common
from ._grep_pattern import LineMatcher, PatternError, literal, parse
from .common import (
    Option,
    UsageError,
    diagnose,
    encode_arg,
    file_error_reason,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    usage_failure,
    write,
)

TOOL = "dp-grep"
STDIN_LABEL = "(standard input)"
HELP_TEXT = """\
Usage: dp-grep [OPTION]... PATTERN [FILE]...
  or:  dp-grep [OPTION]... -e PATTERN... [FILE]...
Search each FILE for lines that match a pattern.

PATTERN is a portable extended regular expression (see the user manual).
With no FILE, read standard input, or the working directory with -r.
A FILE of - means standard input.

Options:
  -e, --regexp=PATTERN      use PATTERN; may be given more than once
  -F, --fixed-strings       treat every PATTERN as a literal string
  -i, --ignore-case         ignore ASCII letter case
  -v, --invert-match        select lines that do not match
  -x, --line-regexp         a pattern must match the whole line
  -w, --word-regexp         a pattern must match a whole word
  -n, --line-number         prefix each selected line with its line number
  -c, --count               print only a count of selected lines per file
  -l, --files-with-matches  print only the names of files with selected lines
  -q, --quiet               print nothing; exit 0 at the first selected line
  -s, --no-messages         suppress diagnostics about unreadable files
  -r, --recursive           search directories recursively
  -H, --with-filename       prefix each output line with the file name
  -h, --no-filename         never prefix output lines with the file name
      --help                display this help and exit
      --version             output version information and exit

Exit status is 0 if a line is selected, 1 if no line is selected, and 2 if an
error occurred; with -q, a selected line gives 0 even after an error.
"""

OPTIONS = [
    Option("regexp", short="e", long="regexp", takes_value=True, repeatable=True),
    Option("fixed", short="F", long="fixed-strings"),
    Option("ignore_case", short="i", long="ignore-case"),
    Option("invert", short="v", long="invert-match"),
    Option("line_regexp", short="x", long="line-regexp"),
    Option("word_regexp", short="w", long="word-regexp"),
    Option("line_number", short="n", long="line-number"),
    Option("count", short="c", long="count"),
    Option("list", short="l", long="files-with-matches"),
    Option("quiet", short="q", long="quiet"),
    Option("no_messages", short="s", long="no-messages"),
    Option("recursive", short="r", long="recursive"),
    # -H and -h share a destination: the one written last wins (SRS FR-15).
    Option("filename", short="H", long="with-filename"),
    Option("filename", short="h", long="no-filename"),
]


class QuietMatch(Exception):
    """Raised under -q at the first selected line: the search stops with status 0."""


@dataclass
class Settings:
    matcher: LineMatcher
    invert: bool
    line_number: bool
    mode: str  # "lines", "count", "list", or "quiet"
    with_filename: bool
    no_messages: bool
    recursive: bool


class Search:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.selected_any = False
        self.error = False

    # --- diagnostics ---------------------------------------------------------------------

    def fail(self, path: str, reason: str) -> None:
        self.error = True
        if not self.settings.no_messages:
            diagnose(TOOL, f"{path}: {reason}")

    # --- one input -----------------------------------------------------------------------

    def search_stream(self, stream: BinaryIO, label: str) -> None:
        settings = self.settings
        prefix = encode_arg(label) + b":" if settings.with_filename else b""
        selected = 0
        for number, line in enumerate(_lines(stream), start=1):
            if settings.matcher.matches(line) == settings.invert:
                continue
            selected += 1
            self.selected_any = True
            if settings.mode == "quiet":
                raise QuietMatch
            if settings.mode == "list":
                break
            if settings.mode == "lines":
                number_field = b"%d:" % number if settings.line_number else b""
                write(prefix + number_field + line + b"\n")
        if settings.mode == "count":
            write(prefix + b"%d\n" % selected)
        elif settings.mode == "list" and selected:
            write(encode_arg(label) + b"\n")

    def search_file(self, path: str, label: str) -> None:
        try:
            with open_input(path) as stream:
                self.search_stream(stream, label)
        except BrokenPipeError:
            raise
        except OSError as error:
            self.error = True
            if not self.settings.no_messages:
                file_failure(TOOL, label, error)

    def search_stdin(self) -> None:
        try:
            self.search_stream(sys.stdin.buffer, STDIN_LABEL)
        except BrokenPipeError:
            raise
        except OSError:
            self.fail(STDIN_LABEL, "Input/output error")

    # --- recursion -----------------------------------------------------------------------

    def walk(self, directory: str, shown: str | None) -> None:
        """Search a directory tree in pre-order with byte-wise sorted entries (CONV-20/21).

        ``shown`` is the displayed directory path; None for the implicit working directory,
        whose entries are displayed without a leading './'.
        """
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: encode_arg(entry.name))
        except OSError as error:
            self.fail(shown if shown is not None else ".", file_error_reason(error))
            return
        for entry in entries:
            path = join_path(directory, entry.name)
            label = entry.name if shown is None else join_path(shown, entry.name)
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    self.walk(path, label)
                elif entry.is_file(follow_symlinks=False):
                    self.search_file(path, label)
            except BrokenPipeError:
                raise
            except OSError as error:
                self.fail(label, file_error_reason(error))

    def search_operand(self, operand: str) -> None:
        if operand == "-":
            self.search_stdin()
        elif self.settings.recursive and os.path.isdir(operand):
            self.walk(operand, operand)
        else:
            self.search_file(operand, operand)


def join_path(directory: str, name: str) -> str:
    """Join with '/', adding no separator after one the user already wrote (SRS FR-17)."""
    separators = ("/", "\\") if os.name == "nt" else ("/",)
    return directory + name if directory.endswith(separators) else f"{directory}/{name}"


def _lines(stream: BinaryIO) -> Iterator[bytes]:
    """Yield each line without its LF; CR bytes are data (CONV-04)."""
    for line in stream:
        yield line[:-1] if line.endswith(b"\n") else line


def output_mode(values: dict[str, object]) -> str:
    for dest, mode in (("quiet", "quiet"), ("list", "list"), ("count", "count")):
        if values.get(dest):
            return mode
    return "lines"


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        operands = list(parsed.operands)
        if "regexp" in parsed.values:
            patterns = [str(p) for p in parsed.values["regexp"]]  # type: ignore
        elif operands:
            patterns = [operands.pop(0)]
        else:
            raise UsageError("missing operand")
    except UsageError as error:
        return usage_failure(TOOL, error)

    values = parsed.values
    trees = []
    for pattern in patterns:
        data = encode_arg(pattern)
        try:
            trees.append(literal(data) if values.get("fixed") else parse(data))
        except PatternError as error:
            common.err.write(
                b"%s: invalid pattern '%s': %s\n" % (TOOL.encode(), data, error.reason)
            )
            return 2

    recursive = bool(values.get("recursive"))
    if "filename" in values:
        with_filename = parsed.spelled["filename"] in ("-H", "--with-filename")
    else:
        with_filename = recursive or len(operands) > 1
    settings = Settings(
        matcher=LineMatcher(
            trees,
            ignore_case=bool(values.get("ignore_case")),
            line_regexp=bool(values.get("line_regexp")),
            word_regexp=bool(values.get("word_regexp")),
        ),
        invert=bool(values.get("invert")),
        line_number=bool(values.get("line_number")),
        mode=output_mode(values),
        with_filename=with_filename,
        no_messages=bool(values.get("no_messages")),
        recursive=recursive,
    )

    search = Search(settings)
    try:
        if not operands and recursive:
            search.walk(".", None)
        for operand in operands or ([] if recursive else ["-"]):
            search.search_operand(operand)
    except QuietMatch:
        return 0
    if search.error:
        return 2
    return 0 if search.selected_any else 1

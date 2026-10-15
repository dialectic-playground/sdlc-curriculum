"""Reference implementation of dp-phone (projects/31-phone/specs/SRS.md).

The whole student file is read and validated before the first query is read. Queries are
read one line at a time, and each answer is written and flushed before the next line is
read, so the tool works interactively.
"""

from __future__ import annotations

import sys

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
    handle_action,
    invalid_argument,
    open_input,
    parse_args,
    prompt,
    read_all,
    strip_eof_marker,
    usage_failure,
)

TOOL = "dp-phone"
DEFAULT_FILE = "students.dat"
PROMPT_TEXT = "Enter a student's name, or signal EOF to halt: "
LNAME_SIZE, FNAME_SIZE, PNUM_SIZE = 25, 25, 12
RECORD_SIZE = LNAME_SIZE + FNAME_SIZE + PNUM_SIZE
HELP_TEXT = """\
Usage: dp-phone [OPTION]... [FILE]
Look up students' telephone numbers by last name.

Load the fixed-width student records (last name in columns 1-25, first name in
columns 26-50, telephone number in columns 51-62), sort them, and then answer
each line of FILE as a last name to look up.  With no FILE, or when FILE is -,
read the names from standard input.  Names are matched exactly, including
case and spaces; a name is reported as 'Record: ' and the student's record, or
as not in the directory.

Options:
  -f, --file=FILE   read the student records from FILE (default students.dat);
                      - means standard input
  -p, --prompt      write a prompt to standard error before each name is read
      --help        display this help and exit
      --version     output version information and exit
"""

OPTIONS: list[Option] = [
    Option("file", short="f", long="file", takes_value=True),
    PROMPT,
]


def strip_cr(line: bytes) -> bytes:
    return line[:-1] if line.endswith(b"\r") else line


def load_records(data: bytes, source: str) -> list[bytes]:
    """Split the student file into 62-byte records (FR-02, FR-03)."""
    data = strip_eof_marker(data)
    if not data:
        return []
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()  # the final line ended with LF
    records = []
    for number, raw in enumerate(lines, start=1):
        record = strip_cr(raw)
        if len(record) != RECORD_SIZE:
            raise DataError(
                source,
                number,
                f"invalid record length {len(record)}, expected {RECORD_SIZE}",
            )
        records.append(record)
    return records


def selection_sort(records: list[bytes]) -> None:
    """Selection sort by whole record, unsigned byte order (FR-04)."""
    count = len(records)
    for i in range(count - 1):
        smallest = i
        for j in range(i + 1, count):
            if records[j] < records[smallest]:
                smallest = j
        records[i], records[smallest] = records[smallest], records[i]


def binary_search(records: list[bytes], key: bytes) -> bytes | None:
    """Binary search on the 25-byte last-name field (FR-06)."""
    low, high = 0, len(records) - 1
    while low <= high:
        mid = (low + high) // 2
        name = records[mid][:LNAME_SIZE]
        if key == name:
            return records[mid]
        if key < name:
            high = mid - 1
        else:
            low = mid + 1
    return None


def answer(records: list[bytes], query: bytes) -> bytes:
    if len(query) <= LNAME_SIZE:
        found = binary_search(records, query.ljust(LNAME_SIZE, b" "))
        if found is not None:
            return b"Record: " + found + b"\n"
    return query + b" is not in our directory.\n"


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
        students = str(parsed.values.get("file", DEFAULT_FILE))
        if students == "":
            raise invalid_argument(students, parsed.spelled["file"])
        queries = parsed.operands[0] if parsed.operands else "-"
        if students == "-" and queries == "-":
            raise invalid_argument(students, parsed.spelled["file"])
    except UsageError as error:
        return usage_failure(TOOL, error)

    prompting = bool(parsed.values.get("prompt"))
    try:
        data = read_all(students)
    except OSError as error:
        file_failure(TOOL, students, error)
        return 1
    try:
        records = load_records(data, students)
    except DataError as error:
        return data_failure(TOOL, error)
    selection_sort(records)

    try:
        handle = open_input(queries)
    except OSError as error:
        file_failure(TOOL, queries, error)
        return 1
    try:
        lines = InputStream(
            handle
        )  # query lines, each as soon as it is complete (FR-05)
        while True:
            prompt(prompting, PROMPT_TEXT)
            try:
                line = lines.read_line()
            except InputError as error:
                file_failure(TOOL, queries, error.error)
                return 1
            if line is None:
                return 0
            query = strip_cr(line.text)
            if query == b"":
                continue
            common.write(answer(records, query))
            common.out.flush()
    finally:
        if handle is not sys.stdin.buffer:
            handle.close()

"""Reference implementation of dp-size (projects/39-size/specs/SRS.md).

Each name gets the extension appended, and the resulting file is opened in binary mode and
counted by reading it to the end in fixed-size chunks. Names come from operands or, for no
operands or the operand ``-``, from the lines of standard input (CONV-37 applies to those lines,
never to the counted files).
"""

from __future__ import annotations

import errno
import os
import sys

from . import common
from .common import (
    PROMPT,
    InputError,
    InputStream,
    Option,
    UsageError,
    encode_arg,
    handle_action,
    invalid_argument,
    parse_args,
    prompt,
    usage_failure,
)

TOOL = "dp-size"
DEFAULT_EXTENSION = ".c"
PROMPT_TEXT = "\tFile name (NO extension):\t"
CHUNK_SIZE = 64 * 1024
HELP_TEXT = """\
Usage: dp-size [OPTION]... [NAME]...
Print the size in bytes of the file NAME.c for each NAME.

Each NAME is a file name without its extension; the extension (.c unless -e
is given) is appended to it, and the file is read to its end in binary mode,
counting every byte.  With no NAME, or when NAME is -, read the names from
standard input, one per line.  For each file, two lines are written:
a TAB, 'File name:', a TAB, and the file name; then a TAB, 'Byte size:', a
TAB, and the number of bytes.

Options:
  -e, --extension=EXT   append EXT instead of .c; EXT is empty or begins
                          with '.'
  -p, --prompt          write the prompt 'File name (NO extension):' to
                          standard error before each name is read
      --help            display this help and exit
      --version         output version information and exit
"""

OPTIONS = [Option("extension", short="e", long="extension", takes_value=True), PROMPT]


class Session:
    def __init__(self, extension: bytes, prompting: bool):
        self.extension = extension
        self.prompting = prompting
        self.failed = False
        self.stdin: InputStream | None = (
            None  # opened by the first read of names (FR-01)
        )

    def measure(self, name: bytes) -> None:
        path = name + self.extension
        try:
            os_path = os.fsdecode(path) if os.name != "nt" else path.decode("utf-8")
        except UnicodeDecodeError:
            self.fail_path(path, "No such file or directory")
            return
        try:
            if os.path.isdir(os_path):
                raise IsADirectoryError(os_path)
            handle = open(os_path, "rb")  # noqa: SIM115
        except OSError as error:
            # A name the platform rejects as malformed (EINVAL, for example a control
            # character in a Windows file name) cannot exist: SRS FR-07.
            invalid = error.errno == errno.EINVAL
            reason = common.file_error_reason(error, os_path)
            self.fail_path(path, "No such file or directory" if invalid else reason)
            return
        count = 0
        try:
            with handle:
                while True:
                    chunk = handle.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    count += len(chunk)
        except OSError:
            self.fail_path(path, "Input/output error")
            return
        common.write(
            b"\tFile name:\t" + path + b"\n\tByte size:\t" + str(count).encode() + b"\n"
        )
        common.out.flush()

    def fail_path(self, path: bytes, reason: str) -> None:
        self.failed = True
        common.err.write(f"{TOOL}: ".encode() + path + f": {reason}\n".encode())

    def fail_line(self, line: int, message: str) -> None:
        self.failed = True
        common.err.write(f"{TOOL}: -:{line}: {message}\n".encode())

    def read_stdin_names(self) -> None:
        if self.stdin is None:
            self.stdin = InputStream(sys.stdin.buffer)
        while True:
            prompt(self.prompting, PROMPT_TEXT)
            try:
                line = self.stdin.read_line()
            except InputError:
                self.failed = True
                common.diagnose(TOOL, "-: Input/output error")
                return
            if line is None:
                return
            name = line.text[:-1] if line.text.endswith(b"\r") else line.text
            if not name:
                self.fail_line(line.line, "empty file name")
            elif b"\x00" in name:
                self.fail_line(line.line, "file name contains a NUL byte")
            else:
                self.measure(name)


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        extension = str(parsed.values.get("extension", DEFAULT_EXTENSION))
        if extension and not extension.startswith("."):
            raise invalid_argument(extension, parsed.spelled["extension"])
    except UsageError as error:
        return usage_failure(TOOL, error)

    session = Session(encode_arg(extension), bool(parsed.values.get("prompt")))
    for operand in parsed.operands or ["-"]:
        if operand == "-":
            session.read_stdin_names()
        elif operand == "":
            session.failed = True
            common.diagnose(TOOL, "empty file name")
        else:
            session.measure(encode_arg(operand))
    return 1 if session.failed else 0

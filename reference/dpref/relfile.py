"""Reference implementation of dp-relfile (projects/40-relative-file/specs/SRS.md).

The relative file holds 100 slots of 35 bytes: a status byte (``0`` free, ``1`` taken, ``2``
deleted), a 4-digit key, and 30 bytes of space-padded data. A key's home slot is key mod 97;
collisions are resolved by linear probing with wrap-around. Every operation reads and writes
single records at their byte offsets; the whole file is read once, at start-up, only to
validate it.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from . import common
from .common import (PROMPT, InputStream, Option, UsageError, handle_action, invalid_argument,
                     parse_args, prompt, usage_failure)

TOOL = "dp-relfile"
DEFAULT_FILE = "relative.dat"
SLOTS = 100
RECORD_SIZE = 35
KEY_SIZE = 4
DATA_SIZE = 30
FILE_SIZE = SLOTS * RECORD_SIZE
DIVISOR = 97
FREE, TAKEN, DELETED = b"0", b"1", b"2"
STATUS_WORDS = {TAKEN: "taken", DELETED: "deleted"}

MENU_PROMPT = ("\t\t\t1   -- add a record\n"
               "\t\t\t2   -- find a record\n"
               "\t\t\t3   -- remove a record\n"
               "\t\t\t0   -- exit the program\n"
               "\n"
               "\t\t\tPlease pick a number:   ")
KEY_PROMPT = "\t\t\tEnter key (4 digits):   "
DATA_PROMPT = "\t\t\tEnter data (up to 30 characters):   "

HELP_TEXT = """\
Usage: dp-relfile [OPTION]... [COMMAND [ARG]...]
Keep records in a relative file: 100 slots of 35 bytes, addressed by hashing.

Each record has a key of exactly 4 digits and up to 30 characters of data
(printable ASCII; trailing spaces are not kept).  A key's home slot is the key
modulo 97; a collision moves on to the next slot, wrapping from 99 to 0.  A
removed record leaves a tombstone that a later add can reuse.  The file is
created, with 100 free slots, if it does not exist.

Commands:
  add KEY DATA    add a record
  find KEY        print the record with key KEY
  remove KEY      remove the record with key KEY
  slots           list every slot that is not free

With no COMMAND, run the menu dialog: read the choices (1 add, 2 find,
3 remove, 0 exit), keys, and data from standard input, one per line.

Options:
  -f, --file=FILE   use the relative file FILE (default relative.dat)
  -p, --prompt      in the menu dialog, write the menu and prompts to
                      standard error before each line is read
      --help        display this help and exit
      --version     output version information and exit
"""

OPTIONS = [Option("file", short="f", long="file", takes_value=True), PROMPT]
COMMAND_ARITY = {"add": 2, "find": 1, "remove": 1, "slots": 0}


class CorruptFile(Exception):
    """The relative file is not valid; ``str(error)`` is the CONV-16-style reason."""


class StdinError(Exception):
    """Standard input could not be read (reported as ``-: Input/output error``)."""


class InputError(Exception):
    """A malformed key or data value; ``str(error)`` is the message."""


def check_key(text: bytes) -> bytes:
    if len(text) != KEY_SIZE or not all(0x30 <= b <= 0x39 for b in text):
        raise InputError(b"invalid key '" + text + b"'")
    return text


def check_data(text: bytes) -> bytes:
    text = text.rstrip(b" ")
    if any(not 0x20 <= b <= 0x7E for b in text):
        raise InputError(b"invalid character in data")
    if len(text) > DATA_SIZE:
        raise InputError(b"data too long (maximum 30 characters)")
    return text


def home_slot(key: bytes) -> int:
    return int(key) % DIVISOR


@dataclass
class Located:
    found: int | None  # slot holding the key, if any
    insert: int | None  # slot an add would use (first tombstone or the free slot), if any


class RelativeFileError(Exception):
    """An I/O failure on the relative file itself, kept apart from standard-output failures."""


class RelativeFile:
    def __init__(self, handle):
        self.handle = handle

    def read_record(self, slot: int) -> bytes:
        try:
            self.handle.seek(slot * RECORD_SIZE)
            return self.handle.read(RECORD_SIZE)
        except OSError as error:
            raise RelativeFileError() from error

    def write(self, slot: int, data: bytes) -> None:
        try:
            self.handle.seek(slot * RECORD_SIZE)
            self.handle.write(data)
            self.handle.flush()
        except OSError as error:
            raise RelativeFileError() from error

    def locate(self, key: bytes) -> Located:
        first_tombstone = None
        slot = home_slot(key)
        for _ in range(SLOTS):
            record = self.read_record(slot)
            status = record[:1]
            if status == FREE:
                return Located(None, first_tombstone if first_tombstone is not None else slot)
            if status == TAKEN and record[1:1 + KEY_SIZE] == key:
                return Located(slot, None)
            if status == DELETED and first_tombstone is None:
                first_tombstone = slot
            slot = (slot + 1) % SLOTS
        return Located(None, first_tombstone)


def validate(data: bytes) -> None:
    if len(data) != FILE_SIZE:
        raise CorruptFile(f"not a relative file (size {len(data)}, expected {FILE_SIZE})")
    for slot in range(SLOTS):
        record = data[slot * RECORD_SIZE:(slot + 1) * RECORD_SIZE]
        status, rest = record[:1], record[1:]
        if status == FREE:
            ok = rest == b" " * (RECORD_SIZE - 1)
        elif status in (TAKEN, DELETED):
            key, value = rest[:KEY_SIZE], rest[KEY_SIZE:]
            ok = (all(0x30 <= b <= 0x39 for b in key)
                  and all(0x20 <= b <= 0x7E for b in value))
        else:
            ok = False
        if not ok:
            raise CorruptFile(f"slot {slot}: invalid record")


class Session:
    def __init__(self, rel: RelativeFile):
        self.rel = rel
        self.failed = False

    def fail(self, message: bytes) -> None:
        self.failed = True
        common.err.write(TOOL.encode() + b": " + message + b"\n")

    def add(self, key: bytes, data: bytes) -> None:
        where = self.rel.locate(key)
        if where.found is not None:
            self.fail(b"cannot add " + key + b": duplicate key")
        elif where.insert is None:
            self.fail(b"cannot add " + key + b": file is full")
        else:
            self.rel.write(where.insert, TAKEN + key + data.ljust(DATA_SIZE, b" "))
            common.write(b"Added " + key + b" in slot " + str(where.insert).encode() + b"\n")

    def find(self, key: bytes) -> None:
        where = self.rel.locate(key)
        if where.found is None:
            self.fail(b"cannot find " + key + b": no such record")
            return
        data = self.rel.read_record(where.found)[1 + KEY_SIZE:].rstrip(b" ")
        line = b"Found " + key + b" in slot " + str(where.found).encode() + b":"
        common.write(line + (b" " + data if data else b"") + b"\n")

    def remove(self, key: bytes) -> None:
        where = self.rel.locate(key)
        if where.found is None:
            self.fail(b"cannot remove " + key + b": no such record")
            return
        self.rel.write(where.found, DELETED)
        common.write(b"Removed " + key + b" from slot " + str(where.found).encode() + b"\n")

    def slots(self) -> None:
        for slot in range(SLOTS):
            record = self.rel.read_record(slot)
            word = STATUS_WORDS.get(record[:1])
            if word is None:
                continue
            key = record[1:1 + KEY_SIZE]
            data = record[1 + KEY_SIZE:].rstrip(b" ")
            line = f"{slot} {word} ".encode() + key
            common.write(line + (b" " + data if data else b"") + b"\n")


class Dialog:
    """The menu dialog of FR-12: line-oriented responses from standard input."""

    def __init__(self, session: Session, prompting: bool):
        self.session = session
        self.prompting = prompting
        self.stream = InputStream(sys.stdin.buffer)
        self.line = 0  # line number of the last response read

    def read_response(self, text: str) -> bytes | None:
        """Prompt, then read one line without its LF and one CR before it; None at the end."""
        prompt(self.prompting, text)
        try:
            response = self.stream.read_line()
        except common.InputError:
            raise StdinError() from None
        if response is None:
            return None
        self.line = response.line
        raw = response.text
        return raw[:-1] if raw.endswith(b"\r") else raw

    def data_error(self, line: int, message: bytes) -> int:
        common.err.write(f"{TOOL}: -:{line}: ".encode() + message + b"\n")
        return 1

    def run(self) -> int:
        try:
            return self.converse()
        except StdinError:
            common.diagnose(TOOL, "-: Input/output error")
            return 1

    def converse(self) -> int:
        while True:
            choice = self.read_response(MENU_PROMPT)
            if choice is None:
                break
            choice = choice.strip(b" \t")
            if choice == b"0":
                break
            if choice not in (b"1", b"2", b"3"):
                return self.data_error(self.line, b"invalid choice '" + choice + b"'")
            try:
                key = self.read_response(KEY_PROMPT)
                if key is None:
                    return self.data_error(self.stream.line, b"unexpected end of input")
                key = check_key(key.strip(b" \t"))
                data = b""
                if choice == b"1":
                    data = self.read_response(DATA_PROMPT)
                    if data is None:
                        return self.data_error(self.stream.line, b"unexpected end of input")
                    data = check_data(data)
            except InputError as error:
                return self.data_error(self.line, error.args[0])
            if choice == b"1":
                self.session.add(key, data)
            elif choice == b"2":
                self.session.find(key)
            else:
                self.session.remove(key)
            common.out.flush()
        return 1 if self.session.failed else 0


def open_relative(path: str, writable: bool):
    """Open (creating and initializing if missing) and validate the relative file."""
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    if not os.path.exists(path):
        with open(path, "xb") as handle:
            handle.write((FREE + b" " * (RECORD_SIZE - 1)) * SLOTS)
    handle = open(path, "r+b" if writable else "rb")
    try:
        validate(handle.read())
    except BaseException:
        handle.close()
        raise
    return handle


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        path = str(parsed.values.get("file", DEFAULT_FILE))
        if path == "":
            raise invalid_argument(path, parsed.spelled["file"])
        command, args = None, []
        if parsed.operands:
            command, args = parsed.operands[0], parsed.operands[1:]
            if command not in COMMAND_ARITY:
                raise UsageError(f"unknown command '{command}'")
            arity = COMMAND_ARITY[command]
            if len(args) < arity:
                raise UsageError("missing operand")
            if len(args) > arity:
                raise UsageError(f"extra operand '{args[arity]}'")
            values = [common.encode_arg(a) for a in args]
            try:
                if command in ("add", "find", "remove"):
                    values[0] = check_key(values[0])
                if command == "add":
                    values[1] = check_data(values[1])
            except InputError as error:
                raise UsageError(error.args[0].decode("utf-8", "surrogateescape")) from None
    except UsageError as error:
        return usage_failure(TOOL, error)

    writable = command in (None, "add", "remove")
    try:
        handle = open_relative(path, writable)
    except CorruptFile as error:
        common.diagnose(TOOL, f"{path}: {error}")
        return 1
    except OSError as error:
        common.file_failure(TOOL, path, error)
        return 1
    try:
        with handle:
            session = Session(RelativeFile(handle))
            if command is None:
                return Dialog(session, bool(parsed.values.get("prompt"))).run()
            if command == "add":
                session.add(values[0], values[1])
            elif command == "find":
                session.find(values[0])
            elif command == "remove":
                session.remove(values[0])
            else:
                session.slots()
            return 1 if session.failed else 0
    except RelativeFileError:
        common.diagnose(TOOL, f"{path}: Input/output error")
        return 1

"""Command driver and ADTs shared by dp-queue1, dp-queue2, dp-stack1, and dp-stack2
(projects/45-queue-stack).

Each tool is the same command dialog bound to a different ADT implementation: a circular
array queue of capacity 100, a linked queue, an array stack of capacity 100, or a linked
stack. The driver uses only the ADT interface (insert/remove, iterate), so the array and
linked tools of a kind behave identically until an array is full.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import Iterator

from .common import (PROMPT, DataError, InputError, InputStream, Token, UsageError,
                     data_failure, file_failure, handle_action, open_input, out, parse_args,
                     parse_int_token, prompt, usage_failure, write, INT64_MAX)

CAPACITY = 100
_AMOUNT = re.compile(rb"([+-]?)([0-9]+)(?:\.([0-9]{1,2}))?\Z")
MAX_CENTS = 99_999_999_999_999_999  # 999999999999999.99


def parse_amount(token: Token, source: str) -> int:
    """A balance in cents: [+-]?digits[.d[d]], magnitude at most 999999999999999.99."""
    match = _AMOUNT.match(token.text)
    if not match:
        raise DataError(source, token.line, b"invalid amount '" + token.text + b"'")
    sign, whole, fraction = match.groups()
    cents = int(whole) * 100 + int((fraction or b"").ljust(2, b"0"))
    if cents > MAX_CENTS:
        raise DataError(source, token.line, b"value out of range '" + token.text + b"'")
    return -cents if sign == b"-" else cents


def format_amount(cents: int) -> bytes:
    sign = b"-" if cents < 0 else b""
    whole, fraction = divmod(abs(cents), 100)
    return sign + str(whole).encode() + b"." + str(fraction).zfill(2).encode()


# --- records ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Customer:
    last: bytes
    first: bytes
    account: int
    balance: int  # cents

    def text(self) -> bytes:
        return (self.last + b", " + self.first + b"; account " + str(self.account).encode()
                + b"; balance " + format_amount(self.balance))


@dataclass(frozen=True)
class Tray:
    color: bytes
    ident: int

    def text(self) -> bytes:
        return b"color " + self.color + b", id " + str(self.ident).encode()


# --- ADTs ------------------------------------------------------------------------------

class ArrayQueue:
    def __init__(self) -> None:
        self.slots: list[object] = [None] * CAPACITY
        self.front = 0
        self.count = 0

    def insert(self, item: object) -> bool:
        if self.count == CAPACITY:
            return False
        self.slots[(self.front + self.count) % CAPACITY] = item
        self.count += 1
        return True

    def remove(self) -> object | None:
        if self.count == 0:
            return None
        item = self.slots[self.front]
        self.slots[self.front] = None
        self.front = (self.front + 1) % CAPACITY
        self.count -= 1
        return item

    def items(self) -> Iterator[object]:
        for offset in range(self.count):
            yield self.slots[(self.front + offset) % CAPACITY]


@dataclass
class _Node:
    item: object
    link: "_Node | None" = None


class LinkedQueue:
    def __init__(self) -> None:
        self.front: _Node | None = None
        self.rear: _Node | None = None

    def insert(self, item: object) -> bool:
        node = _Node(item)
        if self.rear is None:
            self.front = node
        else:
            self.rear.link = node
        self.rear = node
        return True

    def remove(self) -> object | None:
        if self.front is None:
            return None
        node = self.front
        self.front = node.link
        if self.front is None:
            self.rear = None
        return node.item

    def items(self) -> Iterator[object]:
        node = self.front
        while node is not None:
            yield node.item
            node = node.link


class ArrayStack:
    def __init__(self) -> None:
        self.slots: list[object] = [None] * CAPACITY
        self.top = -1

    def insert(self, item: object) -> bool:
        if self.top == CAPACITY - 1:
            return False
        self.top += 1
        self.slots[self.top] = item
        return True

    def remove(self) -> object | None:
        if self.top == -1:
            return None
        item = self.slots[self.top]
        self.slots[self.top] = None
        self.top -= 1
        return item

    def items(self) -> Iterator[object]:
        for index in range(self.top, -1, -1):
            yield self.slots[index]


class LinkedStack:
    def __init__(self) -> None:
        self.top: _Node | None = None

    def insert(self, item: object) -> bool:
        self.top = _Node(item, self.top)
        return True

    def remove(self) -> object | None:
        if self.top is None:
            return None
        node = self.top
        self.top = node.link
        return node.item

    def items(self) -> Iterator[object]:
        node = self.top
        while node is not None:
            yield node.item
            node = node.link


# --- the dialog ------------------------------------------------------------------------

@dataclass(frozen=True)
class Kind:
    """What distinguishes the queue dialog from the stack dialog."""

    menu_prompt: str
    record_prompt: str
    removed_label: bytes
    full: bytes
    empty: bytes
    is_queue: bool


QUEUE = Kind("Enter 1 (insert), 2 (remove), 3 (display), 0 (quit): ",
             "Enter last name, first name, account number, balance: ",
             b"Removed: ", b"QUEUE FULL", b"QUEUE EMPTY", True)
STACK = Kind("Enter 1 (push), 2 (pop), 3 (display), 0 (quit): ",
             "Enter color, id: ",
             b"Popped: ", b"STACK FULL", b"STACK EMPTY", False)


def read_record(kind: Kind, reader: InputStream, source: str) -> object:
    if kind.is_queue:
        last = reader.require(source).text
        first = reader.require(source).text
        account = parse_int_token(reader.require(source), source, 0, INT64_MAX)
        balance = parse_amount(reader.require(source), source)
        return Customer(last, first, account, balance)
    color = reader.require(source).text
    ident = parse_int_token(reader.require(source), source, 0, INT64_MAX)
    return Tray(color, ident)


def session(kind: Kind, adt: object, reader: InputStream, source: str, prompts: bool) -> None:
    while True:
        prompt(prompts, kind.menu_prompt)
        token = reader.token()
        if token is None:
            return
        command = parse_int_token(token, source, 0, 3)
        if command == 0:
            return
        if command == 1:
            prompt(prompts, kind.record_prompt)
            record = read_record(kind, reader, source)
            if not adt.insert(record):  # type: ignore[attr-defined]
                write(kind.full + b"\n")
        elif command == 2:
            item = adt.remove()  # type: ignore[attr-defined]
            if item is None:
                write(kind.empty + b"\n")
            else:
                write(kind.removed_label + item.text() + b"\n")  # type: ignore[attr-defined]
        else:
            position = 0
            for item in adt.items():  # type: ignore[attr-defined]
                position += 1
                write(str(position).encode() + b": " + item.text() + b"\n")
            if position == 0:
                write(kind.empty + b"\n")
        out.flush()


def run_tool(tool: str, help_text: str, kind: Kind, adt_class: type, argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(tool, parsed, help_text):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(tool, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        stream = open_input(source)
    except OSError as error:
        file_failure(tool, source, error)
        return 1
    try:
        session(kind, adt_class(), InputStream(stream), source,
                bool(parsed.values.get("prompt")))
    except DataError as error:
        out.flush()
        return data_failure(tool, error)
    except InputError as failure:
        out.flush()
        file_failure(tool, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0

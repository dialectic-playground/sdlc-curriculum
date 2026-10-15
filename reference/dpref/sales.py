"""Reference implementation of dp-sales (projects/42-sales-report/specs/SRS.md).

Both input files are read and validated completely before the report is written, so a bad
input never produces a partial report. Amounts are exact decimals held as whole cents.
"""

from __future__ import annotations

import re
from bisect import bisect_left
from dataclasses import dataclass

from . import common
from .common import (
    WHITESPACE,
    DataError,
    Option,
    UsageError,
    data_failure,
    file_failure,
    handle_action,
    invalid_argument,
    parse_args,
    read_all,
    strip_eof_marker,
    usage_failure,
)

TOOL = "dp-sales"
DEFAULT_ACCOUNTS = "sales.dat"
DEFAULT_SALESPEOPLE = "sper.dat"
MAX_ACCOUNTS = 100
MAX_SALESPEOPLE = 100
_AMOUNT = re.compile(rb"([0-9]+)(?:\.([0-9]{1,2}))?\Z")
_INTEGER = re.compile(rb"[+-]?[0-9]+\Z")
INT64_MAX = 2**63 - 1
HELP_TEXT = """\
Usage: dp-sales [OPTION]...
Print the sales report by salesperson from an accounts file and a
salesperson file.

Each line of the accounts file (default sales.dat) describes one account:
  ID NAME ACTUAL PROJECTED
Each line of the salesperson file (default sper.dat) describes one
salesperson and lists the ids of the accounts the salesperson manages:
  NAME COACH REGION SALARY BONUS # ID...
Ids are whole numbers; amounts have at most two decimals.  Salespeople are
listed in order of name, each with the accounts in the order listed.  Both
files are checked completely before the report is written.

Options:
  -a, --accounts=FILE      read the accounts from FILE (default sales.dat);
                             - means standard input
  -s, --salespeople=FILE   read the salespeople from FILE (default sper.dat);
                             - means standard input
      --help               display this help and exit
      --version            output version information and exit
"""

OPTIONS = [
    Option("accounts", short="a", long="accounts", takes_value=True),
    Option("salespeople", short="s", long="salespeople", takes_value=True),
]


@dataclass
class Account:
    ident: int
    name: bytes
    actual: int  # cents
    projected: int  # cents


@dataclass
class Salesperson:
    name: bytes
    coach: bytes
    region: bytes
    salary: int
    bonus: int
    accounts: list[Account]


def records(data: bytes) -> list[tuple[int, list[bytes]]]:
    """Non-blank lines as (line number, fields); CR, TAB, VT, FF, and space separate fields."""
    result = []
    for number, line in enumerate(data.split(b"\n"), start=1):
        fields = _fields(line)
        if fields:
            result.append((number, fields))
    return result


def _fields(line: bytes) -> list[bytes]:
    fields, current = [], bytearray()
    for byte in line:
        if byte in WHITESPACE:
            if current:
                fields.append(bytes(current))
                current.clear()
        else:
            current.append(byte)
    if current:
        fields.append(bytes(current))
    return fields


def error(source: str, line: int, text: str, token: bytes | None = None) -> DataError:
    message = text.encode() if token is None else text.encode() + b" '" + token + b"'"
    return DataError(source, line, message)


def parse_id(token: bytes, source: str, line: int) -> int:
    if not _INTEGER.match(token) or not -INT64_MAX - 1 <= int(token) <= INT64_MAX:
        raise error(source, line, "invalid integer", token)
    value = int(token)
    if value < 0:
        raise error(source, line, "value out of range", token)
    return value


def parse_amount(token: bytes, source: str, line: int) -> int:
    match = _AMOUNT.match(token)
    if not match:
        raise error(source, line, "invalid amount", token)
    cents = int(match.group(1)) * 100 + int((match.group(2) or b"0").ljust(2, b"0"))
    if cents > INT64_MAX:
        raise error(source, line, "value out of range", token)
    return cents


def money(cents: int) -> bytes:
    return f"{cents // 100}.{cents % 100:02d}".encode()


def load_accounts(data: bytes, source: str) -> list[Account]:
    accounts: list[Account] = []
    seen: set[int] = set()
    for line, fields in records(data):
        if len(accounts) == MAX_ACCOUNTS:
            raise error(source, line, f"too many accounts (limit {MAX_ACCOUNTS})")
        ident = parse_id(fields[0], source, line)
        if len(fields) < 2:
            raise error(source, line, "incomplete record")
        name = fields[1]
        if len(fields) < 3:
            raise error(source, line, "incomplete record")
        actual = parse_amount(fields[2], source, line)
        if len(fields) < 4:
            raise error(source, line, "incomplete record")
        projected = parse_amount(fields[3], source, line)
        if len(fields) > 4:
            raise error(source, line, "unexpected field", fields[4])
        if ident in seen:
            raise error(source, line, "duplicate account id", fields[0])
        seen.add(ident)
        accounts.append(Account(ident, name, actual, projected))
    return sorted(accounts, key=lambda account: account.ident)


def find_account(
    accounts: list[Account], keys: list[int], ident: int
) -> Account | None:
    index = bisect_left(keys, ident)
    if index < len(keys) and keys[index] == ident:
        return accounts[index]
    return None


def load_salespeople(
    data: bytes, source: str, accounts: list[Account]
) -> list[Salesperson]:
    keys = [account.ident for account in accounts]
    people: list[Salesperson] = []
    for line, fields in records(data):
        if len(people) == MAX_SALESPEOPLE:
            raise error(source, line, f"too many salespeople (limit {MAX_SALESPEOPLE})")
        if len(fields) < 4:
            raise error(source, line, "incomplete record")
        salary = parse_amount(fields[3], source, line)
        if len(fields) < 5:
            raise error(source, line, "incomplete record")
        bonus = parse_amount(fields[4], source, line)
        if len(fields) < 6:
            raise error(source, line, "incomplete record")
        if fields[5] != b"#":
            raise error(source, line, "expected '#' but found", fields[5])
        listed: list[Account] = []
        for token in fields[6:]:
            account = find_account(accounts, keys, parse_id(token, source, line))
            if account is None:
                raise error(source, line, "unknown account", token)
            if any(other is account for other in listed):
                raise error(source, line, "account listed twice", token)
            listed.append(account)
        people.append(
            Salesperson(fields[0], fields[1], fields[2], salary, bonus, listed)
        )
    return sorted(
        people, key=lambda person: person.name
    )  # stable: ties keep file order


def report(people: list[Salesperson]) -> bytes:
    pad, deep = b" " * 8, b" " * 16
    parts = [b"Sales report by salesperson:\n\n"]
    for person in people:
        parts += [
            pad,
            b"Salesperson:  ",
            person.name,
            b"\n",
            pad,
            b"Sales coach:  ",
            person.coach,
            b"\n",
            pad,
            b"Sales region: ",
            person.region,
            b"\n",
            pad,
            b"Base salary and bonus:  ",
            money(person.salary),
            b"  ",
            money(person.bonus),
            b"\n",
            pad,
            str(len(person.accounts)).encode(),
            b" Account(s): \n\n",
        ]
        for account in person.accounts:
            parts += [
                deep,
                b"Name:       ",
                account.name,
                b"\n",
                deep,
                b"Id:         ",
                str(account.ident).encode(),
                b"\n",
                deep,
                b"Projected:  ",
                money(account.projected),
                b"\n",
                deep,
                b"Actual:     ",
                money(account.actual),
                b"\n\n",
            ]
    return b"".join(parts)


def path_option(parsed: common.Parsed, dest: str, default: str) -> str:
    value = str(parsed.values.get(dest, default))
    if value == "":
        raise invalid_argument(value, parsed.spelled[dest])
    return value


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
        accounts_path = path_option(parsed, "accounts", DEFAULT_ACCOUNTS)
        people_path = path_option(parsed, "salespeople", DEFAULT_SALESPEOPLE)
        if accounts_path == "-" and people_path == "-":
            raise invalid_argument("-", parsed.spelled["salespeople"])
    except UsageError as usage:
        return usage_failure(TOOL, usage)

    try:
        try:
            data = strip_eof_marker(read_all(accounts_path))
        except OSError as failure:
            file_failure(TOOL, accounts_path, failure)
            return 1
        accounts = load_accounts(data, accounts_path)
        try:
            data = strip_eof_marker(read_all(people_path))
        except OSError as failure:
            file_failure(TOOL, people_path, failure)
            return 1
        people = load_salespeople(data, people_path, accounts)
    except DataError as failure:
        return data_failure(TOOL, failure)
    common.write(report(people))
    return 0

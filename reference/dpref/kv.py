"""Reference implementation of dp-kv (projects/09-kv-store/specs/SRS.md).

Command-line front end: global option parsing, command dispatch, and argument validation.
The storage engine lives in ``_kv_store`` and the HTTP server in ``_kv_http``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

from . import common
from ._kv_store import (INVALID_STORE_REASON, MAX_VALUE_BYTES, Data, Store, StoreError,
                        encode_document, is_valid_key, is_valid_prefix, parse_document,
                        sorted_keys, value_problem)
from .common import (Option, UsageError, diagnose, file_error_reason, handle_action,
                     invalid_argument, open_input, parse_args, parse_count, usage_failure,
                     write)

TOOL = "dp-kv"
DEFAULT_STORE = "kv.json"
STORE_ENV = "DP_KV_STORE"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7700
HELP_TEXT = """\
Usage: dp-kv [--store=PATH] COMMAND [ARG]...
Store text values under keys in a local JSON file, or serve them over HTTP.

Commands:
  set KEY VALUE             store VALUE under KEY, replacing any previous value
  get KEY                   print the value stored under KEY
  del KEY                   remove KEY and its value
  list [--prefix=P]         print the keys in byte order, one per line
  export                    print the whole store as canonical JSON
  import [--replace] FILE   merge the store document FILE (- for stdin) in
  serve [--host=ADDR] [--port=N]
                            serve the store over HTTP until interrupted

The store is PATH if --store is given, else $DP_KV_STORE if it is set and not
empty, else kv.json. Keys are 1-256 characters from A-Z a-z 0-9 . _ : - and
values are UTF-8 text of at most 65536 bytes. Global options go before
COMMAND; command options go after it. Use -- before a VALUE that starts with -.

Global options:
  -s, --store=PATH          use the store file PATH
      --help                display this help and exit
      --version             output version information and exit

Command options:
  -p, --prefix=P            list: only keys that start with P
  -r, --replace             import: replace all contents instead of merging
      --host=ADDR           serve: IP address to listen on (default 127.0.0.1)
      --port=N              serve: TCP port, 0 for any free one (default 7700)
"""

GLOBAL_OPTIONS = [Option("store", short="s", long="store", takes_value=True)]


class Failure(Exception):
    """A runtime failure (exit 1); ``str(error)`` is the diagnostic without the prefix."""


@dataclass(frozen=True)
class Command:
    operands: tuple[str, ...]  # operand names; FILE/KEY/VALUE are all required
    run: Callable[["Invocation"], None]
    options: list[Option] = field(default_factory=list)


@dataclass
class Invocation:
    store: Store
    values: dict[str, object]
    operands: list[str]


# --- commands ------------------------------------------------------------------------------

def run_set(inv: Invocation) -> None:
    key, value = inv.operands

    def assign(data: Data) -> tuple[bool, None]:
        data[key] = value
        return True, None

    inv.store.update(assign)


def run_get(inv: Invocation) -> None:
    (key,) = inv.operands
    data = inv.store.read()
    if key not in data:
        raise Failure(f"key not found: {key}")
    write(data[key].encode("utf-8") + b"\n")


def run_del(inv: Invocation) -> None:
    (key,) = inv.operands

    def remove(data: Data) -> tuple[bool, bool]:
        if key not in data:
            return False, False
        del data[key]
        return True, True

    if not inv.store.update(remove):
        raise Failure(f"key not found: {key}")


def run_list(inv: Invocation) -> None:
    prefix = str(inv.values.get("prefix", ""))
    data = inv.store.read()
    write("".join(f"{key}\n" for key in sorted_keys(data) if key.startswith(prefix)).encode())


def run_export(inv: Invocation) -> None:
    write(encode_document(inv.store.read()))


def run_import(inv: Invocation) -> None:
    (source,) = inv.operands
    try:
        with open_input(source) as handle:
            raw = handle.read()
    except OSError as error:
        raise Failure(f"{source}: {file_error_reason(error, source)}") from None
    incoming = parse_document(raw)
    if incoming is None:
        raise Failure(f"{source}: {INVALID_STORE_REASON}")
    replace = bool(inv.values.get("replace"))

    def merge(data: Data) -> tuple[bool, None]:
        if replace:
            data.clear()
        data.update(incoming)
        return True, None

    inv.store.update(merge)


def run_serve(inv: Invocation) -> None:
    from ._kv_http import authority, listen_reason, serve  # only serve needs http.server

    host = str(inv.values.get("host", DEFAULT_HOST))
    port = int(inv.values.get("port", DEFAULT_PORT))  # type: ignore[arg-type]

    def announce(message: str) -> None:
        diagnose(TOOL, message)
        common.err.flush()

    try:
        serve(inv.store, host, port, announce)
    except OSError as error:
        reason = listen_reason(error)
        raise Failure(f"{authority(host, port)}: cannot listen: {reason}") from None


COMMANDS: dict[str, Command] = {
    "set": Command(("KEY", "VALUE"), run_set),
    "get": Command(("KEY",), run_get),
    "del": Command(("KEY",), run_del),
    "list": Command((), run_list, [Option("prefix", short="p", long="prefix",
                                          takes_value=True)]),
    "export": Command((), run_export),
    "import": Command(("FILE",), run_import, [Option("replace", short="r", long="replace")]),
    "serve": Command((), run_serve, [Option("host", long="host", takes_value=True),
                                     Option("port", long="port", takes_value=True)]),
}


# --- argument handling ---------------------------------------------------------------------

def validate(name: str, command: Command, parsed: common.Parsed) -> None:
    """Usage checks after option syntax, in SRS FR-02 order: operands, options, KEY, VALUE."""
    operands = parsed.operands
    if len(operands) < len(command.operands):
        raise UsageError("missing operand")
    if len(operands) > len(command.operands):
        raise UsageError(f"extra operand '{operands[len(command.operands)]}'")
    values = parsed.values
    if name == "list" and not is_valid_prefix(str(values.get("prefix", ""))):
        raise invalid_argument(str(values["prefix"]), parsed.spelled["prefix"])
    if name == "serve":
        from ._kv_http import is_valid_host
        if "host" in values and not is_valid_host(str(values["host"])):
            raise invalid_argument(str(values["host"]), parsed.spelled["host"])
        if "port" in values:
            values["port"] = parse_count(str(values["port"]), parsed.spelled["port"],
                                         minimum=0, maximum=65535)
    if "KEY" in command.operands and not is_valid_key(operands[0]):
        raise UsageError(f"invalid key '{operands[0]}'")
    if "VALUE" in command.operands:
        problem = value_problem(operands[1])
        if problem == "utf8":
            raise UsageError("value is not valid UTF-8")
        if problem == "length":
            raise UsageError(f"value too long (maximum {MAX_VALUE_BYTES} bytes)")


def resolve_store_path(values: dict[str, object]) -> str:
    if "store" in values:
        return str(values["store"])
    return os.environ.get(STORE_ENV) or DEFAULT_STORE


def main(argv: list[str]) -> int:
    try:
        top = parse_args(argv, GLOBAL_OPTIONS, permute=False)
        if handle_action(TOOL, top, HELP_TEXT):
            return 0
        if top.values.get("store") == "":
            raise invalid_argument("", top.spelled["store"])
        if not top.operands:
            raise UsageError("missing command")
        name, rest = top.operands[0], top.operands[1:]
        command = COMMANDS.get(name)
        if command is None:
            raise UsageError(f"unknown command '{name}'")
        parsed = parse_args(rest, command.options)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        validate(name, command, parsed)
    except UsageError as error:
        return usage_failure(TOOL, error)

    invocation = Invocation(Store(resolve_store_path(top.values)), parsed.values,
                            parsed.operands)
    try:
        command.run(invocation)
    except (Failure, StoreError) as error:
        diagnose(TOOL, str(error))
        return 1
    return 0

"""Reference implementation of dp-sysmon (projects/10-sys-monitor/specs/SRS.md).

Pipeline per sample: source (snapshot replay or live readings) -> process selection
(filter, sort, top) -> rendering (table or JSON Lines) -> standard output and, optionally, the
``--output`` JSON Lines file.
"""

from __future__ import annotations

import os
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import BinaryIO

from . import _sysmon_live as live
from ._sysmon_model import Process, Sample, format_bytes, format_tenths, ratio_tenths
from ._sysmon_snapshot import SnapshotError, decode_line, is_blank
from .common import (
    Option,
    UsageError,
    diagnose,
    err,
    file_failure,
    handle_action,
    invalid_argument,
    open_input,
    out,
    parse_args,
    parse_count,
    usage_failure,
)

TOOL = "dp-sysmon"
MAX_TOP = 1000000
MAX_COUNT = 1000000
FORMATS = ("table", "json")
SORT_KEYS = ("cpu", "mem", "pid", "name")
INTERVAL_PATTERN = re.compile(r"[0-9]+(\.[0-9]+)?")
MIN_INTERVAL, MAX_INTERVAL = Decimal("0.1"), Decimal(86400)

HELP_TEXT = """\
Usage: dp-sysmon [OPTION]...
Report CPU, memory, disk, and process telemetry as a table or JSON Lines.

Without --snapshot, samples the local system every --interval seconds.
With --snapshot, replays recorded samples (JSON Lines, one sample per
line) from FILE instead; FILE '-' means standard input.

Options:
  -s, --snapshot=FILE   replay samples from FILE instead of polling the system
  -f, --format=FORMAT   output format: table (default) or json
  -k, --sort=KEY        order processes by cpu (default), mem, pid, or name
  -n, --top=N           show at most N processes (0-1000000)
  -m, --filter=TEXT     show only processes whose name contains TEXT
                        (ASCII letters match case-insensitively)
  -i, --interval=SECS   seconds between live samples (0.1-86400, default 1)
  -c, --count=N         stop after N samples (0-1000000, 0 = no limit;
                        default 1 when live, 0 when replaying)
  -o, --output=FILE     also append each sample as a JSON line to FILE
      --help            display this help and exit
      --version         output version information and exit
"""

OPTIONS = [
    Option("snapshot", short="s", long="snapshot", takes_value=True),
    Option("format", short="f", long="format", takes_value=True),
    Option("sort", short="k", long="sort", takes_value=True),
    Option("top", short="n", long="top", takes_value=True),
    Option("filter", short="m", long="filter", takes_value=True),
    Option("interval", short="i", long="interval", takes_value=True),
    Option("count", short="c", long="count", takes_value=True),
    Option("output", short="o", long="output", takes_value=True),
]


@dataclass
class Config:
    snapshot: str | None = None
    format: str = "table"
    sort: str = "cpu"
    top: int | None = None
    filter: str | None = None
    interval: float = 1.0
    count: int = 1
    output: str | None = None


# --- command line ------------------------------------------------------------------------


def _choice(parsed, dest: str, choices: tuple[str, ...]) -> str | None:
    if dest not in parsed.values:
        return None
    value = str(parsed.values[dest])
    if value not in choices:
        raise invalid_argument(value, parsed.spelled[dest])
    return value


def _path(parsed, dest: str) -> str | None:
    if dest not in parsed.values:
        return None
    value = str(parsed.values[dest])
    if value == "":
        raise invalid_argument(value, parsed.spelled[dest])
    return value


def _interval(value: str, spelled: str) -> float:
    if not INTERVAL_PATTERN.fullmatch(value):
        raise invalid_argument(value, spelled)
    number = Decimal(value)
    if not MIN_INTERVAL <= number <= MAX_INTERVAL:
        raise invalid_argument(value, spelled)
    return float(number)


def parse_config(argv: list[str]) -> Config | None:
    """Return the validated configuration, or None after printing help/version."""
    parsed = parse_args(argv, OPTIONS)
    if handle_action(TOOL, parsed, HELP_TEXT):
        return None
    if parsed.operands:
        raise UsageError(f"extra operand '{parsed.operands[0]}'")
    config = Config()
    config.snapshot = _path(parsed, "snapshot")
    config.format = _choice(parsed, "format", FORMATS) or "table"
    config.sort = _choice(parsed, "sort", SORT_KEYS) or "cpu"
    if "top" in parsed.values:
        config.top = parse_count(
            str(parsed.values["top"]), parsed.spelled["top"], minimum=0, maximum=MAX_TOP
        )
    if "filter" in parsed.values:
        config.filter = str(parsed.values["filter"])
    if "interval" in parsed.values:
        config.interval = _interval(
            str(parsed.values["interval"]), parsed.spelled["interval"]
        )
    config.count = 0 if config.snapshot is not None else 1
    if "count" in parsed.values:
        config.count = parse_count(
            str(parsed.values["count"]),
            parsed.spelled["count"],
            minimum=0,
            maximum=MAX_COUNT,
        )
    config.output = _path(parsed, "output")
    return config


# --- process selection -------------------------------------------------------------------

_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def _descending_nulls_last(value: int | None, pid: int) -> tuple[int, int, int]:
    return (1, 0, pid) if value is None else (0, -value, pid)


SORTERS = {
    "cpu": lambda p: _descending_nulls_last(p.cpu_tenths, p.pid),
    "mem": lambda p: _descending_nulls_last(p.rss_bytes, p.pid),
    "pid": lambda p: (p.pid,),
    "name": lambda p: (p.name.encode("utf-8"), p.pid),
}


def select_processes(processes: tuple[Process, ...], config: Config) -> list[Process]:
    """Filter, then sort, then truncate to --top (FR-07 .. FR-09)."""
    chosen = list(processes)
    if config.filter is not None:
        needle = config.filter.translate(_ASCII_LOWER)
        chosen = [p for p in chosen if needle in p.name.translate(_ASCII_LOWER)]
    chosen.sort(key=SORTERS[config.sort])
    if config.top is not None:
        chosen = chosen[: config.top]
    return chosen


# --- JSON rendering ----------------------------------------------------------------------

_JSON_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def json_string(text: str) -> str:
    parts = ['"']
    for char in text:
        if char in _JSON_ESCAPES:
            parts.append(_JSON_ESCAPES[char])
        elif ord(char) < 0x20:
            parts.append(f"\\u{ord(char):04x}")
        else:
            parts.append(char)
    parts.append('"')
    return "".join(parts)


def _json_int(value: int | None) -> str:
    return "null" if value is None else str(value)


def _json_percent(tenths: int | None) -> str:
    return "null" if tenths is None else format_tenths(tenths)


def render_json(sample: Sample, processes: list[Process]) -> str:
    disks = ",".join(
        f'{{"mount":{json_string(d.mount)},"total_bytes":{d.total_bytes},'
        f'"used_bytes":{d.used_bytes}}}'
        for d in sorted_disks(sample)
    )
    procs = ",".join(
        f'{{"pid":{p.pid},"name":{json_string(p.name)},'
        f'"cpu_percent":{_json_percent(p.cpu_tenths)},"rss_bytes":{_json_int(p.rss_bytes)}}}'
        for p in processes
    )
    return (
        f'{{"timestamp":{json_string(sample.timestamp)},'
        f'"hostname":{json_string(sample.hostname)},'
        f'"cpu":{{"count":{_json_int(sample.cpu_count)},'
        f'"percent":{_json_percent(sample.cpu_tenths)}}},'
        f'"memory":{{"total_bytes":{_json_int(sample.memory_total)},'
        f'"available_bytes":{_json_int(sample.memory_available)}}},'
        f'"disks":[{disks}],"processes":[{procs}]}}\n'
    )


# --- table rendering ---------------------------------------------------------------------

LABEL_WIDTH = 11
MOUNT_WIDTH = 20
NAME_WIDTH = 24
PID_WIDTH, CPU_WIDTH, BYTES_WIDTH, USE_WIDTH = 7, 6, 10, 6
GAP = "  "


def sorted_disks(sample: Sample):
    return sorted(sample.disks, key=lambda d: d.mount.encode("utf-8"))


def sanitize(text: str) -> str:
    """Replace C0 controls, DEL, and C1 controls with '?' (FR-12)."""
    return "".join("?" if ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F else c for c in text)


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 3] + "..."


def _dash(text: str | None) -> str:
    return "-" if text is None or text == "" else text


def _bytes_or_dash(value: int | None) -> str:
    return "-" if value is None else format_bytes(value)


def _percent_or_dash(tenths: int | None) -> str:
    return "-" if tenths is None else format_tenths(tenths)


def _label(name: str, value: str) -> str:
    return f"{name + ':':<{LABEL_WIDTH}}{value}\n"


def render_table(sample: Sample, processes: list[Process]) -> str:
    total, available = sample.memory_total, sample.memory_available
    used = None if total is None or available is None else total - available
    used_share = None
    if used is not None and total:
        used_share = format_tenths(ratio_tenths(used, total)) + "%"
    cpu = _percent_or_dash(sample.cpu_tenths)
    cpu_text = cpu + "%" if sample.cpu_tenths is not None else cpu
    count_text = "-" if sample.cpu_count is None else str(sample.cpu_count)

    lines = [
        _label("Host", _dash(sanitize(sample.hostname))),
        _label("Time", _dash(sanitize(sample.timestamp))),
        _label("CPU", f"{cpu_text} busy; logical CPUs: {count_text}"),
        _label(
            "Memory",
            f"{_bytes_or_dash(used)} used of {_bytes_or_dash(total)} "
            f"({_dash(used_share)}); {_bytes_or_dash(available)} available",
        ),
        _label("Processes", f"{len(sample.processes)} total; {len(processes)} shown"),
        "\n",
        (
            f"{'MOUNT':<{MOUNT_WIDTH}}{GAP}{'USED':>{BYTES_WIDTH}}{GAP}"
            f"{'TOTAL':>{BYTES_WIDTH}}{GAP}{'USE%':>{USE_WIDTH}}\n"
        ),
    ]
    for disk in sorted_disks(sample):
        share = (
            format_tenths(ratio_tenths(disk.used_bytes, disk.total_bytes))
            if disk.total_bytes
            else "-"
        )
        mount = truncate(sanitize(disk.mount), MOUNT_WIDTH)
        lines.append(
            f"{mount:<{MOUNT_WIDTH}}{GAP}{format_bytes(disk.used_bytes):>{BYTES_WIDTH}}"
            f"{GAP}{format_bytes(disk.total_bytes):>{BYTES_WIDTH}}"
            f"{GAP}{share:>{USE_WIDTH}}\n"
        )
    lines.append("\n")
    lines.append(
        f"{'PID':>{PID_WIDTH}}{GAP}{'CPU%':>{CPU_WIDTH}}{GAP}"
        f"{'RSS':>{BYTES_WIDTH}}{GAP}NAME\n"
    )
    for proc in processes:
        row = (
            f"{proc.pid:>{PID_WIDTH}}{GAP}{_percent_or_dash(proc.cpu_tenths):>{CPU_WIDTH}}"
            f"{GAP}{_bytes_or_dash(proc.rss_bytes):>{BYTES_WIDTH}}"
        )
        name = truncate(sanitize(proc.name), NAME_WIDTH)
        lines.append(f"{row}{GAP}{name}\n" if name else f"{row}\n")
    return "".join(lines)


# --- sample sources ----------------------------------------------------------------------


class SourceFailure(Exception):
    """A runtime failure already reported on standard error."""


def snapshot_samples(handle: BinaryIO, path: str) -> Iterator[Sample]:
    """Yield samples from a JSON Lines snapshot, one line at a time (FR-03, FR-04)."""
    line_number = 0
    produced = False
    while True:
        try:
            raw = handle.readline()
        except OSError as error:
            file_failure(TOOL, path, error)
            raise SourceFailure from None
        if not raw:
            break
        line_number += 1
        line = raw[:-1] if raw.endswith(b"\n") else raw
        if line.endswith(b"\r"):
            line = line[:-1]
        if is_blank(line):
            continue
        try:
            sample = decode_line(line)
        except SnapshotError as error:
            diagnose(TOOL, f"{path}:{line_number}: {error}")
            raise SourceFailure from None
        produced = True
        yield sample
    if not produced:
        diagnose(TOOL, f"{path}: no samples")
        raise SourceFailure


def live_samples(interval: float) -> Iterator[Sample]:
    """Yield one sample per interval, drift-free relative to the start time (FR-15, FR-16)."""
    previous = live.read()
    start = previous.monotonic
    index = 0
    while True:
        index += 1
        delay = start + index * interval - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        current = live.read()
        yield live.make_sample(previous, current)
        previous = current


# --- main --------------------------------------------------------------------------------


def run_samples(
    config: Config, samples: Iterator[Sample], record: BinaryIO | None
) -> int:
    emitted = 0
    try:
        for sample in samples:
            processes = select_processes(sample.processes, config)
            if config.format == "json":
                text = render_json(sample, processes)
            else:
                text = ("\n" if emitted else "") + render_table(sample, processes)
            out.write(text.encode("utf-8"))
            out.flush()
            if record is not None:
                assert config.output is not None
                try:
                    record.write(render_json(sample, processes).encode("utf-8"))
                    record.flush()
                except OSError as error:
                    file_failure(TOOL, config.output, error)
                    return 1
            emitted += 1
            if config.count and emitted >= config.count:
                break
    except SourceFailure:
        return 1
    return 0


def main(argv: list[str]) -> int:
    try:
        config = parse_config(argv)
    except UsageError as error:
        return usage_failure(TOOL, error)
    if config is None:
        return 0

    handle: BinaryIO | None = None
    if config.snapshot is not None:
        try:
            handle = open_input(config.snapshot)
        except OSError as error:
            file_failure(TOOL, config.snapshot, error)
            return 1
    record: BinaryIO | None = None
    try:
        if config.output is not None:
            try:
                record = open_output(config.output)
            except OSError as error:
                file_failure(TOOL, config.output, error)
                return 1
            if handle is not None and same_file(handle, record):
                diagnose(TOOL, f"{config.output}: input file is output file")
                return 1
        if handle is not None:
            samples = snapshot_samples(handle, config.snapshot or "-")
        else:
            samples = live_samples(config.interval)
        return run_samples(config, samples, record)
    finally:
        if record is not None:
            record.close()
        if handle is not None and config.snapshot != "-":
            handle.close()
        err.flush()


def open_output(path: str) -> BinaryIO:
    """Open the --output file for appending; directories fail on every platform (FR-14)."""
    if os.path.isdir(path):
        raise IsADirectoryError(path)
    return open(path, "ab")


def same_file(first: BinaryIO, second: BinaryIO) -> bool:
    """True when both open handles refer to one file (device + file ID), per FR-14."""
    try:
        a, b = os.fstat(first.fileno()), os.fstat(second.fileno())
    except (OSError, ValueError):
        return False
    return a.st_ino != 0 and (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)

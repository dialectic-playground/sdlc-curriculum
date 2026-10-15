"""Snapshot (JSON Lines) decoding and validation for dp-sysmon (SRS sections 3.8, 3.9, FR-04).

:func:`decode_line` turns one non-blank snapshot line into a :class:`Sample`, or raises
:class:`SnapshotError` whose message is the exact diagnostic detail from the SRS. Members are
validated in schema order and the first violation wins.
"""

from __future__ import annotations

import json
import math

from ._sysmon_model import (
    MAX_INTEGER,
    MAX_PROCESS_PERCENT,
    MAX_SYSTEM_PERCENT,
    Disk,
    Process,
    Sample,
    round1_tenths,
)

MAX_DEPTH = 64
JSON_WHITESPACE = b" \t\r"


class SnapshotError(Exception):
    """Invalid sample; ``str(error)`` is the diagnostic detail (e.g. ``invalid JSON``)."""


def is_blank(line: bytes) -> bool:
    return not line.strip(JSON_WHITESPACE)


# --- JSON text layer ---------------------------------------------------------------------


def _reject_constant(_name: str) -> object:
    raise ValueError("NaN and Infinity are not JSON")


def _parse_int(text: str) -> object:
    # Very long literals are out of range anyway; float() avoids Python's digit limit.
    return int(text) if len(text) <= 24 else float(text)


def _unique_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    members: dict[str, object] = {}
    for key, value in pairs:
        if key in members:
            raise ValueError("duplicate member name")
        members[key] = value
    return members


_DECODER = json.JSONDecoder(
    object_pairs_hook=_unique_members,
    parse_constant=_reject_constant,
    parse_int=_parse_int,
)


def _depth_exceeds(text: str, limit: int) -> bool:
    depth, in_string, escaped = 0, False, False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > limit:
                return True
        elif char in "]}":
            depth -= 1
    return False


def _has_lone_surrogate(value: object) -> bool:
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            return True
        return False
    if isinstance(value, list):
        return any(_has_lone_surrogate(item) for item in value)
    if isinstance(value, dict):
        return any(
            _has_lone_surrogate(k) or _has_lone_surrogate(v) for k, v in value.items()
        )
    return False


def parse_json(line: bytes) -> object:
    """Decode one line as a single RFC 8259 JSON text with the SRS restrictions."""
    try:
        text = line.decode("utf-8")
        if _depth_exceeds(text, MAX_DEPTH):
            raise ValueError("nesting too deep")
        value = _DECODER.decode(text)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise SnapshotError("invalid JSON") from None
    if _has_lone_surrogate(value):
        raise SnapshotError("invalid JSON")
    return value


# --- schema layer ------------------------------------------------------------------------


def _member(container: dict[str, object], key: str, path: str) -> object:
    if key not in container:
        raise SnapshotError(f"missing member '{path}'")
    return container[key]


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _string(container: dict[str, object], key: str, path: str) -> str:
    value = _member(container, key, path)
    if not isinstance(value, str):
        raise SnapshotError(f"invalid type for '{path}'")
    return value


def _object(container: dict[str, object], key: str, path: str) -> dict[str, object]:
    value = _member(container, key, path)
    if not isinstance(value, dict):
        raise SnapshotError(f"invalid type for '{path}'")
    return value


def _array(container: dict[str, object], key: str, path: str) -> list[object]:
    value = _member(container, key, path)
    if not isinstance(value, list):
        raise SnapshotError(f"invalid type for '{path}'")
    return value


def _integer(
    container: dict[str, object],
    key: str,
    path: str,
    *,
    minimum: int = 0,
    nullable: bool = False,
) -> int | None:
    value = _member(container, key, path)
    if value is None and nullable:
        return None
    if not _is_number(value):
        raise SnapshotError(f"invalid type for '{path}'")
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise SnapshotError(f"invalid value for '{path}'")
        value = int(value)
    assert isinstance(value, int)
    if not minimum <= value <= MAX_INTEGER:
        raise SnapshotError(f"invalid value for '{path}'")
    return value


def _percent(
    container: dict[str, object], key: str, path: str, maximum: float
) -> int | None:
    value = _member(container, key, path)
    if value is None:
        return None
    if not _is_number(value):
        raise SnapshotError(f"invalid type for '{path}'")
    assert isinstance(value, (int, float))
    number = float(value)
    if not math.isfinite(number) or not 0.0 <= number <= maximum:
        raise SnapshotError(f"invalid value for '{path}'")
    return round1_tenths(number)


def _element_object(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise SnapshotError(f"invalid type for '{path}'")
    return value


def to_sample(document: object) -> Sample:
    """Validate a decoded JSON value against the sample schema (SRS section 3.9)."""
    if not isinstance(document, dict):
        raise SnapshotError("sample is not a JSON object")
    timestamp = _string(document, "timestamp", "timestamp")
    hostname = _string(document, "hostname", "hostname")
    cpu = _object(document, "cpu", "cpu")
    cpu_count = _integer(cpu, "count", "cpu.count", minimum=1, nullable=True)
    cpu_tenths = _percent(cpu, "percent", "cpu.percent", MAX_SYSTEM_PERCENT)
    memory = _object(document, "memory", "memory")
    total = _integer(memory, "total_bytes", "memory.total_bytes", nullable=True)
    available = _integer(
        memory, "available_bytes", "memory.available_bytes", nullable=True
    )
    if total is not None and available is not None and available > total:
        raise SnapshotError("'memory.available_bytes' exceeds 'memory.total_bytes'")

    disks = []
    for index, item in enumerate(_array(document, "disks", "disks")):
        base = f"disks[{index}]"
        entry = _element_object(item, base)
        mount = _string(entry, "mount", f"{base}.mount")
        disk_total = _integer(entry, "total_bytes", f"{base}.total_bytes")
        used = _integer(entry, "used_bytes", f"{base}.used_bytes")
        assert disk_total is not None and used is not None
        if used > disk_total:
            raise SnapshotError(f"'{base}.used_bytes' exceeds '{base}.total_bytes'")
        disks.append(Disk(mount, disk_total, used))

    processes = []
    seen_pids: set[int] = set()
    for index, item in enumerate(_array(document, "processes", "processes")):
        base = f"processes[{index}]"
        entry = _element_object(item, base)
        pid = _integer(entry, "pid", f"{base}.pid")
        assert pid is not None
        if pid in seen_pids:
            raise SnapshotError(f"duplicate value for '{base}.pid'")
        seen_pids.add(pid)
        name = _string(entry, "name", f"{base}.name")
        cpu_percent = _percent(
            entry, "cpu_percent", f"{base}.cpu_percent", MAX_PROCESS_PERCENT
        )
        rss = _integer(entry, "rss_bytes", f"{base}.rss_bytes", nullable=True)
        processes.append(Process(pid, name, cpu_percent, rss))

    return Sample(
        timestamp,
        hostname,
        cpu_count,
        cpu_tenths,
        total,
        available,
        tuple(disks),
        tuple(processes),
    )


def decode_line(line: bytes) -> Sample:
    return to_sample(parse_json(line))

"""Telemetry data model and numeric rules shared by dp-sysmon's snapshot and live paths.

See projects/10-sys-monitor/specs/SRS.md, sections 3.9 (sample schema) and 3.10 (numeric
formatting). Percentages are carried as integer *tenths* (ROUND1 already applied), so that
sorting, table output, and JSON output all agree on the same value.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

MAX_INTEGER = 2**53 - 1  # largest value of every integer field
MAX_SYSTEM_PERCENT = 100.0  # cpu.percent upper bound
MAX_PROCESS_PERCENT = 1000000.0  # processes[].cpu_percent upper bound
_TENTH = Decimal("0.1")


@dataclass(frozen=True)
class Disk:
    mount: str
    total_bytes: int
    used_bytes: int


@dataclass(frozen=True)
class Process:
    pid: int
    name: str
    cpu_tenths: int | None
    rss_bytes: int | None


@dataclass(frozen=True)
class Sample:
    timestamp: str
    hostname: str
    cpu_count: int | None
    cpu_tenths: int | None
    memory_total: int | None
    memory_available: int | None
    disks: tuple[Disk, ...]
    processes: tuple[Process, ...]


def round1_tenths(value: float) -> int:
    """ROUND1: tenths nearest the exact binary64 value, ties to even; -0.0 becomes 0."""
    return int(Decimal(value).quantize(_TENTH, rounding=ROUND_HALF_EVEN) * 10)


def ratio_tenths(numerator: int, denominator: int) -> int:
    """Tenths of a percent of numerator/denominator (denominator > 0), ties to even.

    Uses only quotient/remainder arithmetic, so it never needs more than 64 bits for
    integer fields bounded by MAX_INTEGER.
    """
    quotient, remainder = divmod(numerator * 1000, denominator)
    twice = 2 * remainder
    if twice > denominator or (twice == denominator and quotient % 2 == 1):
        quotient += 1
    return quotient


def format_tenths(tenths: int) -> str:
    return f"{tenths // 10}.{tenths % 10}"


_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")


def format_bytes(count: int) -> str:
    """Human-readable binary units (SRS section 3.10, HUMAN)."""
    if count < 1024:
        return f"{count} B"
    exponent = 1
    while exponent < len(_UNITS) - 1 and count >= 1024 ** (exponent + 1):
        exponent += 1
    while True:
        divisor = 1024**exponent
        quotient, remainder = divmod(count * 10, divisor)
        twice = 2 * remainder
        if twice > divisor or (twice == divisor and quotient % 2 == 1):
            quotient += 1
        if quotient >= 10240 and exponent < len(_UNITS) - 1:
            exponent += 1
            continue
        return f"{format_tenths(quotient)} {_UNITS[exponent]}"

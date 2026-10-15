"""The tax rule and report format shared by dp-taxes and dp-taxes-file.

Specified identically in projects/13-taxes/specs/SRS.md and
projects/14-taxes-file/specs/SRS.md (section "Tax rule and report").
"""

from __future__ import annotations

THRESHOLD = 6000  # incomes below this are taxed at the lower rate
LOW_RATE = 30  # percent
HIGH_RATE = 60  # percent
MAX_INCOME = 2**63 - 1


def tax(income: int) -> int:
    """Exact integer tax: floor(income * rate / 100) for 0 <= income <= 2**63 - 1."""
    rate = LOW_RATE if income < THRESHOLD else HIGH_RATE
    return income * rate // 100


def record(income: int) -> bytes:
    """The two report lines for one income."""
    return f"Income = {income} greenbacks\nTax = {tax(income)} greenbacks\n".encode(
        "ascii"
    )

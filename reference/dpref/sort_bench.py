"""Reference implementation of dp-sort-bench (projects/35-sort-bench/specs/SRS.md).

Each array is filled from the CONV-38 generator, then sorted on separate clones by selection
sort and by the quicksort of FR-05, counting comparisons and swaps exactly as FR-06 defines
them. Wall-clock times are written only with ``--time`` (never used by the tests).
"""

from __future__ import annotations

import time

from . import common
from .common import (
    AnsiRand,
    Option,
    UsageError,
    handle_action,
    invalid_argument,
    parse_args,
    parse_seed,
    usage_failure,
)

TOOL = "dp-sort-bench"
DEFAULT_SIZES = (1000, 2000, 4000)
MAX_SIZE = 100000
HELP_TEXT = """\
Usage: dp-sort-bench [OPTION]...
Compare selection sort and quicksort on random arrays of growing size.

For each size (default 1000,2000,4000) an array of pseudo-random integers
0-32767 is generated, and a copy of it is sorted by each algorithm.  The
report gives the number of comparisons and swaps each sort made and whether
its result is sorted.

Options:
  -s, --sizes=LIST   comma-separated array sizes, each 0-100000
                       (default 1000,2000,4000)
      --seed=SEED    seed the pseudo-random generator (0-4294967295, default 1)
  -t, --time         also report the elapsed time of each sort in seconds
      --help         display this help and exit
      --version      output version information and exit
"""

OPTIONS: list[Option] = [
    Option("sizes", short="s", long="sizes", takes_value=True),
    Option("seed", long="seed", takes_value=True),
    Option("time", short="t", long="time"),
]


def parse_sizes(value: str, spelled: str) -> list[int]:
    """LIST: one or more SIZEs (ASCII digits, 0 … 100000) separated by single commas."""
    sizes = []
    for item in value.split(","):
        if not item or not all("0" <= c <= "9" for c in item) or int(item) > MAX_SIZE:
            raise invalid_argument(value, spelled)
        sizes.append(int(item))
    return sizes


def selection_sort(values: list[int]) -> tuple[int, int]:
    """FR-04: returns (comparisons, swaps)."""
    n = len(values)
    comparisons = swaps = 0
    for i in range(n - 1):
        # The first position of the smallest remaining value, found at C speed; it is the
        # position the FR-04 scan finds with its n - 1 - i comparisons.
        smallest = values.index(min(values[i:]), i)
        comparisons += n - 1 - i
        if smallest != i:
            values[i], values[smallest] = values[smallest], values[i]
            swaps += 1
    return comparisons, swaps


def quicksort(values: list[int]) -> tuple[int, int]:
    """FR-05: middle element moved to the left end, one-directional partition."""
    comparisons = swaps = 0
    pending = [(0, len(values) - 1)]
    while pending:
        left, right = pending.pop()
        if left >= right:
            continue
        middle = (left + right) // 2
        if middle != left:
            values[left], values[middle] = values[middle], values[left]
            swaps += 1
        pivot = values[left]
        last = left
        for i in range(left + 1, right + 1):
            if values[i] < pivot:
                last += 1
                if last != i:
                    values[last], values[i] = values[i], values[last]
                    swaps += 1
        comparisons += right - left
        if last != left:
            values[left], values[last] = values[last], values[left]
            swaps += 1
        pending.append((left, last - 1))
        pending.append((last + 1, right))
    return comparisons, swaps


ALGORITHMS = (("Selection Sort", selection_sort), ("Quicksort", quicksort))


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        sizes = (
            parse_sizes(str(parsed.values["sizes"]), parsed.spelled["sizes"])
            if "sizes" in parsed.values
            else list(DEFAULT_SIZES)
        )
        seed = parse_seed(parsed)
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    timing = bool(parsed.values.get("time"))
    generator = AnsiRand(seed)
    failed = False
    for block, size in enumerate(sizes):
        original = [generator.next() for _ in range(size)]
        expected = sorted(original)
        lines = [] if block == 0 else [""]
        lines.append(f"Array size: {size}")
        for name, algorithm in ALGORITHMS:
            clone = list(original)
            start = time.perf_counter()
            comparisons, swaps = algorithm(clone)
            elapsed = time.perf_counter() - start
            ok = clone == expected
            failed = failed or not ok
            lines.append(f"\tAlgorithm: {name}")
            if timing:
                lines.append(f"\t\tTime = {common.fix(elapsed, 6)} seconds")
            lines.append(f"\t\tComparisons = {comparisons}")
            lines.append(f"\t\tSwaps = {swaps}")
            lines.append(f"\t\tSorted = {'yes' if ok else 'no'}")
        common.write("".join(line + "\n" for line in lines).encode())
        common.out.flush()
    if failed:
        common.diagnose(TOOL, "verification failed")
        return 1
    return 0

# Project 35 — Empirical Algorithm Runtime Benchmarking (`dp-sort-bench`)

> Race selection sort against quicksort on the same random arrays of growing size and show
> how their work grows — with exact, reproducible operation counts as the specified output,
> and real monotonic-clock timings only when asked for, so the report is byte-identical on
> Linux, macOS, and Windows.

## Purpose

Project 35 is adapted from §6.10 of Johnsonbaugh & Kalin, *Applications Programming in ANSI
C*: a harness that fills arrays of 1000, 2000, and 4000 random integers, gives a copy of each
to a quadratic sort and to quicksort through a function pointer, and prints how long each
sort took. Elapsed times are the point of that program and exactly what a byte-exact
specification cannot fix: they change with every run, machine, and compiler. This project
keeps the experiment and its report layout but makes the *deterministic* evidence the
specified output — the exact number of comparisons and swaps of two fully specified
algorithms on arrays from the curriculum's portable generator — and moves the timings behind
an opt-in `--time` that must use a monotonic clock. The engineering focus is specifying an
algorithm precisely enough that every implementation does the same work, building a
benchmark loop that is fair (identical clones) and honest (verified results), and measuring
time correctly on three operating systems.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Default sizes 1000, 2000, 4000; any list of sizes 0–100000 (`-s`, `--sizes`) | Reading arrays from files or standard input |
| Arrays from the CONV-38 generator, `--seed` (default 1) | Platform `rand()`, other distributions |
| Selection sort and a fully specified quicksort, each on its own clone | Other algorithms, hybrid or library sorts |
| Exact counts of comparisons and swaps (FR-06) | Counting memory traffic, cache misses |
| Verification of every result against the sorted original | Statistics over repeated timings |
| Opt-in elapsed times from a monotonic clock (`-t`, `--time`), `FIX(t, 6)` | Timings in the deterministic default output |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Implement two sorting algorithms to an exact specification — including the pivot choice
   and the partition scheme — and prove it with operation counts that must match to the unit
   (FR-04 … FR-06).
2. Instrument code without changing it: count the operations that matter and only those,
   with a precise definition of what one operation is (FR-06).
3. Design a fair, non-destructive benchmark harness: identical clones, one algorithm
   interface, verified results that no optimizer can discard (FR-03, FR-07, NFR-05).
4. Measure elapsed time correctly with each platform's monotonic high-resolution clock, and
   keep non-deterministic measurements out of what tests compare (FR-09, NFR-02).
5. Observe empirical growth — 4× for *n*² when *n* doubles, about 2× for *n* log *n* — in
   numbers that are the same on every machine.

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-13) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The tool reads no input, so the project has no fixture files, and the textbook section has no
companion data file.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the common algorithm interface that NFR-05 requires.
2. An implementation of `dp-sort-bench`, with unit tests — including the exact counts of both
   sorts on the small arrays NFR-06 lists.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-sort-bench into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

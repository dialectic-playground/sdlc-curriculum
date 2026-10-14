# Project 38 — Greedy Interval Activity Scheduling (`dp-sched`)

> Read competing activities from a fixed-width file and print a largest set of them that do not
> overlap — the way a professional tool would: the classic greedy algorithm with a specified tie
> rule, every line checked before the report is written, exact diagnostics, and byte-identical
> output on Linux, macOS, and Windows.

## Purpose

Project 38 is adapted from §7.9 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that reads activities (a start time in columns 1–5 and a finish time in columns 6–10)
from the file named on its command line, sorts them by finish time with a general-purpose
sorting routine, and selects activities greedily, always taking the next compatible activity
that finishes first. The textbook version's sort is not stable, so for equal finish times its
choice depends on the sort's internals, and the section's own expected result for its sample
file is not even a valid schedule. This project keeps the algorithm and the report and makes
the result fully determined: a stable order by finish time, strict validation of the
fixed-width lines, and a reference answer proven by the curriculum's model. The engineering
focus is *deterministic ordering* — the same input must select the same lines whatever sort the
platform's library provides — and the classic argument for why the greedy choice is optimal.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| One required `FILE` operand (`-` is standard input) | Several input files, a default file name |
| Fixed-width lines: start in columns 1–5, finish in columns 6–10, times 0 … 99999 | Clock times, fractions, other column layouts |
| Stable sort by finish time; greedy selection (start ≥ last finish is compatible) | Weighted activities, several resources |
| The heading, a blank line, and the selected lines exactly as in the input | Listing rejected activities, counts |
| Validation of every line before the report is written | Partial reports after a data error |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Prompts or any other interaction |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Repairing malformed lines |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Implement the greedy algorithm for activity selection and justify its optimality with an
   exchange argument; test it against exhaustive search (FR-05, NFR-06).
2. Specify and implement a deterministic tie rule, and recognize when a library sort's
   stability is part of a program's observable behavior (FR-04, NFR-02).
3. Write a sort routine that is parameterized by its ordering, independent of the records it
   sorts (NFR-05).
4. Parse fixed-width fields by byte position and validate them with precise, located
   diagnostics (FR-03, FR-06).
5. Copy input lines to the output byte for byte while normalizing line endings, so a CRLF file
   and an LF file give the same report (FR-02, FR-05).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-13) |
| `specs/SRS.md` | System requirements (FR-01 … FR-11, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites: `sched.in` (from the textbook's companion disk), `ties.in`, `empty.in`, `bad.in` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-sched`, with unit tests, including the comparison with exhaustive
   search that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-sched into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

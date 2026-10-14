# Project 14 — Batch File-Based Progressive Income Tax Calculator (`dp-taxes-file`)

> Read a file of incomes, compute the tax on each under a two-bracket rule, and write the
> report to a file — the way a professional batch job would: fixed default file names that can
> be overridden, the whole input checked before the output is touched, exact diagnostics for
> every file and data problem, and byte-identical reports on Linux, macOS, and Windows.

## Purpose

Project 14 is adapted from §1.10 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
the tax program of §1.6 ([Project 13](../13-taxes/)), changed to read its incomes from the file
`incomes.dat` and write its report to the file `out.dat`. The tax rule and report format are
exactly those of Project 13. What is new is the *file handling*: default names in the current
directory, options to override them, creating and replacing the output file, mapping file-system
failures to fixed messages, and — the central design decision — checking the whole input
before the output file is opened, so a bad input never leaves a truncated or half-written
report behind.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Input from `incomes.dat`, or the file named by `-i`/`--input` (`-` is standard input) | Several input files |
| Report to `out.dat`, or the file named by `-o`/`--output` (`-` is standard output) | Appending to an existing report, backup copies |
| Exact two-bracket tax (30% below 6000, 60% from 6000), any income 0 … 2⁶³−1 | Other tax schedules, negative incomes |
| Validation of the whole input before the output file is created or replaced | Partial reports after a data error |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Prompts or any other interaction |
| Data diagnostics with line numbers (CONV-34), CONV-16 errors for both files | Atomic replacement, file locking |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Open, create, truncate, write, and close files explicitly, and release every handle on every
   path, including failures (FR-05, NFR-05).
2. Design the order of operations of a batch job so that failures have well-defined effects:
   which checks happen before the output file is touched, and what a failure leaves behind
   (FR-06).
3. Map file-system failures for both input and output to fixed, portable messages (FR-08,
   FR-09, CONV-16).
4. Reuse a business rule unchanged between two front ends (Project 13 and this one), and
   compute it exactly without floating point or overflow (FR-03).
5. Write a report file whose bytes are identical on every operating system, with LF line
   endings even on Windows (NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-13, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`incomes.dat`, `more.dat`, `bad.dat`, `prev.dat`, `empty.dat`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture, including `incomes.dat`, was
written for this project. Several tests have more than one step: a later step reads back, with
`-i`, the file an earlier step wrote, to show whether it was created, replaced, or left alone.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-taxes-file`, with unit tests and the file-handling integration tests
   that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-taxes-file into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

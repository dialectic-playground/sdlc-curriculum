# Project 19 — Formatted Annual Calendar Generator (`dp-calendar`)

> Print the twelve months of a year from two codes — the weekday of January 1 and whether the
> year is a leap year — the way a professional tool would: an exact character grid with no
> stray spaces or blank lines, a scripted equivalent of the textbook's "ask again" loop,
> precise diagnostics, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 19 is adapted from §3.6 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that asks for a day code (0 = Sunday … 6 = Saturday) and a leap-year code, asks again
until the day code is valid, and prints a calendar of the twelve months. The textbook version
leaves trailing spaces and a stray line after months that end on a Saturday, and its re-prompt
loop has no defined behavior for a file of answers. This project keeps the calendar's layout
and turns the program into a well-behaved command-line tool. The engineering focus is *exact
text layout driven by modular arithmetic*: every column, separator, and line break is
specified, and the weekday of each month's first day is carried forward from the previous
month. A convenience option derives the two codes from a Gregorian year, which also gives the
learner an independent oracle for testing.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Day code and leap-year code as integer tokens from standard input or one `FILE` (CONV-32, CONV-33) | Other calendar systems, week numbers, holidays |
| Twelve months in a fixed grid under `Sun  Mon  Tue  Wed  Thu  Fri  Sat` | Several months side by side, other first weekdays |
| Re-reading after an invalid day code, with a diagnostic per rejected pair | Re-reading after any other error |
| The codes derived from a Gregorian year 1 … 9999 (`-y`, `--year`) | Julian calendar, years outside 1 … 9999, the current date |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Localized month or weekday names |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Use modular arithmetic to carry a weekday from one month to the next and to place every day
   in its column (FR-05, FR-06).
2. Produce a character grid that is specified to the byte — field widths, separators, line
   breaks after Saturday, no trailing spaces, no empty week lines — and verify it
   automatically (FR-06).
3. Turn an interactive "ask again until valid" loop into behavior that is equally well defined
   for a keyboard and for a file of answers, and distinguish recoverable input mistakes from
   fatal ones (FR-03, FR-09).
4. Derive the same inputs from a different interface (a Gregorian year) and use the
   equivalence as a test oracle (FR-11, NFR-06).
5. Separate prompts (standard error) from results (standard output), so redirected output is
   identical with or without prompting (FR-08, CONV-36).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-13) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`tue.txt`, `retry.txt`, `sat.txt`, `bad.txt`, `leapbad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-calendar`, with unit tests — including the layout and year-code
   tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-calendar into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

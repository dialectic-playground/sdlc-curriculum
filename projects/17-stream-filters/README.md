<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 17 — Stream Filtering & Monotonicity Validation (`dp-average`, `dp-chk-sort`)](#project-17--stream-filtering--monotonicity-validation-dp-average-dp-chk-sort)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 17 — Stream Filtering & Monotonicity Validation (`dp-average`, `dp-chk-sort`)

> Two small stream filters, built the way professional ones are: `dp-average` averages the
> positive numbers in a stream, and `dp-chk-sort` tells you whether a stream of integers is in
> order — answering through its exit status and stopping at the first number out of place —
> with exact arithmetic, precise diagnostics, and byte-identical output on Linux, macOS, and
> Windows.

## Purpose

Project 17 is adapted from §3.1 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
two programs that read standard input until end-of-file — one averages the positive numbers it
reads, the other checks whether the integers it reads are sorted and stops reading as soon as
it finds one that is not. The textbook versions report only on standard output, cannot tell a
typo from the end of the input, and leave floating-point formatting to the C library. This
project keeps their messages word for word and turns them into well-behaved command-line
filters. The engineering focus is the _filter loop_: selecting values from a stream,
short-circuiting a check without consuming the rest of the stream, and giving a script a
machine-readable answer — `dp-chk-sort` exits with 0 or 1 like `sort -c`, and reserves 2 for
trouble.

## Operational scope

| In scope                                                                                                                                | Out of scope                                                                 |
| :-------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| Numbers as whitespace-separated tokens until end of input (CONV-32, CONV-33): reals for `dp-average`, 64-bit integers for `dp-chk-sort` | Digit grouping, `inf`, `nan`, hexadecimal numbers                            |
| The average of the numbers greater than zero, `FIX(x, 6)` (CONV-35)                                                                     | Other statistics (see `dp-stats`, Project 15), other precisions              |
| A non-decreasing order check that stops reading at the first inversion                                                                  | Other orders (descending, strict, textual), reporting where the inversion is |
| The answer as the exit status of `dp-chk-sort`: 0 sorted, 1 not sorted, 2 trouble                                                       | A quiet mode without the message                                             |
| Standard input or one `FILE` operand (`-` is standard input)                                                                            | Several input files                                                          |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                                                                           | Other legacy encodings                                                       |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                                                                       | Recovering after an invalid number                                           |
| `--help`, `--version`, CONV-13 usage errors                                                                                             | Prompts, configuration files, environment variables                          |

## Learning objectives

1. Write a filter loop that validates every value but uses only the selected ones, with an
   explicit answer for "nothing selected" (FR-03 … FR-05).
2. Short-circuit a check: stop reading at the first inversion, and know exactly which input has
   and has not been read and validated (FR-08).
3. Design an exit-status protocol for a checker, and keep it distinct from failures (FR-09,
   §3.7), as `sort -c`, `grep`, and `cmp` do.
4. Compute and print an average reproducibly: summation order, binary64 division, and correct
   decimal rounding (FR-04, CONV-35).
5. Handle early termination and end of input the same way on every platform, at a console and
   in a pipeline (NFR-02).

## What is provided

| Path                   | Contents                                                                                                                           |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-15)                                                                                                  |
| `specs/SRS.md`         | System requirements (FR-01 … FR-15, NFR-01 … NFR-08)                                                                               |
| `specs/user-manual.md` | Complete user manual, including the normative help texts of both tools                                                             |
| `tests/fixtures/`      | Input files shared by both suites (`numbers.txt`, `nonpos.txt`, `bad.txt`, `sorted.txt`, `unsorted.txt`, `stop.txt`, `badint.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                             |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                            |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. Implementations of `dp-average` and `dp-chk-sort`, with unit tests — including the
   short-circuit test that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-average and dp-chk-sort into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 13 — Stream-Based Progressive Income Tax Calculator (`dp-taxes`)](#project-13--stream-based-progressive-income-tax-calculator-dp-taxes)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 13 — Stream-Based Progressive Income Tax Calculator (`dp-taxes`)

> Read incomes until the end of the input and print the tax due on each under a two-bracket
> rule, the way a professional filter would: exact integer arithmetic for every 64-bit income,
> one result per income as soon as it is typed, precise diagnostics for bad data, and
> byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 13 is adapted from §1.6 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that reads incomes from the keyboard until end-of-file and prints the tax on each,
30% below 6000 greenbacks and 60% from 6000 up. The textbook version multiplies by a
floating-point rate, has no answer for a mistyped number, and knows nothing of other operating
systems' end-of-file conventions. This project keeps its report word for word and turns it into
a well-behaved command-line filter. The engineering focus is a _streaming_ loop that works the
same interactively and in a pipeline, and a business rule that is computed exactly — without
binary floating point and without integer overflow — for every income up to 2⁶³−1.
[Project 14](../14-taxes-file/) applies the same rule to files in batch mode.

## Operational scope

| In scope                                                                             | Out of scope                                         |
| :----------------------------------------------------------------------------------- | :--------------------------------------------------- |
| Incomes as whitespace-separated integer tokens until end of input (CONV-32, CONV-33) | Fractional amounts, digit grouping, currency symbols |
| Exact two-bracket tax (30% below 6000, 60% from 6000), any income 0 … 2⁶³−1          | Other tax schedules, negative incomes                |
| Standard input or one `FILE` operand (`-` is standard input)                         | Several input files, writing files                   |
| One record per income, flushed before the next income is read                        | Summary totals                                       |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                       | Prompts on standard output                           |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                        | Other legacy encodings                               |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                    | Recovering after an invalid income                   |
| `--help`, `--version`, CONV-13 usage errors                                          | Configuration files, environment variables           |

## Learning objectives

1. Write an input loop that reads an unbounded stream until end-of-file and produces each
   result as soon as its input is complete, so the same program serves a keyboard and a pipe
   (FR-05).
2. Implement a numeric grammar exactly (CONV-33) and reject everything else with a precise,
   located diagnostic instead of looping or guessing (FR-02, FR-07).
3. Compute a percentage of a 64-bit integer exactly, avoiding both binary floating point and
   intermediate overflow, and prove it with boundary tests (FR-03).
4. Separate prompts (standard error) from results (standard output), so redirected output is
   identical with or without prompting (FR-06, CONV-36).
5. Handle platform end-of-file conventions — Ctrl-D, Ctrl-Z on Windows consoles, and the Ctrl-Z
   byte at the end of old DOS data files — without changing the result (NFR-02).

## What is provided

| Path                   | Contents                                                                                |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-12, NFR-01 … NFR-08)                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                 |
| `tests/fixtures/`      | Input files shared by both suites (`incomes.txt`, `mixed.txt`, `bad.txt`)               |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates     |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-taxes`, with unit tests — including the boundary and large-income
   tests of the tax function that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-taxes into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

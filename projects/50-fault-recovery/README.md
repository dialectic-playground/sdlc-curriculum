<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 50 — Structured Exception Handling & Fault Recovery (`dp-divide`)](#project-50--structured-exception-handling--fault-recovery-dp-divide)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 50 — Structured Exception Handling & Fault Recovery (`dp-divide`)

> Divide pairs of numbers until an arithmetic fault occurs, then recover the way the textbook
> program does — a status line, a message from the recovery point, and a clean exit — with
> faults defined by explicit tests rather than hardware traps, exact six-digit formatting,
> precise diagnostics for bad data, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 50 is adapted from §11.2 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that repeatedly asks for two floats and prints their quotient, and that, when the
divisor is zero, catches the arithmetic-fault signal, jumps back to a recovery point set up
before the loop, prints `Signal status == 8.` and `At jump point and about to exit...`, and
exits normally. The textbook relies on the hardware raising a signal for a floating-point
division by zero — which IEEE 754 arithmetic, the default on every current platform, does not
do. This project keeps the dialogue and the recovery messages word for word, defines the
faults precisely (a zero divisor of either sign, and a quotient too large to represent), and
turns the program into a well-behaved command-line filter. The engineering focus is _fault
recovery as a control-flow structure_: the fault is raised deep in the division routine and
handled at one recovery point in the driver, by whatever non-local transfer the implementation
language offers — an exception, a `Result` propagated with `?`, or a non-local jump.

## Operational scope

| In scope                                                                        | Out of scope                                            |
| :------------------------------------------------------------------------------ | :------------------------------------------------------ |
| Reals as whitespace-separated tokens, read in pairs (CONV-32, CONV-33)          | Integer division, other operations                      |
| One line `a / b == q` per pair, every number as `FIX(x, 6)` (CONV-35)           | Other formats or precisions                             |
| Faults: zero divisor (including `-0` and 0 ÷ 0) and a quotient that overflows   | Hardware traps, signals, the floating-point environment |
| Recovery: two fixed lines on standard output, rest of the input ignored, exit 0 | Resuming after a fault                                  |
| Standard input or one `FILE` operand (`-` is standard input)                    | Several input files, writing files                      |
| One result per pair, flushed before the next pair is read                       | Summary totals                                          |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                  | Prompts on standard output                              |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                   | Other legacy encodings                                  |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors               | Recovering after an invalid number                      |
| `--help`, `--version`, CONV-13 usage errors                                     | Configuration files, environment variables              |

## Learning objectives

1. Separate _detecting_ a fault (in the routine that divides) from _handling_ it (at one
   recovery point in the driver), and transfer control between them without threading error
   checks through every caller (FR-05, FR-06, NFR-05).
2. Distinguish an _expected_ fault, from which the program recovers with a normal exit status,
   from a _data error_, which is a failure (FR-06, FR-08).
3. Define floating-point faults by explicit tests on IEEE 754 values instead of relying on
   platform-specific traps and signals (FR-05, NFR-02).
4. Format binary floating-point values exactly and identically on every platform (FR-04,
   CONV-35).
5. Write an interactive pairwise reader that prompts on standard error and answers as soon as
   each pair is complete (FR-03, FR-07).

## What is provided

| Path                   | Contents                                                                                                                                 |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                                                        |
| `specs/SRS.md`         | System requirements (FR-01 … FR-14, NFR-01 … NFR-08)                                                                                     |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                                                  |
| `tests/fixtures/`      | Input files shared by both suites: `textbook.txt` (the dialogue of the textbook section), `pairs.txt`, `mixed.txt`, `bad.txt`, `odd.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                                   |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                                  |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                      |

The textbook section has no companion data file; `textbook.txt` holds the two pairs typed in
the section's example dialogue, and every other fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-divide`, with unit tests — including the division routine's fault
   cases and the recovery path, as NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-divide into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

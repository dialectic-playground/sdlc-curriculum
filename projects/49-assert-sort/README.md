<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 49 — Formal Program Verification via Assertions & Loop Invariants (`dp-assert-sort`)](#project-49--formal-program-verification-via-assertions--loop-invariants-dp-assert-sort)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 49 — Formal Program Verification via Assertions & Loop Invariants (`dp-assert-sort`)

> Sort a list of integers by selection sort while the program checks its own correctness: a
> bounds assertion and the loop invariant after every pass, an optional trace of each check,
> deterministic fault injection that makes the checks fire with a precise diagnostic, and
> byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 49 is adapted from §11.1 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a selection sort of the array 5 4 3 2 1, instrumented with an assertion that the index of the
minimum lies inside the array and with an assertion of the loop invariant — after pass _i_,
a[0..i] is sorted and no later element is smaller than a[i]. The textbook program sorts one
built-in array, and its assertions disappear when the program is compiled for release. This
project keeps the algorithm, the two assertions, and the invariant exactly, and turns them into
a command-line tool that sorts any list of 64-bit integers. The engineering focus is
_verification you can observe_: checks that are always compiled in, a trace that shows each
invariant holding, and a fault-injection option that corrupts one precisely defined step of
the algorithm so that the learner can watch the right assertion catch it in the right pass.

## Operational scope

| In scope                                                                            | Out of scope                                                   |
| :---------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| Integers as whitespace-separated tokens, −2⁶³ … 2⁶³−1 (CONV-32, CONV-33)            | Reals, strings, other orderings                                |
| Selection sort with the bounds assertion and the invariant checked after every pass | Other sorting algorithms, stability, sorting in O(_n_ log _n_) |
| Standard input or one `FILE` operand (`-` is standard input)                        | Several input files, writing files                             |
| Sorted output, one integer per line                                                 | Column or single-line layouts                                  |
| Optional trace of every invariant check on standard error (`-t`, `--trace`)         | Timing or comparison counts                                    |
| Three deterministic faults, in every pass or in one pass (`-f`, `--fault`)          | Random faults, faults in the checks themselves                 |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                       | Other legacy encodings                                         |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                   | Recovering after an invalid integer                            |
| `--help`, `--version`, CONV-13 usage errors                                         | Configuration files, environment variables                     |

## Learning objectives

1. State a loop invariant precisely and implement it as one predicate that is evaluated on the
   real data after every iteration (FR-05).
2. Place a defensive assertion where an index error would otherwise corrupt memory or data, and
   report its failure with enough detail to locate the bug (FR-04, FR-09).
3. Keep assertions in every build: distinguish a check that is part of the specified behavior
   from one a release build may compile away (NFR-05).
4. Use deterministic fault injection to prove that a check detects the faults it is meant to
   detect — and see that a fault which leaves the data unchanged is, correctly, not reported
   (FR-08).
5. Separate diagnostic output (the trace, on standard error) from results (standard output), so
   that redirected results never depend on how the run was observed (FR-07).

## What is provided

| Path                   | Contents                                                                                                   |
| :--------------------- | :--------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                          |
| `specs/SRS.md`         | System requirements (FR-01 … FR-15, NFR-01 … NFR-08)                                                       |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                    |
| `tests/fixtures/`      | Input files shared by both suites: `textbook.txt` (the textbook's array 5 4 3 2 1), `mixed.txt`, `bad.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                     |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                    |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                        |

The textbook section has no companion data file; `textbook.txt` holds the array that the
textbook program sorts, and every other fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-assert-sort`, with unit tests — including the invariant predicate
   on arrays that satisfy and violate each of its two conditions, as NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-assert-sort into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

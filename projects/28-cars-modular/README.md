<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 28 — Modular Car Sales Architecture & Reporting (`dp-cars2`)](#project-28--modular-car-sales-architecture--reporting-dp-cars2)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 28 — Modular Car Sales Architecture & Reporting (`dp-cars2`)

> Refactor the dealership's daily sales tool so that the `DAILY REPORT` comes from an
> independent component — without changing a single byte of its behavior — and then use that
> independence: save the day's totals and reprint the report from them, with the same rigor,
> diagnostics, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 28 is adapted from §5.6 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
the textbook's revision of the car-sales program of §5.3 ([Project 26](../26-cars/),
`dp-cars1`), in which the report is printed by a separate function that is passed the stock
array and the sales array. The revision changes the program's structure, not its behavior, and
this project holds you to exactly that: by default `dp-cars2` must reproduce `dp-cars1`'s
output, messages, prompts, and exit statuses byte for byte, and several tests reuse Project
26's inputs and expected outputs. The engineering focus is _decomposition_ — a report component
that receives two read-only collections and knows nothing else — and the payoff of doing it
well: the same component prints a report from a saved totals file (`--totals`) that `--save`
writes, a capability that only exists because the report no longer depends on the dialog.

## Operational scope

| In scope                                                                                                                    | Out of scope                                      |
| :-------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| Everything `dp-cars1` does, with byte-identical results (opening stock, sales, refused sales, report, prompts, diagnostics) | Any change to the dialog or the report layout     |
| Saving the day's totals to a file (`-s`, `--save`), 12 lines of two integers                                                | Appending to a totals file, several days per file |
| Printing the report from 24 totals (`-t`, `--totals`), with complete validation                                             | Combining or comparing several days               |
| Standard input or one `FILE` operand (`-` is standard input) in both modes                                                  | Several input files                               |
| Optional prompts on standard error in sales mode (`-p`, `--prompt`, CONV-36)                                                | Prompts in totals mode                            |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37); LF-only totals files on every OS                             | Other legacy encodings                            |
| Data diagnostics with line numbers (CONV-34), CONV-16 errors for the input and the totals file                              | Recovering from an invalid token                  |
| `--help`, `--version`, CONV-13 usage errors                                                                                 | Configuration files, environment variables        |

## Learning objectives

1. Refactor a working program into components with one responsibility each, while proving
   with black-box tests that its observable behavior has not changed (FR-01).
2. Design a component interface that passes collections across a boundary as read-only data,
   and keep all knowledge of a presentation format in one place (NFR-05).
3. Unit-test a presentation component directly with literal data, without any input or
   dialog (NFR-06).
4. Define a small persistent file format, write it portably, and read it back with complete
   validation, so that a round trip reproduces the original result exactly (FR-10, FR-11).
5. Order side effects deliberately: no report and no file from invalid input, but a report
   that survives a failure to save (FR-11, FR-12).

## What is provided

| Path                   | Contents                                                                                                                                       |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-15)                                                                                                              |
| `specs/SRS.md`         | System requirements (FR-01 … FR-17, NFR-01 … NFR-08)                                                                                           |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                                                        |
| `tests/fixtures/`      | Input files shared by both suites: Project 26's `day.txt`, `rejected.txt`, and `cut.txt`, and the totals files `totals.tot` and `oversold.tot` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                                         |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                                        |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                            |

The textbook section has no companion data file; every fixture was written for Projects 26
and 28.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`; the HLD must show the
   report component and its interface (NFR-05).
2. An implementation of `dp-cars2`, with unit tests — including the direct tests of the report
   component and the totals round-trip test that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-cars2 into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

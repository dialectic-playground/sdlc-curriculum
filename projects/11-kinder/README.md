<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 11 — Console Output & Environment Verification (`dp-kinder`)](#project-11--console-output--environment-verification-dp-kinder)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 11 — Console Output & Environment Verification (`dp-kinder`)

> Print `ANSI--A kinder and gentler C!` the way a professional command-line tool would: with
> standard option handling, exact diagnostics, correct exit statuses, and byte-identical output
> on Linux, macOS, and Windows.

## Purpose

Project 11 is adapted from §1.1 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
the book's first program, which prints one line of text and exits. It opens the curriculum's
applications-programming track (Projects 11–52), and its job is the same as the textbook's:
prove that a new language toolchain can build, run, install, and test a program on every
operating system before any real work starts. The tool has no options of its own, so all the
effort goes into the parts of CLI-CONV every later tool of the track relies on: left-to-right
argument scanning, `--` and operands, usage errors, and LF-only output in binary mode.

## Operational scope

| In scope                                                   | Out of scope                                                      |
| :--------------------------------------------------------- | :---------------------------------------------------------------- |
| Printing the fixed message `ANSI--A kinder and gentler C!` | Other messages, names, or repetition (see `dp-hello`, Project 00) |
| `--help`, `--version`                                      | Localization, colors                                              |
| CONV-12 scan order, `--`, operand rejection                | Reading standard input or files                                   |
| CONV-13 usage errors with exit status 2                    | Configuration files, environment variables                        |

## Learning objectives

1. Set up a language toolchain behind the universal `Makefile` contract and prove it with the
   smallest possible program.
2. Implement the CLI-CONV argument scan for a tool with no options of its own: `--help` and
   `--version` take effect where they are reached, `--` ends option processing, and every
   operand is an error (CONV-09 … CONV-14).
3. Write standard output in binary mode so that the output is LF-only on Windows too (CONV-03).
4. Signal success and failure through the exit status, and verify it from a shell on each
   operating system.

## What is provided

| Path                   | Contents                                                                            |
| :--------------------- | :---------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-10)                                                   |
| `specs/SRS.md`         | System requirements (FR-01 … FR-09, NFR-01 … NFR-08)                                |
| `specs/user-manual.md` | Complete user manual, including the normative help text                             |
| `tests/fixtures/`      | `input.txt`, a file redirected to standard input to show that it is never read      |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                              |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; the fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-kinder`, with unit tests.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-kinder into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 25 — Variadic Functions & Dynamic Arity Processing (`dp-max`)](#project-25--variadic-functions--dynamic-arity-processing-dp-max)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 25 — Variadic Functions & Dynamic Arity Processing (`dp-max`)

> Print the largest of one to four integers, the way a professional tool would: one function
> that accepts any number of arguments, exact results over the whole 64-bit range on every
> platform, precise diagnostics for a missing, surplus, or mistyped value, and byte-identical
> output on Linux, macOS, and Windows.

## Purpose

Project 25 is adapted from §4.10 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that reads one to four integers until end-of-file and prints
`Maximum integer = …`, computed by a single function that can be called with any number of
arguments. The textbook uses this tiny task to teach a language mechanism — variable-length
argument lists. This project keeps the task and the report, states the mechanism as a design
requirement that every language can meet in its own idiom, and adds what the textbook leaves
open: what happens with no value, with a fifth value, with a value that is not an integer, and
with integers that do not fit in the platform's native `int` or `long`.

## Operational scope

| In scope                                                                                  | Out of scope                                                       |
| :---------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| One to four integers as whitespace-separated tokens until end of input (CONV-32, CONV-33) | Real numbers, digit grouping, more than four values                |
| Exact maximum over the full 64-bit signed range                                           | Minimum, sum, or other statistics (see `dp-stats`, Project 15)     |
| One variadic maximum function, checked by design review                                   | A fixed-arity function or a function that only accepts four values |
| Standard input or one `FILE` operand (`-` is standard input)                              | Values given as command-line operands, several input files         |
| Optional prompt on standard error (`-p`, `--prompt`, CONV-36)                             | Prompts on standard output                                         |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                             | Other legacy encodings                                             |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                         | Partial results after a bad value                                  |
| `--help`, `--version`, CONV-13 usage errors                                               | Configuration files, environment variables                         |

## Learning objectives

1. Write one function that accepts any number of arguments, using the variable-arity mechanism
   of your language, and keep the program's limit of four values out of it (NFR-05).
2. Compute an extreme value without a sentinel that could collide with real data, so that the
   smallest 64-bit integer is handled like any other (FR-04, NFR-06).
3. Validate a whole input — count and content — before writing a single result (FR-03,
   FR-05).
4. Read integers as exactly 64 bits on every platform, whatever the size of the language's
   native integer types (NFR-02).
5. Separate a prompt (standard error) from the result (standard output), so redirected output
   is identical with or without prompting (FR-06, CONV-36).

## What is provided

| Path                   | Contents                                                                                                |
| :--------------------- | :------------------------------------------------------------------------------------------------------ |
| `specs/URD.md`         | User requirements (UR-01 … UR-13)                                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-12, NFR-01 … NFR-08)                                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                 |
| `tests/fixtures/`      | Input files shared by both suites (`readme.txt`, `one.txt`, `four-negative.txt`, `five.txt`, `bad.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                 |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                     |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-max`, with unit tests — including the tests of the maximum
   function with one to ten arguments that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-max into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, the design review confirms NFR-05, and every RTM row is
_Verified_.

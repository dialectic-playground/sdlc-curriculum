<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 46 — Shunting-Yard Infix to Postfix Conversion (`dp-infix`)](#project-46--shunting-yard-infix-to-postfix-conversion-dp-infix)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 46 — Shunting-Yard Infix to Postfix Conversion (`dp-infix`)

> Convert arithmetic expressions from infix to postfix notation with an explicit operator
> stack, the way a professional tool would: an exact precedence and associativity rule, a
> scripted version of the textbook's "Another?" dialog, a precise diagnostic for every
> malformed expression, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 46 is adapted from §10.5 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that reads an infix expression, converts it to postfix (reverse Polish) notation with
Dijkstra's shunting-yard algorithm, prints the result, and asks `Another? (y/n)`. The textbook
version trusts its input: an unbalanced parenthesis or a stray operator produces a wrong answer
or none. This project keeps the algorithm, the precedence table, and the report layout, and
turns the program into a well-behaved command-line tool. The engineering focus is a stack-based
converter that _validates_ while it converts — every malformed expression is rejected with the
first error found, scanning left to right — and an interactive dialog that reads the same
sequence of answers from a keyboard, a pipe, or a file.

## Operational scope

| In scope                                                                                | Out of scope                                                   |
| :-------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| Operands that are runs of ASCII letters and digits (`A`, `x1`, `40`)                    | Unary operators, functions, exponentiation, real-number syntax |
| Operators `+ - * / %` (left-associative, `* / %` before `+ -`) and parentheses          | Evaluating the expression                                      |
| One expression per line, alternating with `y`/`n` answers to `Another? (y/n)`           | Several expressions on one line                                |
| Standard input or one `FILE` operand (`-` is standard input)                            | Several input files, writing files                             |
| `Infix:` / `Postfix:` report with single-space-separated postfix tokens                 | Other output notations (prefix, trees)                         |
| Diagnostics for malformed expressions (the dialog continues) and bad answers (it stops) | Error recovery inside an expression                            |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                          | Prompts on standard output                                     |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                           | Other legacy encodings                                         |
| `--help`, `--version`, CONV-13 usage errors, CONV-16 file errors                        | Configuration files, environment variables                     |

## Learning objectives

1. Implement the shunting-yard algorithm with an explicit operator stack and a precedence
   table, including left associativity (`A - B - C` → `A B - C -`) (FR-04).
2. Validate an expression in the same single left-to-right pass that converts it, using a
   two-state scanner (expecting an operand or an operator), so the first error is reported
   exactly and deterministically (FR-05).
3. Tokenize a line by hand: maximal runs of operand characters, single-byte operators,
   insignificant blanks, and everything else rejected (FR-03).
4. Map an interactive question-and-answer dialog onto scripted input, keeping prompts on
   standard error so that redirected output is identical with or without them (FR-07, FR-09).
5. Read line-oriented input identically on every platform: LF and CRLF line ends, a missing
   final line feed, and the Ctrl-Z end-of-file byte of old DOS files (NFR-02).

## What is provided

| Path                   | Contents                                                                                |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-14, NFR-01 … NFR-08)                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                 |
| `tests/fixtures/`      | Input files shared by both suites (`readme.txt`, `mixed.txt`, `errors.txt`, `stop.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates     |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-infix`, with unit tests — including the conversion and error
   tables that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-infix into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

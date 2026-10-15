<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 01 — Stream Echo & Formatting (`dp-echo`)](#project-01--stream-echo--formatting-dp-echo)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 01 — Stream Echo & Formatting (`dp-echo`)

> Re-create `echo` so that it behaves identically, byte for byte, on Linux, macOS, and Windows:
> traditional option handling, newline control, backslash escapes, exit statuses, and line
> endings that are decided by the specification instead of by the platform.

## Purpose

`echo` looks trivial, yet it is one of the least portable commands in everyday use: shells
disagree about whether it interprets backslashes, whether `-n` is an option, and which line
ending it writes. Project 01 turns that mess into a precise specification. It is also the first
project that _deliberately_ departs from the shared CLI conventions (only leading `-n`/`-e`/`-E`
tokens are options, `--help` works only on its own, and there are no usage errors), so it
teaches how to read, honor, and document an override.

The cross-platform focus is **line endings**: the tool always terminates its output with LF,
never CRLF, on every OS, and it produces CRLF only when the user explicitly asks for it with
escapes (`-ne 'text\r\n'`).

## Operational scope

| In scope                                                                  | Out of scope                                   |
| :------------------------------------------------------------------------ | :--------------------------------------------- |
| Writing operands separated by single spaces                               | Reading stdin or files                         |
| Suppressing the trailing LF (`-n`)                                        | `printf`-style format specifiers               |
| Backslash escapes (`-e`, `-E`), including `\c`, `\0NNN`, `\xHH`           | Locale-dependent behavior, `POSIXLY_CORRECT`   |
| GNU-style leading-option parsing; `--help` / `--version` as sole argument | Long options other than `--help` / `--version` |
| LF-only output; explicit CRLF through escapes                             | Automatic line-ending conversion               |
| Exit statuses 0 (success) and 1 (write failure)                           | Usage errors (there are none)                  |

## Learning objectives

1. Implement a hand-written argument classifier that differs from the common conventions, and
   document exactly where and why it differs (SRS §2.5).
2. Write byte-oriented output: put standard output in binary mode so Windows never turns LF into
   CRLF (CONV-03), and pass UTF-8 arguments through unchanged (CONV-05).
3. Implement a small, fully specified escape-sequence scanner as a pure, unit-tested function,
   including greedy bounded digit runs, unknown escapes, and early termination (`\c`).
4. Reason about exit statuses when no input can be invalid, and handle output failures (broken
   pipe versus other write errors).
5. Continue the white-box lifecycle: HLD → LLD → code → RTM → test plan.

## What is provided

| Path                   | Contents                                                                               |
| :--------------------- | :------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-16)                                                      |
| `specs/SRS.md`         | System requirements (FR-01 … FR-15, NFR-01 … NFR-08), including the CLI-CONV overrides |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                 |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                   |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates    |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-echo`, with unit tests (at least one per row of the SRS FR-07 escape
   table, plus the FR-09 and FR-10 examples).
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-echo into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

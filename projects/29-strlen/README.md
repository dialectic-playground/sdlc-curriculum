<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 29 — String Length from First Principles (`dp-strlen`)](#project-29--string-length-from-first-principles-dp-strlen)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 29 — String Length from First Principles (`dp-strlen`)

> Measure strings by walking them, the way a professional tool would: lengths of command-line
> strings or of every input line, counted in UTF-8 characters or in bytes by one fixed
> definition, by an explicit scan that holds no line in memory, with byte-identical output on
> Linux, macOS, and Windows.

## Purpose

Project 29 is adapted from §5.8 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a function that computes the length of a string by stepping through it until the terminating
null byte, counting as it goes. The textbook function counts bytes and relies on the null
terminator, so it cannot measure text that contains a NUL byte and miscounts every non-ASCII
letter. This project keeps the essential idea — the length is found by an explicit scan, never
read from a stored length — and turns it into a useful command-line tool: it prints the length
of each string operand, or of each line of its input, in characters under the same UTF-8 rule
as `dp-wc` (Project 04) or, with `-b`, in bytes. [Project 27](../27-line-wrap/) and
[Project 33](../33-reverse/) measure text by the same rule.

## Operational scope

| In scope                                                              | Out of scope                                             |
| :-------------------------------------------------------------------- | :------------------------------------------------------- |
| Length of each STRING operand                                         | Display widths (wide or combining characters, TAB stops) |
| Length of each line of standard input or of one file (`-f`, `--file`) | Several input files in one run                           |
| Characters by the SRS-04 UTF-8 rule, or bytes (`-b`)                  | Grapheme clusters, normalization                         |
| LF-terminated lines; one CR before LF removed; NUL bytes are data     | Other line terminators (CR alone, U+2028)                |
| A trailing Ctrl-Z end-of-file marker (CONV-37)                        | Other legacy encodings                                   |
| Counting by an explicit scan in constant memory                       | Totals, maximum, or other statistics                     |
| CONV-16 file errors, `--help`, `--version`, CONV-13 usage errors      | Configuration files, environment variables               |

## Learning objectives

1. Compute a length by an explicit scan from the first byte, and explain why it costs O(_n_)
   time where a stored length costs O(1) (FR-06).
2. Contrast a sentinel-terminated string with a counted one: a NUL byte is data here, not the
   end (FR-04).
3. Measure text in characters by a fixed, locale-independent UTF-8 rule, including every kind of
   invalid byte, and contrast it with measuring in bytes (FR-05).
4. Define lines precisely across platforms: LF terminators, CRLF files, a missing final LF, and
   a trailing Ctrl-Z (FR-04, NFR-02).
5. Stream an input of any size, with lines of any length, in constant memory (NFR-03).

## What is provided

| Path                   | Contents                                                                                |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-13)                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-12, NFR-01 … NFR-08)                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                 |
| `tests/fixtures/`      | Input files shared by both suites (`lines.txt`, `crlf.txt`, `utf8.txt`)                 |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates     |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-strlen`, with unit tests — including the scan tests that NFR-06
   requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-strlen into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

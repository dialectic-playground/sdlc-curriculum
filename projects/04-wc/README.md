<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 04 — Word, Line, and Byte Counter (`dp-wc`)](#project-04--word-line-and-byte-counter-dp-wc)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 04 — Word, Line, and Byte Counter (`dp-wc`)

> Count lines, words, UTF-8 characters, and bytes the way `wc` does — but with one answer for
> the same bytes on every operating system and in every locale, a fully specified output
> layout, and constant memory on inputs of any size.

## Purpose

Earlier projects copied or sliced bytes. Project 04 is the first that must _interpret_ them:
as words separated by whitespace, as UTF-8 characters that may be damaged or truncated, and as
lines whose length is measured in characters. Traditional `wc` leaves these definitions to the
locale and derives its column widths from file sizes; this project replaces every such
dependency with an exact rule, so independent implementations agree byte for byte. The central
engineering challenge is a streaming, incremental counter that gets the same answer no matter
where the read-buffer boundaries fall — including in the middle of a multibyte character.

## Operational scope

| In scope                                                             | Out of scope                                      |
| :------------------------------------------------------------------- | :------------------------------------------------ |
| Line (LF), word, character, and byte counts (`-l`, `-w`, `-m`, `-c`) | Locale-dependent word and character rules         |
| Maximum line length in characters (`-L`)                             | Display-width (column) measurement, tab expansion |
| Fixed column order and a deterministic width rule                    | GNU's size-dependent column widths                |
| Multiple files with a `total` line; standard input and `-`           | `--files0-from`, `--total=WHEN`                   |
| Strict UTF-8 decoding with a per-byte rule for invalid sequences     | Encodings other than UTF-8                        |
| CONV-16 file diagnostics, continuing after failures                  | Directory traversal                               |
| `--help`, `--version`, CONV-13 usage errors                          | Colors, quoting of file names                     |

## Learning objectives

1. Implement an incremental (streaming) counting engine with constant memory, whose results do
   not depend on read-buffer size (NFR-03, NFR-05).
2. Decode UTF-8 by hand against the Unicode well-formedness table, including overlong forms,
   surrogates, out-of-range values, and truncated sequences (FR-06).
3. Replace locale- and platform-dependent library behavior with byte-level definitions that
   give identical results on Linux, macOS, and Windows (NFR-02).
4. Design a report formatter whose layout depends on every value it prints (FR-09) and test it
   as a pure function.
5. Handle per-operand failures without losing the rest of the work (FR-13, CONV-17).
6. Write unit tests that systematically split inputs at every boundary.

## What is provided

| Path                   | Contents                                                                                |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-17)                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-18, NFR-01 … NFR-10)                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                 |
| `tests/fixtures/`      | Input files shared by both suites (`poem.txt`, `utf8.txt`, `crlf.txt`)                  |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates     |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-wc`, with unit tests — including the chunk-splitting tests that
   NFR-05 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-wc into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

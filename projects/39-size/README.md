<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 39 — Binary File Byte Size Inspector (`dp-size`)](#project-39--binary-file-byte-size-inspector-dp-size)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 39 — Binary File Byte Size Inspector (`dp-size`)

> Take a file name without its extension, append `.c`, and report the file's exact size in
> bytes by reading it — the way a professional tool would: binary-mode input so that NUL, CR,
> and Ctrl-Z bytes all count, several names from the command line or standard input, exact
> diagnostics that name the file, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 39 is adapted from §8.3 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that asks for a file name without its extension, appends `.c`, opens the file in
binary mode, and counts its bytes until end-of-file. The lesson is the difference between
_binary_ and _text_ input. In text mode, a Windows C library turns each CRLF into LF and stops
at the first Ctrl-Z byte, so the same file would have different sizes on different systems; in
binary mode every byte is counted, everywhere. Around that core, the project adds what a real
tool needs: names from arguments or standard input, a choice of extension, records that name
their file, and failures that are reported without stopping the other names.

## Operational scope

| In scope                                                                         | Out of scope                                             |
| :------------------------------------------------------------------------------- | :------------------------------------------------------- |
| Names as operands, or one per line on standard input (`-` reads standard input)  | Measuring standard input itself, directory totals        |
| Extension `.c` appended by default; `-e`/`--extension` chooses another or none   | Wildcards, recursive traversal                           |
| Exact byte count by binary-mode reading: NUL, CR, and Ctrl-Z bytes counted       | File-system metadata (`stat` size), human-readable units |
| Two-line records (`File name:` / `Byte size:`) in the textbook's TAB layout      | Other output formats, totals                             |
| Optional prompt `File name (NO extension):` on standard error (`-p`, `--prompt`) | Interactive line editing                                 |
| CRLF names and a trailing Ctrl-Z in the name input (CONV-37)                     | CONV-37 applied to measured files (it never is)          |
| CONV-16 errors that name the constructed file, continuing with the next name     | Configuration files, environment variables               |
| `--help`, `--version`, CONV-13 usage errors                                      |                                                          |

## Learning objectives

1. Read a file in binary mode in fixed-size blocks and count its bytes exactly, in memory that
   does not depend on the file's size (FR-04, NFR-03).
2. Explain, and demonstrate with fixtures, how text-mode input changes the count of a file with
   CRLF line endings or Ctrl-Z bytes on Windows (NFR-02).
3. Build file names by concatenation and report failures with the name as constructed, mapped
   to fixed, portable reasons (FR-03, FR-07, CONV-16).
4. Process a sequence of names from two sources, one line at a time, with prompts that never
   mix into standard output (FR-01, FR-02, FR-09).
5. Keep going after a failure and summarize the outcome in the exit status (FR-10, CONV-17).

## What is provided

| Path                   | Contents                                                                                                                                                                                                                                                                                                   |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-13)                                                                                                                                                                                                                                                                          |
| `specs/SRS.md`         | System requirements (FR-01 … FR-14, NFR-01 … NFR-08)                                                                                                                                                                                                                                                       |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                                                                                                                                                                                                                    |
| `tests/fixtures/`      | Files shared by both suites: `size.c` (562 bytes, the size in the textbook example), `binary.c` (every byte value, NUL bytes, CRLF pairs, Ctrl-Z bytes), `crlf.c`, `ctrlz.c`, `empty.c`, `notes.txt`, `license`, `sub/inner.c`, the directory `dir.c/`, and the name lists `size-name.txt` and `names.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                                                                                                                                                                                                     |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                                                                                                                                                                                                    |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                                                                                                                                                                                        |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-size`, with unit tests.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-size into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.

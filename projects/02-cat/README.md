# Project 02 — Concatenate & Number Files (`dp-cat`)

> Join files and standard input into one output stream, exactly as the bytes arrive. On request,
> number lines, squeeze blank runs, and make control bytes, tabs, and CRLF line endings visible.
> Do all of it in constant memory, with identical output on Linux, macOS, and Windows.

## Purpose

Project 02 is the curriculum's first tool that reads files. Its algorithm is modest, but it
teaches the habits every later file-processing tool depends on:

- treat data as **bytes**, never as text to be "fixed up";
- **stream**: use a fixed buffer, whatever the size of the file or the length of its lines;
- **manage file descriptors**: open one file at a time and close it promptly on every path;
- **keep going**: one failed operand is reported and the rest are still processed.

The cross-platform focus is the classic Windows pitfalls. Text-mode I/O silently converts CRLF
and stops at Ctrl-Z, and opening a directory fails with a different error. The `-A` option
turns these into the visible **CRLF lesson**: every Windows line end shows up as `^M$`.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Concatenating any number of files and `-` (standard input), in order | Line-ending or character-set conversion |
| Byte-exact copying of binary data and CRLF files | Recursing into directories |
| Numbering all lines (`-n`) or non-empty lines (`-b`) across files | Paging, colors, terminal control |
| Squeezing blank-line runs (`-s`) | Detecting that an input is also the output file |
| `-v` / `-T` / `-E` / `-A` visualization (`^X`, `M-`, `^I`, `$`, `^M$`) | GNU-only `-e`, `-t`, `-u` |
| CONV-16 diagnostics that continue past failures; exit status 1 | Configuration files, environment variables |
| `--help`, `--version`, CONV-13 usage errors (exit 2) | |

## Learning objectives

1. Read files and standard input in binary mode with large buffers, and write standard output
   in binary mode on every OS (CONV-03, CONV-04, NFR-01, NFR-03).
2. Design a **chunk-independent streaming state machine**: the output must not depend on where
   buffer or file boundaries fall, even when a CR and its LF arrive in different reads (FR-05,
   FR-13, NFR-08).
3. Manage resources deterministically: one open file at a time, closed on every path, with
   standard input never closed (FR-03, NFR-05).
4. Map operating-system errors to fixed, portable diagnostics, and continue after a failure
   (CONV-16, CONV-17, FR-14).
5. Specify and reproduce a classic Unix tool's exact semantics (GNU `cat` line numbering and
   `^`/`M-` notation) from a written specification alone.

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-20, NFR-01 … NFR-10) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites: CRLF, control and high bytes, no final newline, blank runs, an empty file, and a directory |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-cat`, with unit tests. The tests must include the chunk-boundary
   tests required by NFR-08.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-cat into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when all of the following hold:

- `make test` and `make test-hidden` pass on all three operating systems in CI;
- `make lint` is clean;
- the memory and streaming measurements for NFR-02 … NFR-04 are recorded in the master test
  plan;
- every RTM row is *Verified*.

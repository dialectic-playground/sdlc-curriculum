# Project 36 — Stream Text Pagination Utility (`dp-page`)

> Break a stream of text into numbered, printable pages of 52 lines, each opened by a header
> and closed by a form feed, the way a professional filter would: every input byte copied
> exactly, no empty page ever written, memory that does not grow with the input, and
> byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 36 is adapted from §7.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a filter that copies its standard input to its standard output in pages of 52 lines, writing
`Page     N` and a blank line at the top of each page and a form feed (the printer's
"eject page" control character) after it. The textbook version reads the keyboard only, has a
fixed page length, and leaves the corner cases of the end of the input to the reader. This
project keeps its page layout byte for byte and turns it into a well-behaved command-line
filter. The engineering focus is *boundary conditions on stream exhaustion*: the end of the
input can arrive at the start of a page, in the middle of one, exactly at a page boundary, or
in the middle of a line, and in every case the output must be exactly right — never an empty
trailing page, never a lost or invented byte.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Pages of 52 input lines, each with a `Page     N` header, a blank line, and a closing form feed | Page footers, margins, columns, line numbering, page width |
| Any page length from 1 line up (`-l`, `--lines`) | Headers with file names, dates, or titles |
| Standard input and any number of `FILE` operands, read as one stream (`-` is standard input) | Restarting page numbers for each file |
| Byte-for-byte copying of every input line, including CR, NUL, form feed, and Ctrl-Z bytes (CONV-04) | Converting line endings or expanding tabs |
| A final line without a newline, copied without one | Adding missing newlines |
| CONV-16 file errors, continuing with the next operand (CONV-17) | Data diagnostics: no input byte is ever invalid |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables, printer control |

## Learning objectives

1. Write a stream filter whose state (page number, lines on the current page, whether a page
   is open) carries across chunk and file boundaries, so the result never depends on how the
   input is split into reads (FR-01, NFR-06).
2. Handle every way a stream can end — empty, at a page boundary, mid-page, mid-line — and
   prove each case with a test instead of an assumption (FR-05).
3. Copy data byte for byte, treating CR, NUL, and control characters as data, so that removing
   the inserted headers and form feeds gives back the input exactly (FR-02, FR-06).
4. Use an ASCII device-control character (form feed, `0x0C`) as part of a specified output
   format, and write it identically on every operating system (NFR-02).
5. Keep memory bounded for inputs of any size and lines of any length (NFR-03).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-13) |
| `specs/SRS.md` | System requirements (FR-01 … FR-12, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`lines50.txt`, `lines53.txt`, `lines104.txt`, `poem.txt`, `noeol.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.
Expected outputs contain form feed bytes and end without a newline; view them with `od -c`
or a hex viewer rather than a text editor.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-page`, with unit tests — including the chunk-boundary tests that
   NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-page into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

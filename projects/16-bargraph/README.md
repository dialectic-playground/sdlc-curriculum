# Project 16 — ASCII Comic Book Bar Graph Generator (`dp-bargraph`)

> Draw a terminal bar graph from alternating title and value lines, reading the same data file
> identically on every operating system — LF or CRLF line endings, with or without an MS-DOS
> Ctrl-Z marker — and pinpointing bad data by line number.

## Purpose

Project 16 is adapted from §2.8 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*,
where a short program echoes comic-book titles and draws a bar of asterisks for each book's
value. The program is small, but its input is not: it interleaves free-text lines with numeric
lines, and the textbook's data file still ends with the Ctrl-Z byte an MS-DOS editor wrote in
1996. The engineering challenge is to define a line-oriented format exactly — what a line is,
what happens to CR, what a value line may contain, what a blank line means and where — and to
read it as bytes, so that no platform's text-mode conventions can change the result.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Alternating title and value lines from one FILE or standard input | Several input files |
| One `*` per 2 units of value (integer division), values 0–10000 | Other scales, negative or fractional values |
| Titles echoed byte for byte (spaces, empty titles, any encoding) | Decoding or validating title text |
| LF and CRLF line endings; trailing Ctrl-Z marker (CONV-37) | Other legacy encodings or line-ending conventions |
| Trailing blank lines ignored | Comments, headers, or sorting |
| CONV-34 data diagnostics with line numbers; CONV-16 file errors | Recovering after a data error |
| `--help`, `--version`, CONV-13 usage errors | Colors, vertical bars |

## Learning objectives

1. Specify and implement a line-oriented record format precisely, including CR handling, blank
   lines, and end of input in the middle of a record (FR-02 … FR-06).
2. Read input as bytes and apply legacy rules (CRLF, the Ctrl-Z end-of-file marker) explicitly
   rather than through platform text mode (NFR-02).
3. Validate numeric fields strictly against a grammar and a range, with exact diagnostics that
   name the line (FR-06, FR-08).
4. Decide, and test, what happens to output already written when an error is found (FR-08).
5. Separate parsing, validation, and rendering into pure, unit-tested functions (NFR-05,
   NFR-06).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-16) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites: `bargraph.in` (from the textbook's companion disk), `edge.txt`, `crlf.txt`, `trailing.txt`, `badvalue.txt`, `truncated.txt` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-bargraph`, with unit tests for line splitting, record validation,
   and bar rendering.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-bargraph into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

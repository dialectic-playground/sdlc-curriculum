# Project 31 — Student Directory Lookup via Selection Sort & Binary Search (`dp-phone`)

> Load a file of fixed-width student records, sort it, and answer last names with the matching
> record — the way a professional lookup tool would: every record checked before the first
> answer, exact byte-wise matching that treats `Von Neumann` as one name, one answer per name as
> soon as it is typed, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 31 is adapted from §5.11 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that reads the student records of `students.dat` (last name, first name, and
telephone number in fixed columns), sorts them with selection sort, and then looks up each last
name typed at the keyboard with binary search on the blank-padded last-name column. The
textbook version assumes a well-formed data file and says nothing about names with spaces, bad
records, or other platforms' line endings. This
project keeps its algorithms and its answers word for word, and turns it into a well-behaved
command-line tool. The engineering focus is fixed-width data handled as *bytes* — column
widths, line endings, and comparisons that do not depend on the platform or the locale — and
two classic algorithms implemented exactly as specified, so that even the choice among students
who share a last name is the same in every implementation.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Student file `students.dat`, or the file named by `-f`/`--file` (`-` is standard input) | Several student files, writing or updating records |
| Fixed-width 62-byte records, each checked before any name is answered | Variable-width or delimited formats |
| Selection sort by whole record; binary search on the 25-byte padded last name | Library sort or search routines |
| Names as whole lines (spaces allowed) from standard input or one `FILE` operand | Partial, prefix, or case-insensitive matching |
| One answer per non-empty name, flushed before the next name is read | Listing every student who shares a last name |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF line endings and a trailing Ctrl-Z end-of-file marker in both inputs (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Repairing malformed records |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Parse fixed-width records by byte position, and decide exactly what a malformed record is
   and how it is reported (FR-02, FR-03).
2. Implement selection sort and binary search by hand, exactly as specified, and test them at
   their boundaries: the first and last records, missing keys on either side, and duplicate
   keys (FR-04, FR-06, NFR-06).
3. Compare strings as unsigned bytes, independent of locale and case, so that sorting and
   matching give the same result on every platform (NFR-02).
4. Write a line-oriented interactive loop that answers each line as soon as it is complete,
   with optional prompts on standard error (FR-05, FR-08).
5. Order a program's operations so that every input problem is found before any answer is
   written (FR-09).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-15) |
| `specs/SRS.md` | System requirements (FR-01 … FR-13, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites: `students.dat` (from the textbook's companion disk), `names.txt`, `edges.txt`, `more.dat`, `dups.txt`, `bad.dat` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-phone`, with unit tests for the sort, the search, and the line
   reader that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-phone into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

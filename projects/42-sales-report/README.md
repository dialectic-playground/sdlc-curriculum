# Project 42 — Enterprise Sales Reporting & Relational Data Integration (`dp-sales`)

> Join two flat files — accounts and the salespeople who manage them — and print a
> hierarchical sales report, the way a professional reporting job would: every record checked
> and every reference resolved before the first byte is written, exact decimal money, a stated
> sort order, and a report that matches the textbook's sample byte for byte on Linux, macOS,
> and Windows.

## Purpose

Project 42 is adapted from §9.7 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.
A sales department keeps two files. The accounts file (`sales.dat`) holds one line per customer
account: an id, a name, the actual sales, and the projected sales. The salesperson file
(`sper.dat`) holds one line per salesperson: name, sales coach, region, base salary, bonus, and,
after a `#`, the ids of the accounts the salesperson manages. The ids are *foreign keys*: the
tool sorts the accounts by id, resolves every id by binary search, sorts the salespeople by
name, and prints the report whose exact layout is given by the textbook's sample report
`sales.rpt`.

The project is about relational data in flat files: parsing two record formats, validating
keys (duplicates, dangling references), linking records instead of copying them, sorting with
a comparison function, and producing a fixed-layout report — including its blank lines and
trailing spaces — exactly.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Accounts from `sales.dat`, or the file named by `-a`/`--accounts` | Updating either file, other report layouts |
| Salespeople from `sper.dat`, or the file named by `-s`/`--salespeople` | Joins on anything but the account id |
| Either file from standard input (`-`), but not both | Report totals, sub-totals, or percentages |
| Up to 100 accounts and 100 salespeople; ids 0 … 2⁶³−1 | Larger data sets, external sorting |
| Exact decimal amounts with at most two decimals, printed with two decimals | Binary floating-point money, currencies, negative amounts |
| Validation of both files (fields, amounts, duplicate ids, unknown ids) before any output | Partial reports after a data error |
| CRLF input, trailing Ctrl-Z (CONV-37), data diagnostics with line numbers (CONV-34) | Prompts or any other interaction |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Parse two line-oriented record formats with field validation and precise diagnostics
   (FR-03, FR-05).
2. Resolve foreign keys with binary search over records sorted by a comparison function, and
   detect duplicate and dangling keys (FR-03, FR-05, FR-06).
3. Represent money exactly as decimal (whole cents), not as binary floating point (FR-04).
4. Sort records with a stated, locale-independent, stable order (FR-07).
5. Produce a fixed-layout report — indentation, blank lines, and trailing spaces — byte for
   byte, and only after all input has been validated (FR-08, FR-09).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-15, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Inputs shared by both suites: `sales.rpt` (from the textbook's companion disk), `sales.dat`, `sper.dat`, `team.dat`, `mixed.dat`, `unknown.dat`, `dup.dat`, `bad-amount.dat` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

`sales.rpt` is the textbook's sample report, byte for byte; do not modify it. The textbook did
not supply its input files: `sales.dat` and `sper.dat` were written for this project from the
accounts and salespeople that appear in `sales.rpt`, listed out of order so that both sorts
matter. Public test 01 runs `dp-sales` on them, and its expected standard output is identical
to `sales.rpt`.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-sales`, with unit tests.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-sales into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

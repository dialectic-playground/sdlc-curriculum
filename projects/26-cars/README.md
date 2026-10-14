# Project 26 — Car Dealership Daily Sales & Inventory Tracker (`dp-cars1`)

> Enter a dealership's opening stock for twelve brands and the day's sales, and print a
> `DAILY REPORT` of stock, sales, closing stock, and sales share — the way a professional tool
> would: indexed per-brand totals, impossible sales refused without losing the day, an exact
> report layout, precise diagnostics, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 26 is adapted from §5.3 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that keeps the opening stock and the sales of twelve car brands in two arrays indexed
by brand number, reads sales until a negative brand is entered, and prints a daily report. The
textbook version accepts any quantity (so a lot can end the day with a negative number of
cars), divides by zero for a brand with no stock, and does not say how its report is laid out.
This project keeps its dialog, prompts, and report contents and turns it into a well-behaved
command-line tool. The engineering focus is the *indexed collection* — per-brand totals held
and processed by index rather than by name — together with a dialog that validates each entry
as it arrives, refuses impossible sales with a located message, and still produces a correct
report. [Project 28](../28-cars-modular/) revisits the same program with the report as an
independent component.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Opening stock of brands 0 … 11 (0 … 999999 each), then (brand, quantity) sales as integer tokens (CONV-32, CONV-33) | Brand names, prices, revenue, a different number of brands |
| End of the day at a negative brand or at the end of the input | Several days, carried-over stock |
| Refusing unknown brands, negative quantities, and overselling, then continuing | Returns or corrections of earlier sales |
| A fixed-layout `DAILY REPORT` with a `FIX`-formatted percentage and `n/a` for empty lots (CONV-35) | Other report formats, saving totals (see Project 28) |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files, writing files |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Recovering from an invalid token |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Hold related per-category data in indexed collections and process it with loops over the
   index, with the category count as one named constant (NFR-05).
2. Drive a two-phase, sentinel-terminated dialog from a token stream that works the same at a
   keyboard and in a pipeline (FR-03, FR-04, FR-08).
3. Separate *recoverable* entry errors, which are reported and skipped, from *fatal* data
   errors, which stop the run before a misleading report is written (FR-05, FR-09).
4. Guard every index and every subtraction: reject out-of-range brands, compare quantities
   without overflow, and define the percentage for a zero denominator (FR-05, FR-07).
5. Lay out a fixed-width report exactly and format a binary64 percentage reproducibly
   (FR-06, FR-07, CONV-35).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-16) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`day.txt`, `rejected.txt`, `noend.txt`, `cut.txt`, `bad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-cars1`, with unit tests — including the sale-check, percentage, and
   report-formatter tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-cars1 into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

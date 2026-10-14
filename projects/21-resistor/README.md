# Project 21 — Resistor 3-Band Color Code Decoder (`dp-resistor`)

> Show the resistor color guide, then turn three color bands at a time into a resistance in
> ohms, kilo-ohms, or mega-ohms, the way a professional dialog tool would: exact arithmetic,
> one answer per resistor as soon as its codes are typed, a typo reported and asked for again,
> and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 21 is adapted from §4.4 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that prints a menu of resistor color codes, reads the three one-letter codes of a
resistor's bands, prints its resistance in ohms, kilo-ohms, or mega-ohms, and asks whether to
decode another. The textbook version is a keyboard dialog that only a person at a terminal can
drive. This project keeps its color table, its unit thresholds, and its six-decimal results,
and turns it into a command-line tool that reads the same responses from a keyboard, a pipe, or
a file. The engineering focus is *multi-way decoding* through one lookup table, *recoverable*
input errors (an invalid code is reported and the dialog continues, as in the textbook) versus
*fatal* ones (a nonsensical answer ends the run), and a dialog loop whose behavior at the end
of the input is defined for every position.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| The color guide, written once at the start | 4-, 5-, and 6-band resistors, tolerance and temperature bands |
| Three one-letter color codes per resistor, read as tokens (CONV-32), in either letter case | Color names (`red`), digits, codes written without spaces (`YVR`) |
| Exact resistance 0 … 99 000 000 000 ohms, written with `FIX(x, 6)` (CONV-35) in ohms, kilo-ohms, or mega-ohms | Other unit prefixes, standard-value (E12) checking |
| The answer `1` or `0` after each resistance (decode another or stop) | Other answers such as `y` or `yes` |
| Invalid codes reported on standard error; the three codes are asked for again | Correcting a single code of a set |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Configuration files, environment variables |
| `--help`, `--version`, CONV-13 usage errors | Localized color names |

## Learning objectives

1. Decode a symbolic code into a number through one table that is the only place the ten
   colors appear, instead of a chain of special cases (FR-05, NFR-05).
2. Compute a value exactly in integer arithmetic and present it in an engineering unit chosen
   by magnitude thresholds, with a fixed number of decimals (FR-06, FR-07).
3. Distinguish a recoverable input error, reported while the dialog continues, from a fatal
   one, and reflect both in the exit status (FR-08, FR-09).
4. Define what a dialog does when its input ends at every possible point, so a script that
   feeds it a file gets a predictable result (FR-10).
5. Fold letter case using ASCII rules only, so the result never depends on the user's locale
   (NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-17, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`codes.txt`, `mixed.txt`, `invalid.txt`, `bounds.txt`, `answer.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-resistor`, with unit tests — including the decoding table, every
   unit boundary, and the end-of-input cases that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-resistor into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

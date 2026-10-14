# Project 27 — Greedy Word-Wrapping Text Formatter (`dp-wrap`)

> Fill a stream of words into lines no longer than a given length, the way a professional
> filter would: a precise greedy rule, lengths measured in UTF-8 characters or bytes by one
> fixed definition, a clear report for every word that cannot fit, and byte-identical output on
> Linux, macOS, and Windows.

## Purpose

Project 27 is adapted from §5.5 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that reads a line length and then a stream of words, and writes the words greedily,
separated by single spaces, so that no line exceeds the length. The textbook version reads into
a fixed-size word buffer, counts bytes, and prints its error message into the middle of the
formatted text. This project keeps its greedy rule and turns it into a well-behaved filter:
the line length may come from the data or from an option, word lengths are counted in UTF-8
characters (the same rule as `dp-wc`, Project 04) or in bytes, an over-long word is reported on
standard error and still written, and the arithmetic is safe for any line length up to 2⁶³−1.
[Project 29](../29-strlen/) and [Project 33](../33-reverse/) use the same character rule.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Words as whitespace-separated tokens (CONV-32), any line structure | Hyphenation, justification, indentation |
| Line length from the first token, or from `-w`, `--width` (1 … 2⁶³−1) | Display widths (wide or combining characters, TAB stops) |
| Word lengths in UTF-8 characters (SRS-04 rule) or bytes (`-b`) | Preserving paragraphs or blank lines |
| Over-long words reported on standard error and written on a line of their own | Breaking a word across lines |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files, writing files |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Prompts (the textbook program did not prompt) |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Implement a greedy packing algorithm exactly, including the boundary where a line reaches
   the limit exactly (FR-05).
2. Measure text in characters by a fixed, locale-independent UTF-8 rule, and contrast it with
   measuring in bytes (FR-04).
3. Process an unbounded stream of words in memory proportional to the longest word, not to the
   input or the line length (NFR-03).
4. Avoid integer overflow in a comparison whose operands can be as large as 2⁶³−1 (FR-05).
5. Separate data from diagnostics: errors go to standard error, the formatted text to standard
   output, and processing continues where that is the useful choice (FR-07).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-13, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`fox.txt`, `words.txt`, `utf8.txt`, `long.txt`, `badwidth.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.
`fox.txt` holds the example from the section's description.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-wrap`, with unit tests — including the placement and
   character-counting tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-wrap into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

# Project 33 — Two-Pointer In-Place Sequence Reversal (`dp-reverse`)

> Reverse short strings in place with two converging indices, the way a professional tool
> would: words or whole lines from a keyboard, a pipe, or a file, UTF-8 characters kept intact,
> a hard 100-character limit reported precisely, optional prompts on standard error, and
> byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 33 is adapted from §6.5 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that prompts for a string of up to 100 characters, reverses it in place by swapping
characters from both ends towards the middle, and prints the result. The textbook version reads
one word into a fixed array without checking its length and reverses bytes, so it overruns its
buffer on a long word and scrambles every multibyte UTF-8 character. This project keeps its
prompt, its report line, its limit, and its two-index algorithm, and turns it into a
well-behaved tool: it reverses every word (or, with `-l`, every line) of its input, reverses
UTF-8 characters rather than bytes — still in place, in constant extra space — and reports a
string that exceeds the limit instead of overrunning anything. [Project 27](../27-line-wrap/)
and [Project 29](../29-strlen/) measure text by the same character rule.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Strings as whitespace-free words (CONV-32), or whole lines with `-l`, `--lines` | Reversing a whole file as one sequence |
| Reversal of UTF-8 characters (SRS-04 rule), or of bytes with `-b`, `--bytes` | Grapheme clusters (combining marks, emoji sequences) |
| In-place reversal with converging indices, O(1) extra space | Strings longer than 100 characters |
| The textbook prompt and report line; prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files, writing files |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Recovering after a string that is too long |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Implement the two-pointer reversal with converging indices, and reason about its boundaries:
   even and odd lengths, one character, an empty line (FR-07).
2. Reverse a sequence of variable-width units in place, in constant extra space, without
   breaking any unit apart (FR-06, FR-07).
3. Enforce a fixed capacity explicitly and report a violation precisely, instead of overrunning
   a buffer (FR-05).
4. Define a "string" exactly in scripted input — a word or a line — including CRLF files and a
   missing final line break (FR-02, FR-03).
5. Separate prompts (standard error) from results (standard output), so redirected output is
   identical with or without prompting (FR-09, CONV-36).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`words.txt`, `utf8.txt`, `lines.txt`, `toolong.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-reverse`, with unit tests — including the reversal tests that
   NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-reverse into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

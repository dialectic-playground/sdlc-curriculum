# Project 05 — Pattern Matching Search Engine (`dp-grep`)

> Find the lines that match a regular expression in files, pipelines, and whole directory
> trees, with a pattern language that means exactly the same thing on Linux, macOS, and
> Windows, and in every implementation language.

## Purpose

Every language ships a regular-expression engine, and no two agree completely. Backtracking
engines and linear-time automaton engines accept different syntax, treat `\`, `{`, and `]`
differently in different contexts, and differ in which text they report as "the" match. Project
05 turns that problem into the main lesson: you implement a `grep` whose **portable ERE subset**
is defined by an exact grammar (SRS section 5). You validate every pattern yourself, reject
unsupported constructs with precise diagnostics, and only then hand a translated pattern to an
engine, or match it with your own. Recursive search adds the second portability lesson: building
paths with `/` and visiting directory entries in a fixed byte-wise order, so that `-r` output
does not depend on the operating system or the file system.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Portable ERE subset: literals, `.`, brackets with ranges and POSIX classes, `^ $`, `* + ?`, `{m}`, `{m,}`, `{m,n}`, `\|`, `( )`, escaped metacharacters | Backreferences, lookaround, lazy/possessive quantifiers, `\d \w \s \b`, Unicode classes |
| Exact diagnostics for invalid and unsupported patterns (exit 2) | Printing only the matched text (`-o`), color, context lines (`-A -B -C`) |
| `-e` (repeatable), `-F`, `-i` (ASCII), `-v`, `-x`, `-w` | Pattern files (`-f`), `-L`, `-m`, include/exclude globs |
| `-n`, `-c`, `-l`, `-q`, `-s`, `-H`, `-h` | Binary-file detection, compressed files |
| `-r` with sorted pre-order traversal and `/`-joined paths | Following symbolic links found inside directories (`-R`) |
| Byte-oriented matching; CR kept as data; stdin and `-` | Locale-aware case folding |
| Three-valued exit status (0 selected, 1 none, 2 error; `-q` rule) | |

## Learning objectives

1. Write a recursive-descent parser and validator for a formally specified grammar, with a
   precisely defined first-error rule.
2. Understand where regular-expression dialects differ (escapes, bracket syntax, quantifier
   forms, anchors, byte versus code-point matching, match preference) and why "does this line
   match?" is engine-independent when the grammar is restricted.
3. Translate a validated syntax tree into a target engine's syntax safely, or match it directly,
   and prove equivalence with unit tests.
4. Traverse directory trees deterministically: byte-wise sorted entries, pre-order, `/`
   joining, symbolic links skipped (CONV-19 … CONV-21).
5. Stream large inputs line by line in binary mode with memory bounded by the longest line.
6. Implement an exit-status contract that differs from the curriculum default (CONV-18
   override), including the `-q` early-exit rule.

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-22) |
| `specs/SRS.md` | System requirements (FR-01 … FR-24, NFR-01 … NFR-12) and the portable ERE grammar |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Fixture files shared by both suites (text files, a CRLF file, and a directory tree) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-grep`, with unit tests that cover every grammar rule and every
   pattern-error reason in SRS section 5.6.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-grep into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

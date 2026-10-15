<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 06 — Recursive File Discovery Suite (`dp-find`)](#project-06--recursive-file-discovery-suite-dp-find)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 06 — Recursive File Discovery Suite (`dp-find`)

> Walk directory trees and select entries with a `find`-style expression language: glob names,
> types, sizes, ages, depth limits, boolean operators, and a command run for each match. The
> output order and bytes are identical on Linux, macOS, and Windows.

## Purpose

Project 06 is the curriculum's first tool that is driven by a small _language_ rather than by a
fixed set of options. Learners write a scanner and a recursive-descent parser for `find`'s
expression grammar, an evaluator with short-circuit semantics, a glob matcher built from first
principles, and a deterministic tree walker. They also start child processes portably. The
cross-platform focus is the file system itself: byte-wise ordering instead of whatever order the
OS returns, `/`-joined paths on Windows, Windows' 260-character `MAX_PATH` limit, and directories
that cannot be read.

## Operational scope

| In scope                                                                        | Out of scope                                                 |
| :------------------------------------------------------------------------------ | :----------------------------------------------------------- |
| Pre-order traversal of several start paths in byte-wise order                   | Following symbolic links (`-L`, `-H`), cycle detection       |
| `-name`, `-iname` with `*`, `?`, `[...]`, `[!...]`, `\` escapes                 | Regular-expression name tests, `-path`, `-regex`             |
| `-type f\|d`, `-size [+\|-]N[ckMG]`, `-mtime [+\|-]N`, `-empty`                 | Permission, owner, inode, and access-time tests              |
| `-maxdepth`, `-mindepth`                                                        | `-prune`, `-depth` (post-order), `-xdev`                     |
| `!`, `-not`, `-a`, implicit AND, `-o`, parentheses                              | The `,` operator, `-and` / `-or` spellings                   |
| `-print`, `-exec COMMAND ;` with `{}` substitution                              | `-exec … +` batching, `-ok`, `-delete`, `-printf`, `-print0` |
| Exact usage diagnostics; missing and unreadable paths reported without stopping | Reading standard input, configuration files                  |
| Windows long paths and access-denied folders                                    | Network file system specifics                                |

## Learning objectives

1. Design a scanner and a recursive-descent parser for an operator-precedence grammar, with
   precise, position-dependent syntax diagnostics (SRS FR-02 … FR-04).
2. Implement short-circuit evaluation over an expression tree, including actions with side
   effects (FR-03, FR-06, FR-15).
3. Build a glob matcher from a written specification, with exact bracket-expression and escape
   rules (FR-08, FR-09).
4. Traverse a file system deterministically: byte-wise order, `/` separators, no link following,
   iterative traversal for very deep trees (FR-05, FR-07, NFR-05).
5. Handle hostile file system conditions — Windows `MAX_PATH`, permission-denied directories,
   vanishing entries — and prove the handling with integration tests (FR-18, FR-22).
6. Start child processes without a shell, keep their output correctly ordered with your own,
   and report start failures exactly (FR-15, FR-16).

## What is provided

| Path                   | Contents                                                                                                 |
| :--------------------- | :------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-18)                                                                        |
| `specs/SRS.md`         | System requirements (FR-01 … FR-22, NFR-01 … NFR-10), including the deliberate CLI-CONV overrides (§1.5) |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                  |
| `tests/fixtures/`      | The fixture tree and two `-exec` helper scripts, copied into every test's working directory              |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                   |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                                     |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                      |

The black-box harness cannot portably create long paths, unreadable directories, or files with
specific old timestamps. Those requirements (FR-18, FR-22, and the full range of FR-12) are
verified by **your own** unit and integration tests, which your master test plan must describe.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-find`, with unit tests (scanner, parser, glob matcher, size and age
   arithmetic) and integration tests (permission-denied directories, paths over 260 characters,
   a very deep tree).
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-find into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, the FR-18 and FR-22 integration tests pass on their target
platforms, and every RTM row is _Verified_.

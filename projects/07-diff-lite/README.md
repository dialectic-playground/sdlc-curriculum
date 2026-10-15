<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 07 — Line-by-Line File Comparison (`dp-diff`)](#project-07--line-by-line-file-comparison-dp-diff)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 07 — Line-by-Line File Comparison (`dp-diff`)

> Compare two files line by line and print the differences in normal or unified format, with
> output so precisely defined that every correct implementation, in any language and on any
> operating system, prints exactly the same bytes.

## Purpose

Project 07 is the curriculum's first real algorithms project. Computing a shortest edit script
between two sequences is a classic dynamic-programming problem (longest common subsequence),
and Myers' O((N+M)·D) algorithm is one of the best-known practical refinements. The project
adds a specification lesson on top: because many shortest edit scripts usually exist, a
byte-exact test is only possible once the specification defines **one canonical edit script**
(SRS-07, FR-05) and lets implementers choose any algorithm that reproduces it (FR-07). The
cross-platform focus is deterministic formatting: LF-only output, no timestamps, and explicit
control over CRLF versus LF line endings.

## Operational scope

| In scope                                                             | Out of scope                            |
| :------------------------------------------------------------------- | :-------------------------------------- |
| Line-by-line comparison of two files, or a file and stdin (`-`)      | Directory comparison                    |
| Canonical shortest edit script (LCS-based definition)                | Whitespace/case-insensitive comparison  |
| Normal format (`NaM`, `NdM`, `NcM`)                                  | Context (`-c`) and side-by-side formats |
| Unified format (`-u`, `-U NUM`, `--unified[=NUM]`) with hunk merging | Timestamps in headers, colors           |
| `\ No newline at end of file` markers                                | Binary-file detection                   |
| `-q` / `--brief`, `--strip-trailing-cr`                              | Applying patches                        |
| Exit status 0 / 1 / 2 (same / different / trouble)                   | Heuristics that give up minimality      |

## Learning objectives

1. Implement the longest-common-subsequence recurrence and derive an edit script from it.
2. Understand why an _underspecified_ output ("any shortest diff") cannot be tested byte for
   byte, and how a mathematical definition with explicit tie-breaking fixes that.
3. Optionally, implement Myers' algorithm (or another fast method) and prove that it produces
   exactly the canonical script — and learn why tempting shortcuts such as common-suffix
   trimming can silently break equivalence.
4. Format output to exact conventions: 1-based ranges, hunk headers, context merging, and
   end-of-file markers.
5. Handle line endings deliberately: CR is data unless the user asks for normalization.
6. Design an exit-status contract (0/1/2) that overrides the common conventions for a reason.

## What is provided

| Path                   | Contents                                                                               |
| :--------------------- | :------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                      |
| `specs/SRS.md`         | System requirements (FR-01 … FR-19, NFR-01 … NFR-10), canonical edit script definition |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs and fixture files               |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                   |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates    |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`. The LLD must name the
   algorithm you chose and argue why it yields exactly the FR-05 script.
2. An implementation of `dp-diff`, with unit tests, including tests of the edit-script function
   on inputs with repeated lines (NFR-08).
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-diff into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

A good first milestone is the full L table of SRS FR-05 plus normal format (tests 01–03 and
06). Unified format, then the input edge cases, follow.

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, NFR-03 is met, and every RTM row is _Verified_.

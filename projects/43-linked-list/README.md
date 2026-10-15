<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 43 — Singly Linked List Foundations (`dp-elephnt1`, `dp-elephnt2`)](#project-43--singly-linked-list-foundations-dp-elephnt1-dp-elephnt2)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 43 — Singly Linked List Foundations (`dp-elephnt1`, `dp-elephnt2`)

> Build a list out of nodes that point to their successors — first three nodes linked by hand,
> then a list of any length grown from a keyboard dialog — and print it by walking the links,
> with a dialog that behaves the same at a keyboard and on a prepared file, and byte-identical
> output on Linux, macOS, and Windows.

## Purpose

Project 43 is adapted from §10.2 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_,
the section that introduces linked lists. It has two tools. `dp-elephnt1` creates three nodes
(Edna, Elmer, Eloise), links them by explicit assignments, and prints the list with a traversal
procedure that follows the links until the end marker. `dp-elephnt2` grows a list one node at a
time from a dialog — a name, then "Add another?" — appending at the tail, and prints it with the
same traversal. The output is trivial on purpose: the engineering focus is the _structure_
(self-referential nodes, an explicit end marker, O(1) appending through a tail reference, no
built-in array or list holding the names), which the SRS states as design requirements, and a
line-oriented dialog whose every edge — a blank name, a mistyped answer, the input ending in
the middle — has exactly one specified outcome.

## Operational scope

| In scope                                                                                     | Out of scope                                                        |
| :------------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| `dp-elephnt1`: three hand-linked nodes, one traversal, no input                              | Changing the three names                                            |
| `dp-elephnt2`: names and answers on alternate lines, any number of names                     | Names that span lines; editing or deleting names                    |
| Names trimmed of surrounding whitespace, otherwise copied byte for byte                      | Character-set conversion, length limits                             |
| Answers 0 or 1 (CONV-33 _integer_); the end of the input in place of an answer ends the list | Answers such as `y` / `n`                                           |
| `-p`, `--prompt` with the textbook's tab-indented prompts on standard error (CONV-36)        | Prompts on standard output                                          |
| Standard input or one `FILE` operand; CRLF input and a trailing Ctrl-Z (CONV-37)             | Several input files                                                 |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                            | Recovering after a data error                                       |
| Linked-structure design requirements, checked by design review                               | Sorting, searching, or freeing strategies beyond the end of the run |
| `--help`, `--version`, CONV-13 usage errors for both tools                                   | Configuration files, environment variables                          |

## Learning objectives

1. Define a self-referential node record and build a list from it, both statically (three
   nodes linked by assignments) and dynamically (one new node per name) (FR-01, FR-05,
   NFR-05).
2. Append in constant time by keeping a reference to the last node, and terminate the list
   with an explicit end marker that the traversal relies on (FR-05, NFR-05).
3. Write one traversal procedure that serves both programs and counts nodes as it walks
   (FR-02, NFR-05).
4. Implement a line-oriented dialog that reads incrementally, writes prompts to standard error
   before each read, and treats every way the dialog can end — answer 0, end of input, a bad
   answer, a blank name — exactly as specified (FR-04, FR-05, FR-07, FR-08, FR-10).
5. Validate the whole dialog before printing anything, so a failed run never prints a partial
   list (FR-09).

## What is provided

| Path                   | Contents                                                                                                                                             |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-15)                                                                                                                    |
| `specs/SRS.md`         | System requirements (FR-01 … FR-15, NFR-01 … NFR-08)                                                                                                 |
| `specs/user-manual.md` | Complete user manual for both tools, including both normative help texts                                                                             |
| `tests/fixtures/`      | Input files shared by both suites: `readme.txt` (the dialog shown in the textbook section), `herd.txt`, `no-answer.txt`, `bad-answer.txt`, `cut.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                                               |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                                              |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                                  |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the node record, the list-building procedure, and the shared traversal that NFR-05 requires.
2. Implementations of `dp-elephnt1` and `dp-elephnt2`, with unit tests — including the
   traversal of an empty, a one-node, and a three-node list, and the line reader split at every
   byte position (NFR-06).
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain, building and
   installing both executables (see `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-elephnt1 and dp-elephnt2 into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, the design review confirms NFR-05, and every RTM row is
_Verified_.

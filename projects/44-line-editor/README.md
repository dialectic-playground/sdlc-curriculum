# Project 44 — Modal Line-Oriented Text Editor (`dp-line-ed`)

> Edit a text file with a classic line editor — a linked buffer headed by a `[BOF]` sentinel,
> a current-line pointer, and one-letter commands read from standard input — the way a
> professional tool would: exact command syntax, cursor rules with no dead ends, precise
> diagnostics that never lose the session, a file written only on request, and byte-identical
> behavior on Linux, macOS, and Windows.

## Purpose

Project 44 is adapted from §10.3 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a line editor that loads a file into a linked list of lines, keeps a pointer to the current
line, and obeys the commands `i` (insert), `d` (delete), `t` (type), `m` (move), `f` (find),
`s` (substitute), and `q` (quit and write). The textbook version prompts for the file name,
trusts every command it reads, and says nothing about the bytes of the file. This project keeps
the buffer design and the command language and turns the program into a well-behaved
command-line tool that can be driven from the keyboard or from a script. The engineering focus
is linked-list surgery — splicing lines in after a cursor and unlinking runs of lines without
ever leaving the sentinel or the cursor dangling — and a command interpreter whose every input,
valid or not, has exactly one specified outcome.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| A buffer of lines headed by the `[BOF]` sentinel, with a current line | Undo, marks, line addresses, several buffers |
| Commands `i`, `d [N]`, `t .`/`b`/`e`/`N`, `m N`, `f 'PAT'`, `s 'OLD' 'NEW'`, `q` | Regular expressions, global substitution, shell escapes |
| Insert mode ended by a line holding a single `.` | Inserting a line that is exactly `.` |
| Patterns and replacements between any punctuation delimiters | Escape sequences inside patterns |
| Commands from standard input; the file named by the one operand | Commands from the command line or a script file option |
| A missing file starts an empty buffer; `q` creates or replaces the file | Backup files, atomic replacement, file locking |
| Lines as raw bytes: CR, NUL, and invalid UTF-8 preserved; trailing Ctrl-Z ignored (CONV-37) | Character-set conversion, line-ending conversion |
| Command diagnostics with line numbers (CONV-34); the session continues | Interactive recovery prompts |
| Optional `*` prompt on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| `--help`, `--version`, CONV-13 usage errors, CONV-16 file errors | Configuration files, environment variables |

## Learning objectives

1. Represent a text buffer as a singly linked list with a sentinel head, and implement insertion
   after a cursor and deletion of a run of nodes after it in time proportional to the lines
   touched (FR-06, FR-07, NFR-05).
2. Maintain a cursor invariant — the current line is always the sentinel or a line in the
   buffer — through every command, including commands that would move past the end (FR-04,
   FR-08, FR-09).
3. Write a command interpreter: split a command line into a command word and arguments, parse
   counts with an exact integer grammar, and parse delimited strings with arbitrary delimiters
   (FR-05, FR-10).
4. Design error handling for an interactive session: report a bad command precisely, leave the
   buffer unchanged, carry on, and still let a script detect that something failed (FR-14,
   FR-15).
5. Preserve a file's bytes through a load/save round trip on every platform: binary I/O, CR
   bytes kept as data, a missing final line feed and a Ctrl-Z end-of-file mark handled by rule,
   never by accident (FR-02, FR-13, NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-16) |
| `specs/SRS.md` | System requirements (FR-01 … FR-20, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Files shared by both suites: the text `poem.txt` and the command scripts `cmd-*.txt` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-line-ed`, with unit tests — including the buffer and command-parser
   tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-line-ed into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

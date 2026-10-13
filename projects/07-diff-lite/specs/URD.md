# User Requirements Document (URD) — dp-diff

| Field | Value |
| :-- | :-- |
| Document ID | URD-07 |
| Project | `07-diff-lite` — Line-by-Line File Comparison |
| Product | `dp-diff` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-07), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-diff` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-07), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-diff` compares two text files line by line and reports how to turn the first into the
second. It speaks the two output dialects every developer already reads: the classic "normal"
format (`2c2`, `< old`, `> new`) and the unified format used by code review tools and patches
(`@@ -1,3 +1,3 @@`). Unlike traditional diff tools, its output is *fully determined*: two
correct implementations, on any operating system, print exactly the same bytes for the same
pair of files. That makes its output safe to store, compare, and test.

### 1.3 Scope
In scope: comparing two files (or one file and standard input) line by line; normal and unified
output; adjustable unified context; a brief "differ or not" mode; optional normalization of
Windows (CRLF) line endings; reporting a missing final newline; exit statuses that separate
"same", "different", and "trouble"; help and version information.
Out of scope: comparing directories, binary-file detection, ignoring whitespace or case,
side-by-side and context (`-c`) formats, colors, timestamps in headers, and applying patches.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Developer | Compares versions of source files or configuration by hand on Linux, macOS, or Windows | Readable, familiar output |
| SH-2 | Script author | Uses the tool in shell scripts, build steps, and CI jobs | Reliable exit statuses and reproducible output |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | One unambiguous, testable definition of "the" difference |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Byte-exact, deterministic behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a script author, I want the exit status to tell me whether two files are the same, so I can branch on it without parsing output. | M | SH-2 |
| UR-02 | As a developer, I want to see which lines were added, removed, or changed, in the classic diff "normal" format. | M | SH-1 |
| UR-03 | As a developer, I want a unified format with surrounding context lines, and I want to choose how many context lines are shown. | M | SH-1 |
| UR-04 | As a script author, I want a brief mode that only says whether the files differ. | S | SH-2 |
| UR-05 | As a script author, I want to compare a file with the output of another command, by reading one side from standard input. | S | SH-2 |
| UR-06 | As a developer working across Windows and Unix, I want to be able to ignore the difference between CRLF and LF line endings, so files that differ only in line endings compare as equal. | M | SH-1 |
| UR-07 | As a developer, I want to be told when a file does not end with a newline, because that difference is otherwise invisible. | M | SH-1 |
| UR-08 | As a grader, I want identical output bytes on Linux, macOS, and Windows and from every correct implementation, with nothing time- or machine-dependent in it. | M | SH-4 |
| UR-09 | As a script author, I want problems such as a missing file or a wrong command line to be reported clearly and with an exit status different from "files differ". | M | SH-2 |
| UR-10 | As a developer, I want a built-in help screen and a version query. | M | SH-1 |
| UR-11 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-3 |
| UR-12 | As a learner, I want the specification to say exactly which of the many possible correct difference listings is expected, so my implementation can be checked byte for byte. | M | SH-3 |
| UR-13 | As a developer, I want comparisons of ordinary source files (thousands of lines) to finish in about a second. | S | SH-1 |
| UR-14 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-4 |

## 4. Usage scenarios

### 4.1 Did anything change?
A CI job runs `dp-diff expected.txt actual.txt`. When the files match, nothing is printed and
the exit status is 0. When they differ, the differences are printed and the status is 1. If
`actual.txt` was never produced, a one-line error is printed and the status is 2, so the job can
tell a failed comparison from a broken build. (UR-01, UR-02, UR-09)

### 4.2 Reviewing a change
A developer runs `dp-diff -u config.old config.new` and sees a unified listing with three lines
of context around each change. Wanting a tighter view, they run `dp-diff -U 1 ...`, and the
listing splits into smaller hunks. (UR-03)

### 4.3 Windows line endings
A file saved on Windows (CRLF) is compared with its Unix copy (LF). Plain `dp-diff` reports every
line as changed. With `--strip-trailing-cr` the files compare as equal and the exit status is 0.
(UR-06)

### 4.4 The invisible newline
A developer's editor removed the final newline from a file. `dp-diff` shows the last line as
changed and adds the marker `\ No newline at end of file`. (UR-07)

### 4.5 Comparing against a command's output
A script runs `generate-report | dp-diff -u - golden.txt` to check a program's output against a
stored copy. The header names standard input as `-`. (UR-05)

### 4.6 Just tell me yes or no
`dp-diff -q a.txt b.txt` prints `Files a.txt and b.txt differ` or nothing. (UR-04)

### 4.7 Two implementations, one answer
Two learners implement `dp-diff` in different languages, using different algorithms. For a file
with many repeated lines, where several equally short listings exist, both print the same one,
because the specification defines exactly which listing is canonical. (UR-08, UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale, terminal settings, or time zone. |
| UC-5 | Must not modify either input file. |

## 6. User acceptance criteria

The users will accept `dp-diff` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Line | A sequence of bytes ending in a line feed, or the final bytes of a file that does not end in one |
| Normal format | The classic diff output: commands such as `3d2`, followed by `< ` and `> ` lines |
| Unified format | Output with `---` / `+++` headers and `@@` hunks that mix context, removed (`-`), and added (`+`) lines |
| Hunk | One block of unified output: a header plus nearby changes and their context |
| Context | Unchanged lines shown around a change in unified format |
| Edit script | The list of keep, delete, and insert steps that turns the first file into the second |
| CRLF / LF | Windows (`\r\n`) and Unix (`\n`) line endings |
| Exit status | The integer a process returns to its caller |

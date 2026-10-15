<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-grep](#user-requirements-document-urd--dp-grep)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Find a word in a file](#41-find-a-word-in-a-file)
    - [4.2 Case-insensitive search with line numbers](#42-case-insensitive-search-with-line-numbers)
    - [4.3 Searching a source tree](#43-searching-a-source-tree)
    - [4.4 A literal search](#44-a-literal-search)
    - [4.5 A script that branches on the result](#45-a-script-that-branches-on-the-result)
    - [4.6 An unsupported pattern](#46-an-unsupported-pattern)
    - [4.7 A missing file in a list](#47-a-missing-file-in-a-list)
    - [4.8 Filtering a pipeline](#48-filtering-a-pipeline)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-grep

| Field               | Value                                           |
| :------------------ | :---------------------------------------------- |
| Document ID         | URD-05                                          |
| Project             | `05-grep-lite` — Pattern Matching Search Engine |
| Product             | `dp-grep`                                       |
| Version             | 1.0.0                                           |
| Status              | Approved (pre-written by the curriculum)        |
| Successor documents | `SRS.md` (SRS-05), `user-manual.md`             |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-grep` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-05), which turns each need into precise,
testable system behavior.

### 1.2 Product vision

`dp-grep` finds the lines of text that match a pattern, in files, in whole directory trees, or
in a pipeline. It is a disciplined subset of the classic `grep` utility with one property that
real-world `grep` implementations do not share: **a given pattern means exactly the same thing
on every operating system and in every implementation**. Regular-expression dialects differ
between libraries and platforms in many small ways; `dp-grep` defines a small, portable pattern
language, rejects everything outside it with a clear message, and prints file paths the same
way on Linux, macOS, and Windows.

### 1.3 Scope

In scope: searching files, standard input, and directory trees for lines that match one or more
regular expressions or literal strings; case-insensitive, inverted, whole-line, and whole-word
matching; line numbers, counts, file lists, and a silent mode for scripts; precise error
reporting and exit statuses.
Out of scope: printing only the matched part of a line, colored output, context lines around a
match, reading patterns from a file, binary-file detection, compressed files, file name
filters (include/exclude globs), following symbolic links inside directory trees, and
locale-dependent (non-ASCII) case folding.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                         | Primary interest                                                      |
| :--- | :----------------- | :------------------------------------------------------------------ | :-------------------------------------------------------------------- |
| SH-1 | Terminal user      | Searches files and source trees by hand on Linux, macOS, or Windows | Fast, readable results; helpful errors                                |
| SH-2 | Script author      | Uses the tool in shell scripts, build steps, and CI jobs            | Predictable output bytes and meaningful exit statuses                 |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice        | A complete, unambiguous specification, including the pattern language |
| SH-4 | Grader / CI        | Runs automated acceptance tests on three operating systems          | Deterministic, byte-exact behavior                                    |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                                              | Priority | Source     |
| :---- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a terminal user, I want to print every line of one or more files that matches a pattern, so I can find text quickly.                                                                                                                       | M        | SH-1       |
| UR-02 | As a script author, I want regular expressions (alternation, repetition, character sets, anchors) that match exactly the same lines on every platform and in every implementation, so a pattern I test once works everywhere.                 | M        | SH-2, SH-4 |
| UR-03 | As a terminal user, I want to search for a literal string that contains characters such as `.` or `*` without escaping them.                                                                                                                  | M        | SH-1       |
| UR-04 | As a terminal user, I want to ignore the difference between upper- and lower-case letters.                                                                                                                                                    | M        | SH-1       |
| UR-05 | As a terminal user, I want to print the lines that do _not_ match, so I can filter text out.                                                                                                                                                  | M        | SH-1       |
| UR-06 | As a terminal user, I want to see the line number of each matching line, so I can open the file at the right place.                                                                                                                           | M        | SH-1       |
| UR-07 | As a script author, I want to count matching lines per file instead of printing them.                                                                                                                                                         | S        | SH-2       |
| UR-08 | As a terminal user, I want to list only the names of the files that contain a match.                                                                                                                                                          | S        | SH-1       |
| UR-09 | As a script author, I want a silent mode that only reports, through the exit status, whether anything matched, and that stops as soon as it knows.                                                                                            | S        | SH-2       |
| UR-10 | As a terminal user, I want to search a whole directory tree in one command, with results in a stable, predictable order.                                                                                                                      | M        | SH-1, SH-4 |
| UR-11 | As a terminal user, I want to require that a pattern match a whole line or a whole word, so that `cat` does not also find `concatenate`.                                                                                                      | S        | SH-1       |
| UR-12 | As a terminal user, I want to give several patterns at once and see lines that match any of them.                                                                                                                                             | S        | SH-1       |
| UR-13 | As a script author, I want the tool to read standard input when I give no file, so it works in pipelines.                                                                                                                                     | M        | SH-2       |
| UR-14 | As a script author, I want distinct exit statuses for "found", "not found", and "something went wrong", so my scripts can branch on them.                                                                                                     | M        | SH-2       |
| UR-15 | As a terminal user, I want a pattern that is malformed, or that uses a feature the tool does not support (such as backreferences), to be rejected with a message that says what is wrong, rather than silently matching something unexpected. | M        | SH-1, SH-2 |
| UR-16 | As a terminal user, I want a missing or unreadable file to be reported without stopping the rest of the search, and I want to be able to silence those reports.                                                                               | M        | SH-1, SH-2 |
| UR-17 | As a grader, I want identical output bytes on Linux, macOS, and Windows, including line endings and the paths printed during directory searches.                                                                                              | M        | SH-4       |
| UR-18 | As a terminal user, I want to control whether each output line is prefixed by its file name.                                                                                                                                                  | S        | SH-1       |
| UR-19 | As a terminal user, I want built-in help and version information.                                                                                                                                                                             | M        | SH-1, SH-2 |
| UR-20 | As a terminal user, I want to search large files quickly and without the tool's memory use growing with the file size.                                                                                                                        | S        | SH-1       |
| UR-21 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                                                                          | M        | SH-3       |
| UR-22 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language.                                                                                                                      | M        | SH-4       |

## 4. Usage scenarios

### 4.1 Find a word in a file

A user runs `dp-grep fox poem.txt` and sees every line of `poem.txt` that contains `fox`,
exactly as it appears in the file. The exit status is 0. (UR-01, UR-14)

### 4.2 Case-insensitive search with line numbers

A user runs `dp-grep -i -n the poem.txt` and sees lines containing `The`, `the`, or `THE`, each
prefixed with its line number, for example `3:THE END is not near`. (UR-04, UR-06)

### 4.3 Searching a source tree

A user runs `dp-grep -r TODO src` on Windows and on Linux. Both print the same lines in the same
order, with paths such as `src/lib/util.c:// TODO tidy`, using `/` as the separator on both
systems. (UR-10, UR-17)

### 4.4 A literal search

A user wants lines containing `a.b*`. With `dp-grep -F 'a.b*' notes.txt`, the dot and the star
are ordinary characters, so `axbbb` is not matched. (UR-03)

### 4.5 A script that branches on the result

A CI job runs `dp-grep -q 'FAILED' report.txt`. Exit status 0 means a failure was reported,
1 means none was, and 2 means the report could not be read or the pattern was wrong. (UR-09,
UR-14)

### 4.6 An unsupported pattern

A user used to another `grep` types `dp-grep '(a)\1' poem.txt`. Instead of guessing, the tool
prints `dp-grep: invalid pattern '(a)\1': unsupported escape \1` and exits with status 2.
(UR-15, UR-02)

### 4.7 A missing file in a list

A user runs `dp-grep -l fox poem.txt missing.txt words.txt`. The tool lists `poem.txt`, reports
that `missing.txt` does not exist, still searches `words.txt`, and exits with status 2 because
an error occurred. (UR-08, UR-16)

### 4.8 Filtering a pipeline

A user pipes a log into `dp-grep -v DEBUG` to drop the debug lines. (UR-05, UR-13)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must never modify, create, or delete files.                                                                    |

## 6. User acceptance criteria

The users will accept `dp-grep` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.
4. Every pattern the user manual describes as valid is accepted, and every construct it
   describes as unsupported is rejected with the documented message.

## 7. Glossary

| Term               | Meaning                                                                                          |
| :----------------- | :----------------------------------------------------------------------------------------------- |
| Pattern            | The text that describes which lines to find: a regular expression, or a literal string with `-F` |
| Regular expression | A pattern language in which characters such as `.`, `*`, and `\|` have special meanings          |
| Selected line      | A line that is output (or counted): a matching line, or with `-v` a non-matching line            |
| Recursive search   | Searching every file inside a directory and all of its subdirectories                            |
| Exit status        | The integer a process returns to its caller                                                      |
| Backreference      | A construct such as `\1` that matches the same text as an earlier group; not supported           |

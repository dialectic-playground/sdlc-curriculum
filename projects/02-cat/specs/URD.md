<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-cat](#user-requirements-document-urd--dp-cat)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Joining files](#41-joining-files)
    - [4.2 In a pipeline](#42-in-a-pipeline)
    - [4.3 Numbered listing](#43-numbered-listing)
    - [4.4 Tidying blank lines](#44-tidying-blank-lines)
    - [4.5 The mysterious Windows file](#45-the-mysterious-windows-file)
    - [4.6 Binary garbage](#46-binary-garbage)
    - [4.7 A missing file in the middle](#47-a-missing-file-in-the-middle)
    - [4.8 A mistake](#48-a-mistake)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-cat

| Field               | Value                                    |
| :------------------ | :--------------------------------------- |
| Document ID         | URD-02                                   |
| Project             | `02-cat` — Concatenate & Number Files    |
| Product             | `dp-cat`                                 |
| Version             | 1.0.0                                    |
| Status              | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-02), `user-manual.md`      |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-cat` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-02), which turns each need into precise,
testable system behavior.

### 1.2 Product vision

`dp-cat` joins files together and writes them to standard output, exactly as they are, so that
they can be viewed, combined into one file, or fed into the next command of a pipeline. On
request it numbers the lines, collapses runs of blank lines, and makes invisible bytes visible:
control characters, tabs, line ends, and the carriage returns that Windows files carry. It is
the curriculum's first tool that reads files, and it teaches the discipline that every later
file-reading tool needs: treat data as bytes, never as text that may be "fixed up"; handle every
file, even when some of them fail; release each file as soon as it has been read; and use a
fixed amount of memory, whatever the size of the input.

### 1.3 Scope

In scope: concatenating any number of files and standard input in the order given, line
numbering (all lines or non-blank lines only), squeezing repeated blank lines, showing
non-printing bytes, tabs, and line ends, help and version information, and clear diagnostics for
files that cannot be read.
Out of scope: changing the content of the data (line-ending conversion, character-set
conversion), reading directories recursively, following URLs, paging output on a terminal,
colors, and configuration files.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                     | Primary interest                                           |
| :--- | :----------------- | :-------------------------------------------------------------- | :--------------------------------------------------------- |
| SH-1 | Terminal user      | Inspects and combines files by hand on Linux, macOS, or Windows | Faithful output, visible "invisible" bytes, helpful errors |
| SH-2 | Script author      | Uses the tool in pipelines, build scripts, and CI jobs          | Exact bytes, predictable exit statuses, streaming behavior |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice    | A complete, unambiguous specification                      |
| SH-4 | Grader / CI        | Runs automated acceptance tests on three operating systems      | Deterministic, byte-exact behavior                         |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                                                                              | Priority | Source |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :----- |
| UR-01 | As a terminal user, I want to name several files and see their contents one after another, in the order I named them, so I can read or combine them.                                                                                                                          | M        | SH-1   |
| UR-02 | As a script author, I want the tool to read standard input when I name no files, or where I write `-` among the files, so it works in pipelines.                                                                                                                              | M        | SH-2   |
| UR-03 | As a script author, I want the output to be an exact byte-for-byte copy of the input when I ask for no formatting, including binary files and Windows (CRLF) line endings, so that `dp-cat a b > c` really joins `a` and `b`.                                                 | M        | SH-2   |
| UR-04 | As a terminal user, I want to number the output lines, either all of them or only the non-blank ones, with numbering that continues from one file to the next, so I can refer to lines by number.                                                                             | M        | SH-1   |
| UR-05 | As a terminal user, I want to collapse runs of blank lines into a single blank line, so sparse files are easier to read.                                                                                                                                                      | S        | SH-1   |
| UR-06 | As a terminal user, I want to see control characters, high (non-ASCII) bytes, tabs, carriage returns, and line ends in a visible notation, so I can diagnose files that "look right" but are not.                                                                             | M        | SH-1   |
| UR-07 | As a terminal user, I want to recognize a file with Windows (CRLF) line endings at a glance, so I can tell why another tool misbehaves on it.                                                                                                                                 | M        | SH-1   |
| UR-08 | As a script author, I want a file that cannot be read (missing, a directory, or not permitted) to be reported by name, while the remaining files are still output, and I want a non-zero exit status afterwards, so one bad file neither hides the others nor goes unnoticed. | M        | SH-2   |
| UR-09 | As a script author, I want invalid usage to be rejected with a clear message and a distinct exit status before any output is produced, so my scripts can detect mistakes.                                                                                                     | M        | SH-2   |
| UR-10 | As a script author, I want the tool to process very large files and endless streams with modest, constant memory, and to pass data through as it arrives, so it works on logs and pipes of any size.                                                                          | M        | SH-2   |
| UR-11 | As a terminal user, I want a built-in help screen that lists every option, and a way to query the version.                                                                                                                                                                    | M        | SH-1   |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so a single set of expected outputs verifies every platform.                                                                                                                                         | M        | SH-4   |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions and the established behavior of the classic `cat` command, so what I learn carries over to other projects and to real systems.                                                                | M        | SH-3   |
| UR-14 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language.                                                                                                                                                      | M        | SH-4   |

## 4. Usage scenarios

### 4.1 Joining files

A user runs `dp-cat part1.txt part2.txt > whole.txt`. The file `whole.txt` contains exactly the
bytes of `part1.txt` followed by exactly the bytes of `part2.txt`. The exit status is 0.
(UR-01, UR-03)

### 4.2 In a pipeline

A script runs `some-command | dp-cat header.txt - footer.txt`. The output is the header, then
everything `some-command` printed, then the footer. Data from the pipe appears as soon as it
arrives. (UR-02, UR-10)

### 4.3 Numbered listing

A user runs `dp-cat -n notes.txt tasks.txt` and gets every line prefixed with its number, the
numbers continuing across both files. With `-b` instead, blank lines are left unnumbered.
(UR-04)

### 4.4 Tidying blank lines

A user runs `dp-cat -s draft.txt` on a file with runs of blank lines and sees each run collapsed
to one blank line. (UR-05)

### 4.5 The mysterious Windows file

A shell script fails on a configuration file that came from a Windows machine. The user runs
`dp-cat -A config.ini` and sees every line end in `^M$` instead of `$`: the file has CRLF line
endings. Without options, `dp-cat config.ini` prints the file unchanged, CRs included.
(UR-06, UR-07, UR-03)

### 4.6 Binary garbage

A user runs `dp-cat -v data.bin` and sees control bytes as `^A`, `^[`, and so on, and high bytes
as `M-` sequences, instead of corrupting the terminal. (UR-06)

### 4.7 A missing file in the middle

A user runs `dp-cat a.txt missing.txt b.txt`. The output contains `a.txt` and `b.txt`; standard
error says that `missing.txt` does not exist; the exit status is 1. (UR-08)

### 4.8 A mistake

A user types `dp-cat --numbr file.txt`. The tool prints a one-line explanation and a pointer to
`--help`, reads nothing, writes nothing to standard output, and exits with a non-zero status
different from the one used for unreadable files. (UR-09)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must handle inputs larger than the available memory.                                                           |

## 6. User acceptance criteria

The users will accept `dp-cat` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.
4. A multi-gigabyte file is copied with memory use that does not grow with the file size.

## 7. Glossary

| Term              | Meaning                                                                             |
| :---------------- | :---------------------------------------------------------------------------------- |
| Operand           | A command-line argument that names an input: a file path, or `-` for standard input |
| Concatenate       | Write several inputs one after another as a single output                           |
| LF                | Line feed, byte `0x0A`; the only byte that ends a line                              |
| CR                | Carriage return, byte `0x0D`; ordinary data to this tool                            |
| CRLF              | The pair CR LF, which ends lines in files written by many Windows programs          |
| Blank line        | A line with no bytes before its LF (a line holding only a CR is _not_ blank)        |
| Non-printing byte | A control byte, the DEL byte, or a byte of value 128 or more                        |
| Exit status       | The integer a process returns to its caller; 0 means success                        |

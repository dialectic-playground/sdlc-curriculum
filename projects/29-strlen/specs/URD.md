<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-strlen](#user-requirements-document-urd--dp-strlen)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Quick checks](#41-quick-checks)
    - [4.2 Characters and bytes](#42-characters-and-bytes)
    - [4.3 Line lengths of a file](#43-line-lengths-of-a-file)
    - [4.4 Damaged text](#44-damaged-text)
    - [4.5 A missing file](#45-a-missing-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-strlen

| Field               | Value                                             |
| :------------------ | :------------------------------------------------ |
| Document ID         | URD-29                                            |
| Project             | `29-strlen` — String Length from First Principles |
| Product             | `dp-strlen`                                       |
| Version             | 1.0.0                                             |
| Status              | Approved (pre-written by the curriculum)          |
| Successor documents | `SRS.md` (SRS-29), `user-manual.md`               |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-strlen` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-29), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-strlen` answers one question precisely: how long is this text? It measures the strings
typed on its command line, or every line of a file or pipe, and prints one number per string.
Text in any language written in UTF-8 is measured in characters, so `Zoë` is three long on
every computer; when storage matters, the same text can be measured in bytes. The answers never
depend on the locale, the console, or the line endings of the file.

### 1.3 Scope

In scope: the length of each command-line string; the length of each line of standard input or
of a named file; character or byte counting; files written on Windows or MS-DOS; reporting
unreadable files; help and version information.
Out of scope: display widths, grapheme clusters, totals or other statistics, several files in
one run, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                    | Primary interest                              |
| :--- | :----------------- | :----------------------------------------------------------------------------- | :-------------------------------------------- |
| SH-1 | Terminal user      | Checks the length of a name, a password, or a line on Linux, macOS, or Windows | A quick, correct number                       |
| SH-2 | Script author      | Validates field lengths and line lengths in scripts and CI jobs                | Predictable output bytes and exit statuses    |
| SH-3 | International user | Works with accented and non-Latin text                                         | Lengths that count letters, not storage bytes |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                   | A complete, unambiguous specification         |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                     | Deterministic, byte-exact behavior            |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                       | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a terminal user, I want to give one or more strings on the command line and see the length of each, in order, one per line.                                                         | M        | SH-1       |
| UR-02 | As a script author, I want the length of every line of a file or pipe, in order, one per line, so I can check line lengths.                                                            | M        | SH-2       |
| UR-03 | As an international user, I want lengths counted in characters, so accented and non-Latin text is measured as it reads.                                                                | M        | SH-3       |
| UR-04 | As a script author, I want to count bytes instead when a storage limit is in bytes.                                                                                                    | M        | SH-2       |
| UR-05 | As a script author, I want text that is not valid UTF-8 measured by a fixed, documented rule, never rejected and never measured differently on another computer.                       | M        | SH-2       |
| UR-06 | As a script author, I want files with Windows (CRLF) line endings, a missing final line break, or a Ctrl-Z end-of-file mark to give the same line lengths as a clean file.             | S        | SH-2       |
| UR-07 | As a script author, I want an empty string, an empty line, and a line containing a NUL byte measured correctly.                                                                        | M        | SH-2       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                 | M        | SH-2       |
| UR-09 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                 | M        | SH-1, SH-2 |
| UR-10 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                     | M        | SH-2       |
| UR-11 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                       | M        | SH-5       |
| UR-12 | As a learner, I want the tool to follow the curriculum's common CLI conventions, and to practise computing a length by scanning, so what I learn carries over.                         | M        | SH-4       |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to measure large inputs quickly in little memory. | M        | SH-5       |

## 4. Usage scenarios

### 4.1 Quick checks

A user runs `dp-strlen '' a 'hello world' 'ANSI C'` and sees `0`, `1`, `11`, and `6` on four
lines. The exit status is 0. (UR-01, UR-07)

### 4.2 Characters and bytes

`dp-strlen Zoë 日本語 🙂` prints `3`, `3`, and `1`; `dp-strlen -b Zoë 日本語 🙂` prints `4`,
`9`, and `4`. (UR-03, UR-04)

### 4.3 Line lengths of a file

A script runs `dp-strlen -f notes.txt` and receives one number per line, `0` for each empty
line. The same file saved with Windows line endings gives the same numbers. (UR-02, UR-06)

### 4.4 Damaged text

A log file contains bytes that are not valid UTF-8. `dp-strlen` still prints a length for every
line, counting each invalid byte as one character, and exits with status 0. (UR-05)

### 4.5 A missing file

`dp-strlen -f missing.txt` reports `missing.txt: No such file or directory` and exits with
status 1. (UR-08)

### 4.6 Discovery and mistakes

A user runs `dp-strlen --help` to see the options; `dp-strlen -f notes.txt extra` is rejected,
because strings and a file cannot be measured in the same run. (UR-09, UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must measure inputs and lines of any size without holding them in memory.                                      |

## 6. User acceptance criteria

The users will accept `dp-strlen` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term        | Meaning                                                                                       |
| :---------- | :-------------------------------------------------------------------------------------------- |
| String      | A command-line argument, or one line of the input                                             |
| Line        | The text before a line feed, or the text after the last line feed if there is any             |
| Character   | A letter or symbol as stored in UTF-8; a byte that is not valid UTF-8 counts as one character |
| Length      | The number of characters (or bytes, with `-b`) in a string                                    |
| Exit status | The integer a process returns to its caller; 0 means success                                  |

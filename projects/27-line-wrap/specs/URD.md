<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-wrap](#user-requirements-document-urd--dp-wrap)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The textbook example](#41-the-textbook-example)
    - [4.2 Reflowing a message](#42-reflowing-a-message)
    - [4.3 Accented text](#43-accented-text)
    - [4.4 A word that cannot fit](#44-a-word-that-cannot-fit)
    - [4.5 A wrong first line](#45-a-wrong-first-line)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-wrap

| Field               | Value                                                |
| :------------------ | :--------------------------------------------------- |
| Document ID         | URD-27                                               |
| Project             | `27-line-wrap` — Greedy Word-Wrapping Text Formatter |
| Product             | `dp-wrap`                                            |
| Version             | 1.0.0                                                |
| Status              | Approved (pre-written by the curriculum)             |
| Successor documents | `SRS.md` (SRS-27), `user-manual.md`                  |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-wrap` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-27), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-wrap` reflows text: it takes words from any source, ignores how they were laid out, and
writes them back in lines that never exceed a chosen length, with exactly one space between
words. Text in any language written in UTF-8 is measured in characters, so `café` is four long
wherever the tool runs. A word that is simply too long for the chosen length is never lost or
split: it is reported, and written on a line of its own.

### 1.3 Scope

In scope: reading words from the keyboard, a pipe, or a file; taking the line length from the
data or from the command line; measuring words in characters or bytes; reporting over-long
words, a bad line length, and unreadable files; reading files written on Windows or MS-DOS;
help and version information.
Out of scope: hyphenation, justification, indentation, keeping paragraphs apart, display widths
of wide or combining characters, several input files, configuration files, and environment
variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                             | Primary interest                              |
| :--- | :----------------- | :---------------------------------------------------------------------- | :-------------------------------------------- |
| SH-1 | Writer             | Reflows notes and messages to a fixed width on Linux, macOS, or Windows | Tidy lines; words never broken or lost        |
| SH-2 | Script author      | Formats generated text in pipelines and batch jobs                      | Predictable output bytes and exit statuses    |
| SH-3 | International user | Writes in languages with accented or non-Latin letters                  | Lengths that count letters, not storage bytes |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice            | A complete, unambiguous specification         |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems              | Deterministic, byte-exact behavior            |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                      | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- | :--------- |
| UR-01 | As a writer, I want words written in their original order with exactly one space between neighbours on a line, however they were spaced in the input.                                 | M        | SH-1       |
| UR-02 | As a writer, I want each line filled with as many words as fit, so that no line exceeds the line length and a line that reaches it exactly is not lengthened.                         | M        | SH-1       |
| UR-03 | As a script author, I want to give the line length as the first item of the data, as the original program expects, or on the command line, so I can reflow existing text unchanged.   | M        | SH-2       |
| UR-04 | As an international user, I want word lengths counted in characters, so accented and non-Latin words are measured as they read.                                                       | M        | SH-3       |
| UR-05 | As a script author, I want to count lengths in bytes instead when the output goes to a byte-limited field.                                                                            | S        | SH-2       |
| UR-06 | As a writer, I want a word longer than the line length to be reported, and still written in full, so no text is lost.                                                                 | M        | SH-1       |
| UR-07 | As a script author, I want a missing or invalid line length reported with its position and a non-zero exit status.                                                                    | M        | SH-2       |
| UR-08 | As a script author, I want to pipe text into the tool or name a file, and a missing or unreadable file reported clearly.                                                              | M        | SH-2       |
| UR-09 | As a writer, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                    | S        | SH-1       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                    | M        | SH-2       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                      | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                  | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to reflow large inputs quickly in little memory. | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The textbook example

A file holds `20` followed by `The quick brown fox jumps over the lazy dog`. `dp-wrap` writes
`The quick brown fox`, `jumps over the lazy`, and `dog` on three lines and exits with
status 0. (UR-01, UR-02, UR-03)

### 4.2 Reflowing a message

A writer runs `dp-wrap -w 72 notes.txt > wrapped.txt`. Every line of the result is at most 72
characters long, and blank lines and runs of spaces in the original have disappeared.
(UR-01, UR-02, UR-03)

### 4.3 Accented text

`dp-wrap -w 12` places `crème brûlée` on one line: it is twelve characters long, although it
takes fifteen bytes. With `-b` the two words go on separate lines. (UR-04, UR-05)

### 4.4 A word that cannot fit

With a line length of 10, the word `supercalifragilistic,` is written on a line of its own,
the tool reports `long.txt:2: word length exceeds line length 'supercalifragilistic,'`, the
rest of the text is wrapped as usual, and the exit status is 1. (UR-06)

### 4.5 A wrong first line

A file that should start with the line length starts with `twenty`. The tool reports
`badwidth.txt:1: invalid integer 'twenty'`, writes nothing, and exits with status 1. (UR-07)

### 4.6 Discovery and mistakes

A user runs `dp-wrap --help` to see the options; `dp-wrap -w 0 notes.txt` is rejected because
a line length must be at least 1. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must reflow inputs of any size without holding the whole input in memory.                                      |

## 6. User acceptance criteria

The users will accept `dp-wrap` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term           | Meaning                                                                                       |
| :------------- | :-------------------------------------------------------------------------------------------- |
| Word           | A run of characters containing no space, tab, line break, vertical tab, or form feed          |
| Line length    | The largest number of characters (or bytes, with `-b`) that a line may hold                   |
| Greedy         | Each word goes on the current line if it fits there; otherwise it starts a new line           |
| Over-long word | A word longer than the line length; it can never fit, and is written on a line of its own     |
| Character      | A letter or symbol as stored in UTF-8; a byte that is not valid UTF-8 counts as one character |
| Exit status    | The integer a process returns to its caller; 0 means success                                  |

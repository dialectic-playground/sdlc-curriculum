<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-page](#user-requirements-document-urd--dp-page)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Printing a listing](#41-printing-a-listing)
    - [4.2 An exactly full last page](#42-an-exactly-full-last-page)
    - [4.3 A Windows file without a final newline](#43-a-windows-file-without-a-final-newline)
    - [4.4 Several files and smaller paper](#44-several-files-and-smaller-paper)
    - [4.5 A missing file](#45-a-missing-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-page

| Field               | Value                                      |
| :------------------ | :----------------------------------------- |
| Document ID         | URD-36                                     |
| Project             | `36-page` — Stream Text Pagination Utility |
| Product             | `dp-page`                                  |
| Version             | 1.0.0                                      |
| Status              | Approved (pre-written by the curriculum)   |
| Successor documents | `SRS.md` (SRS-36), `user-manual.md`        |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-page` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-36), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-page` prepares plain text for a printer. It splits the text into pages of 52 lines, puts a
numbered header at the top of each page, and ends each page with a form feed, so that every
page starts on a fresh sheet. The text itself is never altered: every byte of every line is
copied exactly as it was read, and no blank page is ever produced.

### 1.3 Scope

In scope: reading text from the keyboard, a pipe, or one or more files; splitting it into
numbered pages of a fixed number of lines (52 unless the user chooses another number);
copying the text unchanged; reporting files that cannot be read; help and version
information.
Out of scope: page footers, margins, multiple columns, line numbering, wrapping or truncating
long lines, file names or dates in headers, converting line endings, sending output to a
printer, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                           | Primary interest                                              |
| :--- | :----------------- | :-------------------------------------------------------------------- | :------------------------------------------------------------ |
| SH-1 | Office user        | Prints reports and listings on Linux, macOS, or Windows               | Correctly numbered pages that each start on a new sheet       |
| SH-2 | Script author      | Pipes generated text through the tool in print jobs and batch scripts | Predictable output bytes and exit statuses                    |
| SH-3 | Archivist          | Keeps paginated copies of data files                                  | The original text recoverable exactly from the paginated copy |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice          | A complete, unambiguous specification                         |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems            | Deterministic, byte-exact behavior                            |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                           | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As an office user, I want text split into pages of 52 lines, so that each page fits a printed sheet.                                                                                                                       | M        | SH-1       |
| UR-02 | As an office user, I want each page to start with a header giving its page number, followed by a blank line.                                                                                                               | M        | SH-1       |
| UR-03 | As an office user, I want each page to end with a form feed, so the printer starts the next page on a new sheet.                                                                                                           | M        | SH-1       |
| UR-04 | As an office user, I want no page to be printed without text on it: not for an empty input, and not after a last page that is exactly full.                                                                                | M        | SH-1       |
| UR-05 | As an archivist, I want every line copied exactly, including blank lines, Windows line endings, control characters, and a last line without a newline, so that the original text can be recovered from the paginated copy. | M        | SH-3       |
| UR-06 | As a script author, I want to pipe text into the tool or name one or more files, which are paginated as one continuous text.                                                                                               | M        | SH-2       |
| UR-07 | As an office user, I want to choose a different number of lines per page for other paper sizes.                                                                                                                            | S        | SH-1       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status, while the other files are still paginated.                                                                          | M        | SH-2       |
| UR-09 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                                     | M        | SH-1, SH-2 |
| UR-10 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                         | M        | SH-2       |
| UR-11 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                                                           | M        | SH-5       |
| UR-12 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                                                       | M        | SH-4       |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to paginate large files quickly in little memory.                                     | M        | SH-5       |

## 4. Usage scenarios

### 4.1 Printing a listing

A user runs `dp-page report.txt > report.prn` on a 120-line report and sends the result to a
printer. It prints three sheets: `Page     1` and `Page     2` with 52 lines each and
`Page     3` with the last 16 lines. (UR-01, UR-02, UR-03)

### 4.2 An exactly full last page

A 104-line file produces exactly two pages; the printer does not eject a third, empty sheet.
An empty file produces no output at all. (UR-04)

### 4.3 A Windows file without a final newline

A file written on Windows has CRLF line endings and no newline after its last line. The pages
contain the CR bytes unchanged, the last line is followed directly by the form feed, and
removing the headers and form feeds gives back the original file exactly. (UR-05)

### 4.4 Several files and smaller paper

A script runs `dp-page -l 40 part1.txt part2.txt` and gets one continuously numbered sequence
of 40-line pages covering both files. (UR-06, UR-07)

### 4.5 A missing file

`dp-page missing.txt notes.txt` reports that `missing.txt` does not exist, still paginates
`notes.txt`, and exits with status 1. (UR-08)

### 4.6 Discovery and mistakes

A user runs `dp-page --help` to see the options; `dp-page -l 0` is rejected because a page
must hold at least one line. (UR-09, UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must handle inputs much larger than memory and lines of any length.                                            |

## 6. User acceptance criteria

The users will accept `dp-page` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term        | Meaning                                                                                              |
| :---------- | :--------------------------------------------------------------------------------------------------- |
| Line        | A sequence of bytes ending with a newline (LF), or the bytes after the last newline if there are any |
| Page        | A header, a blank line, up to 52 lines of text, and a form feed                                      |
| Header      | The line `Page     N` that opens a page, where N is the page number                                  |
| Form feed   | The control character `0x0C`, which tells a printer to eject the current sheet                       |
| Exit status | The integer a process returns to its caller; 0 means success                                         |

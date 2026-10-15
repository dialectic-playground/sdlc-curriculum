<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-head, dp-tail](#user-requirements-document-urd--dp-head-dp-tail)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Peeking at a file](#41-peeking-at-a-file)
    - [4.2 Precise extraction in a script](#42-precise-extraction-in-a-script)
    - [4.3 Several files at once](#43-several-files-at-once)
    - [4.4 Pipelines](#44-pipelines)
    - [4.5 Watching a log](#45-watching-a-log)
    - [4.6 A terminating follow in a test](#46-a-terminating-follow-in-a-test)
    - [4.7 A huge file](#47-a-huge-file)
    - [4.8 A mistake](#48-a-mistake)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-head, dp-tail

| Field               | Value                                    |
| :------------------ | :--------------------------------------- |
| Document ID         | URD-03                                   |
| Project             | `03-head-tail` — Stream Slicing Utility  |
| Products            | `dp-head`, `dp-tail`                     |
| Version             | 1.0.0                                    |
| Status              | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-03), `user-manual.md`      |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-head` and `dp-tail` need, in their own terms. It
is the starting point for the Software Requirements Specification (SRS-03), which turns each
need into precise, testable system behavior.

### 1.2 Product vision

`dp-head` and `dp-tail` cut a slice out of the beginning or the end of a file or stream: the
first or last lines, the first or last bytes, everything except the last part, or everything
from a given point onward. `dp-tail` can also keep watching files and print data as it is
appended, which is how people watch log files. Both tools must be safe to point at very large
files, such as a multi-gigabyte log, without slowing to a crawl or exhausting memory, and they
must produce the same bytes on Linux, macOS, and Windows.

### 1.3 Scope

In scope: printing the first or last N lines or bytes of one or more files or standard input;
printing all but the last N lines or bytes; printing everything from line or byte N onward;
file-name headers when several files are processed; follow mode for growing files, including a
bounded, deterministic variant for scripts and tests; help and version information; clear usage
and file errors.
Out of scope: following files by name across rotation or re-creation, inotify-style
notifications, process-ID watching, line delimiters other than LF (for example NUL), character
or word counts, regular-expression selection, and editing files in place.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                            | Primary interest                                         |
| :--- | :----------------- | :--------------------------------------------------------------------- | :------------------------------------------------------- |
| SH-1 | Terminal user      | Inspects the start or end of files by hand on Linux, macOS, or Windows | Quick, readable slices; helpful errors                   |
| SH-2 | Script author      | Uses the tools in pipelines, shell scripts, and CI jobs                | Predictable bytes, exit statuses, and resource use       |
| SH-3 | Operator           | Watches growing log files and inspects very large data files           | Follow mode; no memory blow-ups on huge files            |
| SH-4 | Learner (assignee) | Implements both tools in a language repository of their choice         | A complete, unambiguous specification                    |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems             | Deterministic, byte-exact behavior; tests that terminate |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                               | Priority | Source     |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a terminal user, I want to see the first 10 lines of a file by default, so I can glance at its beginning.                                                                                   | M        | SH-1       |
| UR-02 | As a terminal user, I want to see the last 10 lines of a file by default, so I can glance at its end.                                                                                          | M        | SH-1       |
| UR-03 | As a script author, I want to choose how many lines or how many bytes are printed, so I can extract exactly the part I need.                                                                   | M        | SH-2       |
| UR-04 | As a script author, I want to print everything except the last N lines or bytes, so I can strip trailers.                                                                                      | M        | SH-2       |
| UR-05 | As a script author, I want to print everything from line N or byte N onward, so I can skip headers.                                                                                            | M        | SH-2       |
| UR-06 | As a terminal user, I want large counts to be easy to type (for example `64K`), so I can slice by kilobytes or megabytes.                                                                      | C        | SH-1       |
| UR-07 | As a terminal user, I want each file's output labelled when I give several files, and I want to be able to force or suppress those labels.                                                     | M        | SH-1, SH-2 |
| UR-08 | As a script author, I want both tools to read standard input when I give no file, or when I give `-`, so they work in pipelines.                                                               | M        | SH-2       |
| UR-09 | As an operator, I want to keep watching a file and see new data as it is appended, so I can follow a log.                                                                                      | S        | SH-3       |
| UR-10 | As a grader, I want a way to make follow mode stop by itself after a fixed number of checks, so automated tests always terminate.                                                              | M        | SH-5       |
| UR-11 | As an operator, I want slicing the end of a multi-gigabyte file to be fast and to use a small, fixed amount of memory, whatever the file size.                                                 | M        | SH-3       |
| UR-12 | As a script author, I want the data copied exactly, byte for byte, including Windows CRLF line endings and a last line with no line feed.                                                      | M        | SH-2       |
| UR-13 | As a script author, I want a missing or unreadable file to be reported clearly without stopping the processing of the other files, and I want the exit status to tell me something went wrong. | M        | SH-2       |
| UR-14 | As a script author, I want invalid options and invalid counts to be rejected with a clear message and a distinct exit status before any output is produced.                                    | M        | SH-2       |
| UR-15 | As a terminal user, I want built-in help and version information for both tools.                                                                                                               | M        | SH-1       |
| UR-16 | As a grader, I want identical output bytes on Linux, macOS, and Windows, including line endings, so one set of expected outputs verifies every platform.                                       | M        | SH-5       |
| UR-17 | As a learner, I want both tools to follow the curriculum's common CLI conventions, so what I learn carries over to the other projects.                                                         | M        | SH-4       |
| UR-18 | As a grader, I want both tools to install and uninstall with standard commands, regardless of their implementation language.                                                                   | M        | SH-5       |

## 4. Usage scenarios

### 4.1 Peeking at a file

A user runs `dp-head notes.txt` and sees its first 10 lines, then `dp-tail notes.txt` and sees
its last 10. If the file has fewer than 10 lines, the whole file is printed. (UR-01, UR-02)

### 4.2 Precise extraction in a script

A script runs `dp-head -c 512 image.bin > header.bin` to capture a file header, and
`dp-tail -n +2 table.csv` to drop the column-title line. Another strips a two-line trailer with
`dp-head -n -2 report.txt`. (UR-03, UR-04, UR-05)

### 4.3 Several files at once

A user runs `dp-tail -n 3 app.log db.log`. Each file's last three lines appear under a header
such as `==> app.log <==`, with a blank line between the files. Adding `-q` removes the headers.
(UR-07)

### 4.4 Pipelines

A CI job runs `build-tool | dp-tail -n 50` to keep only the end of a long build log. (UR-08)

### 4.5 Watching a log

An operator runs `dp-tail -f server.log` and leaves it running. New lines appear as the server
writes them, until the operator interrupts the command. (UR-09)

### 4.6 A terminating follow in a test

A grader runs `dp-tail -f --max-polls 1 -s 0 server.log`. The tool prints the last 10 lines,
checks the file once more for new data, and exits with status 0. (UR-10)

### 4.7 A huge file

An operator runs `dp-tail -n 20 archive-40GB.log`. The answer appears almost instantly, because
the tool reads only the end of the file, and memory use stays small. (UR-11)

### 4.8 A mistake

A user types `dp-head -n ten notes.txt`. The tool prints a one-line explanation, points to
`--help`, and exits with status 2, printing nothing on standard output. If instead one of
several files is missing, that file is reported, the other files are still printed, and the
exit status is 1. (UR-13, UR-14)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as native executables or language-runtime launchers.   |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must remain usable on files larger than the computer's memory.                                                 |

## 6. User acceptance criteria

The users will accept `dp-head` and `dp-tail` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. Both help texts exactly match the ones published in the user manual.
4. A demonstration on a file of at least 4 GiB shows `dp-tail -n 10` completing quickly with
   memory use that does not grow with the file size.

## 7. Glossary

| Term          | Meaning                                                                                                            |
| :------------ | :----------------------------------------------------------------------------------------------------------------- |
| Line          | A run of bytes ending with a line feed, or the bytes after the last line feed when the input does not end with one |
| Header        | The label line `==> NAME <==` printed before a file's slice                                                        |
| Follow mode   | Continuing to watch files after the initial output and printing appended data                                      |
| Poll          | One check of the followed files for appended data                                                                  |
| Seekable file | A regular file whose read position can be moved, as opposed to a pipe or terminal                                  |
| Exit status   | The integer a process returns to its caller; 0 means success                                                       |

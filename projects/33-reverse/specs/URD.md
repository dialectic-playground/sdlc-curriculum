<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-reverse](#user-requirements-document-urd--dp-reverse)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the keyboard](#41-at-the-keyboard)
    - [4.2 A list of words](#42-a-list-of-words)
    - [4.3 Accented text](#43-accented-text)
    - [4.4 Whole lines](#44-whole-lines)
    - [4.5 Too long](#45-too-long)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-reverse

| Field               | Value                                                 |
| :------------------ | :---------------------------------------------------- |
| Document ID         | URD-33                                                |
| Project             | `33-reverse` — Two-Pointer In-Place Sequence Reversal |
| Product             | `dp-reverse`                                          |
| Version             | 1.0.0                                                 |
| Status              | Approved (pre-written by the curriculum)              |
| Successor documents | `SRS.md` (SRS-33), `user-manual.md`                   |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-reverse` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-33), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-reverse` writes short strings backwards: `Antigravity` becomes `ytivargitnA`. A user can
type words one after another and see each reversed at once; a script can pass a file of words
or lines and get every one reversed. Text in any language written in UTF-8 comes out as
readable text, with each letter intact, and the tool never misbehaves on a string that is too
long — it says so.

### 1.3 Scope

In scope: reading words, or whole lines, from the keyboard, a pipe, or a file; reversing each
one by characters or by bytes; optional prompts; reading files written on Windows or MS-DOS;
reporting strings over the 100-character limit and unreadable files; help and version
information.
Out of scope: strings longer than 100 characters, reversing a whole file, grapheme clusters,
writing files, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                  | Primary interest                                                         |
| :--- | :----------------- | :----------------------------------------------------------- | :----------------------------------------------------------------------- |
| SH-1 | Terminal user      | Types strings by hand on Linux, macOS, or Windows            | An immediate answer for each string; clear prompts; helpful errors       |
| SH-2 | Script author      | Reverses lists of words or lines in pipelines                | Predictable output bytes and exit statuses                               |
| SH-3 | International user | Works with accented and non-Latin text                       | Reversed text that is still valid, readable UTF-8                        |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification; practice with in-place algorithms |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems   | Deterministic, byte-exact behavior                                       |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                       | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a terminal user, I want to enter words one after another and see each one reversed, labelled as in the original program, until I signal the end of the input.                       | M        | SH-1       |
| UR-02 | As a script author, I want to reverse whole lines, spaces included, when I ask for it.                                                                                                 | S        | SH-2       |
| UR-03 | As an international user, I want each character kept intact when a string is reversed, so `Zoë` becomes `ëoZ`.                                                                         | M        | SH-3       |
| UR-04 | As a learner, I want to reverse bytes instead when I ask for it, to see why byte reversal breaks multibyte characters.                                                                 | C        | SH-4       |
| UR-05 | As a script author, I want a string longer than 100 characters reported with its position and a non-zero exit status, while the results already produced are kept.                     | M        | SH-2       |
| UR-06 | As a terminal user, I want the tool to ask for each string when I request it, without the prompts appearing in the output I save.                                                      | S        | SH-1       |
| UR-07 | As a script author, I want to pipe text into the tool or name a file, and a missing or unreadable file reported clearly.                                                               | M        | SH-2       |
| UR-08 | As a terminal user, I want to see each reversed string as soon as I have typed it.                                                                                                     | M        | SH-1       |
| UR-09 | As a script author, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                              | S        | SH-2       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                 | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                     | M        | SH-2       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                       | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, and to practise reversing a string in place, so what I learn carries over.                            | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large inputs quickly in little memory. | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the keyboard

A user runs `dp-reverse --prompt`, sees `Enter a string:` followed by a tab, types
`Antigravity` and Enter, and at once sees `Reversed string:` followed by a tab and
`ytivargitnA`, then the next prompt. After the last string the user presses Ctrl-D (Ctrl-Z then
Enter on Windows) and the tool exits with status 0. (UR-01, UR-06, UR-08)

### 4.2 A list of words

A script runs `dp-reverse words.txt > reversed.txt`. The file holds one line per word of the
input, in order, and nothing else; `ABCD` gives `DCBA`, `ABCDE` gives `EDCBA`, and `racecar`
gives `racecar`. (UR-01, UR-07)

### 4.3 Accented text

`Zoë` gives `ëoZ` and `日本語` gives `語本日`. With `-b` the bytes are reversed instead, and the
accented letters come out as invalid bytes. (UR-03, UR-04)

### 4.4 Whole lines

`dp-reverse -l` reverses `Hello, World!` to `!dlroW ,olleH`; an empty line gives an empty
result. (UR-02)

### 4.5 Too long

The second word of a file is 101 characters long. The tool prints the result for the first
word, reports `toolong.txt:2: string exceeds 100 characters`, and exits with status 1. (UR-05)

### 4.6 Discovery and mistakes

A user runs `dp-reverse --help` to see the options; `dp-reverse a.txt b.txt` is rejected,
because the tool reads one file. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must not wait for the end of the input before answering.                           |

## 6. User acceptance criteria

The users will accept `dp-reverse` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term         | Meaning                                                                                                       |
| :----------- | :------------------------------------------------------------------------------------------------------------ |
| String       | One word of the input (a run of characters without spaces, tabs, or line breaks), or one whole line with `-l` |
| Character    | A letter or symbol as stored in UTF-8; a byte that is not valid UTF-8 counts as one character                 |
| In place     | Reversed within the storage that holds the string, without a second copy                                      |
| Limit        | The largest string the tool accepts: 100 characters (100 bytes with `-b`)                                     |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard                    |
| Exit status  | The integer a process returns to its caller; 0 means success                                                  |

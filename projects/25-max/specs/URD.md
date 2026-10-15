<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-max](#user-requirements-document-urd--dp-max)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the keyboard](#41-at-the-keyboard)
    - [4.2 All negative](#42-all-negative)
    - [4.3 The extremes](#43-the-extremes)
    - [4.4 Too many, too few](#44-too-many-too-few)
    - [4.5 A typo](#45-a-typo)
    - [4.6 Code review](#46-code-review)
    - [4.7 Discovery and mistakes](#47-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-max

| Field               | Value                                                    |
| :------------------ | :------------------------------------------------------- |
| Document ID         | URD-25                                                   |
| Project             | `25-max` — Variadic Functions & Dynamic Arity Processing |
| Product             | `dp-max`                                                 |
| Version             | 1.0.0                                                    |
| Status              | Approved (pre-written by the curriculum)                 |
| Successor documents | `SRS.md` (SRS-25), `user-manual.md`                      |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-max` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-25), which turns each need into precise,
testable system behavior.

### 1.2 Product vision

`dp-max` answers one question: which of these few integers is the largest? A user types one to
four integers, or pipes them in, and gets `Maximum integer = …`. Behind that answer is a
reusable building block — a maximum function that takes as many arguments as it is given — that
the curriculum's maintainers want to see written cleanly in every language. The answer is exact
for every 64-bit integer, and a wrong number of values or a mistyped value is reported clearly
instead of producing a misleading result.

### 1.3 Scope

In scope: reading one to four integers from the keyboard, a pipe, or a file; printing the
largest; an optional prompt; reading data files written on Windows or MS-DOS; reporting a
missing, surplus, or invalid value and unreadable files; help and version information.
Out of scope: more than four values, real numbers, other statistics (see `dp-stats`, Project
15), values given on the command line, writing files, configuration files, and environment
variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                      | Primary interest                                                   |
| :--- | :----------------- | :--------------------------------------------------------------- | :----------------------------------------------------------------- |
| SH-1 | Interactive user   | Types a few integers at the keyboard on Linux, macOS, or Windows | A clear prompt and an immediate, correct answer                    |
| SH-2 | Script author      | Pipes integers through the tool in shell scripts                 | Predictable output bytes and exit statuses; exact results          |
| SH-3 | Code reviewer      | Reviews implementations in many languages                        | One reusable maximum function that accepts any number of arguments |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice     | A complete, unambiguous specification                              |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems       | Deterministic, byte-exact behavior                                 |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                               | Priority | Source     |
| :---- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As an interactive user, I want to enter one, two, three, or four integers and be told the largest.                                                                             | M        | SH-1       |
| UR-02 | As a script author, I want the answer to be exact for any integer from −9223372036854775808 to 9223372036854775807, on every platform, including when every value is negative. | M        | SH-2       |
| UR-03 | As a script author, I want to pipe the integers into the tool or name a file that holds them.                                                                                  | M        | SH-2       |
| UR-04 | As a script author, I want an input with no integers or with more than four reported as an error, not answered with a guess.                                                   | M        | SH-2       |
| UR-05 | As a script author, I want a value that is not an integer reported with its position and a non-zero exit status, and no answer printed.                                        | M        | SH-2       |
| UR-06 | As a code reviewer, I want the maximum computed by one function that accepts any number of arguments, so the same function serves two values or twenty.                        | M        | SH-3       |
| UR-07 | As an interactive user, I want to be told what to type when I ask for it, without the prompt appearing in the output I save.                                                   | S        | SH-1       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                         | M        | SH-2       |
| UR-09 | As an interactive user, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                             | S        | SH-1       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                         | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                             | M        | SH-2       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions.                                       | M        | SH-4, SH-5 |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language.                                               | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the keyboard

A user runs `dp-max --prompt`, sees `Enter one to four integers` and `generate EOF when done`,
types `15 42 8`, presses Enter and then Ctrl-D (Ctrl-Z then Enter on Windows), and sees
`Maximum integer = 42`. (UR-01, UR-07)

### 4.2 All negative

A script runs `printf -- '-10 -2 -50 -4\n' | dp-max` and receives `Maximum integer = -2`.
(UR-01, UR-02)

### 4.3 The extremes

An input of `-9223372036854775808` alone gives `Maximum integer = -9223372036854775808`, on a
platform whose `long` has 32 bits as well as on one where it has 64. (UR-02)

### 4.4 Too many, too few

A file holding five integers is rejected with `five.txt:2: too many values '5'`; an empty input
is rejected with `-:1: unexpected end of input`. Neither prints an answer. (UR-04)

### 4.5 A typo

A file contains `10 2O` (a letter O instead of a zero). The tool reports
`bad.txt:1: invalid integer '2O'` and exits with status 1. (UR-05)

### 4.6 Code review

A reviewer finds a single function, called once with all the values read, whose parameter list
accepts any number of integers; its unit tests call it with one value and with ten. (UR-06)

### 4.7 Discovery and mistakes

A user runs `dp-max --help` to see the options, and `dp-max a.txt b.txt` is rejected because
the tool reads one file. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-max` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.
4. A design review confirms the single variable-arity maximum function (UR-06).

## 7. Glossary

| Term                               | Meaning                                                                                    |
| :--------------------------------- | :----------------------------------------------------------------------------------------- |
| Integer                            | A whole number from −9223372036854775808 to 9223372036854775807 (64-bit signed)            |
| Maximum                            | The largest of the values; when several are equal and largest, that value                  |
| Variable-arity (variadic) function | A function that can be called with different numbers of arguments                          |
| End of input                       | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status                        | The integer a process returns to its caller; 0 means success                               |

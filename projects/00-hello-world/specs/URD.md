<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-hello](#user-requirements-document-urd--dp-hello)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 First run](#41-first-run)
    - [4.2 Personalized greeting](#42-personalized-greeting)
    - [4.3 Scripted repetition](#43-scripted-repetition)
    - [4.4 A mistake](#44-a-mistake)
    - [4.5 Discovery](#45-discovery)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-hello

| Field               | Value                                            |
| :------------------ | :----------------------------------------------- |
| Document ID         | URD-00                                           |
| Project             | `00-hello-world` — Standard Terminal Hello World |
| Product             | `dp-hello`                                       |
| Version             | 1.0.0                                            |
| Status              | Approved (pre-written by the curriculum)         |
| Successor documents | `SRS.md` (SRS-00), `user-manual.md`              |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-hello` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-00), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-hello` is the smallest possible complete command-line tool. It prints a greeting, but it
does so _properly_: it parses options, validates input, produces the same bytes on every
operating system, and reports errors and exit statuses the way a professional POSIX utility
does. Every later project in the curriculum builds on the conventions this tool establishes.

### 1.3 Scope

In scope: printing a greeting to standard output, choosing the greeted name, repeating the
greeting, help and version information, and clear usage errors.
Out of scope: localization (translated greetings), colors, interactive input, configuration
files, and reading environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                     | Primary interest                           |
| :--- | :----------------- | :-------------------------------------------------------------- | :----------------------------------------- |
| SH-1 | Terminal user      | Runs the command by hand in a shell on Linux, macOS, or Windows | Readable output, helpful errors            |
| SH-2 | Script author      | Calls the tool from shell scripts or CI jobs                    | Predictable output bytes and exit statuses |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice    | A complete, unambiguous specification      |
| SH-4 | Grader / CI        | Runs automated acceptance tests on three operating systems      | Deterministic, byte-exact behavior         |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                    | Priority | Source |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- | :----- |
| UR-01 | As a terminal user, I want to run the tool with no arguments and see the classic greeting `Hello, World!`, so I can confirm it works.                               | M        | SH-1   |
| UR-02 | As a terminal user, I want to choose whom the tool greets, so the output can be personalized.                                                                       | M        | SH-1   |
| UR-03 | As a script author, I want to repeat the greeting a chosen number of times, so I can produce a known amount of output.                                              | S        | SH-2   |
| UR-04 | As a terminal user, I want a built-in help screen that lists every option, so I can use the tool without other documentation.                                       | M        | SH-1   |
| UR-05 | As a script author, I want to query the tool's version, so I can confirm which specification it implements.                                                         | M        | SH-2   |
| UR-06 | As a script author, I want invalid usage to be rejected with a clear message and a distinct exit status, never silently ignored, so my scripts can detect mistakes. | M        | SH-2   |
| UR-07 | As a script author, I want success to be signaled with exit status 0, so I can chain the tool with `&&`.                                                            | M        | SH-2   |
| UR-08 | As a grader, I want identical output bytes on Linux, macOS, and Windows, including line endings, so a single set of expected outputs verifies every platform.       | M        | SH-4   |
| UR-09 | As a terminal user, I want names containing spaces and non-ASCII characters (for example `Zoë`) to be printed exactly as I typed them.                              | M        | SH-1   |
| UR-10 | As a learner, I want the tool's behavior to follow the curriculum's common CLI conventions, so what I learn here carries over to the later projects.                | M        | SH-3   |
| UR-11 | As a terminal user, I want the tool to start and finish instantly.                                                                                                  | S        | SH-1   |
| UR-12 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language.                                            | M        | SH-4   |

## 4. Usage scenarios

### 4.1 First run

A new user types `dp-hello` and sees `Hello, World!` on one line. The command exits with
status 0. (UR-01, UR-07)

### 4.2 Personalized greeting

A user types `dp-hello --name Ada` and sees `Hello, Ada!`. Typing `dp-hello -n 'Ada Lovelace'`
prints the full name, including the space. (UR-02, UR-09)

### 4.3 Scripted repetition

A CI job runs `dp-hello --count 3` to emit exactly three identical lines, then checks that the
exit status is 0. (UR-03, UR-07)

### 4.4 A mistake

A user mistypes `dp-hello --nme Ada`. The tool prints a one-line explanation, points to
`--help`, and exits with a non-zero status. Nothing is written to standard output. (UR-06)

### 4.5 Discovery

A user runs `dp-hello --help` to see the options, and `dp-hello --version` to check the version.
(UR-04, UR-05)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-hello` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term        | Meaning                                                      |
| :---------- | :----------------------------------------------------------- |
| Greeting    | The line `Hello, <name>!` followed by a line feed            |
| Exit status | The integer a process returns to its caller; 0 means success |
| Usage error | An invalid combination of command-line arguments             |

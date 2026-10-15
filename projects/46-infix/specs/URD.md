<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-infix](#user-requirements-document-urd--dp-infix)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the keyboard](#41-at-the-keyboard)
    - [4.2 A prepared exercise sheet](#42-a-prepared-exercise-sheet)
    - [4.3 Names and numbers](#43-names-and-numbers)
    - [4.4 A mistake](#44-a-mistake)
    - [4.5 An old exercise file](#45-an-old-exercise-file)
    - [4.6 Discovery and mistakes on the command line](#46-discovery-and-mistakes-on-the-command-line)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-infix

| Field               | Value                                                  |
| :------------------ | :----------------------------------------------------- |
| Document ID         | URD-46                                                 |
| Project             | `46-infix` — Shunting-Yard Infix to Postfix Conversion |
| Product             | `dp-infix`                                             |
| Version             | 1.0.0                                                  |
| Status              | Approved (pre-written by the curriculum)               |
| Successor documents | `SRS.md` (SRS-46), `user-manual.md`                    |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-infix` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-46), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-infix` rewrites arithmetic expressions such as `(A + B) * C` in postfix notation
(`A B + C *`), the form a stack machine or a calculator evaluates without parentheses. A
student can type expressions one after another, answering `Another? (y/n)` between them, and
see each conversion at once; a script can feed a prepared file of expressions and answers and
get the same report. A malformed expression is reported precisely instead of producing a
misleading result, and the session continues with the next one.

### 1.3 Scope

In scope: reading expressions and answers from the keyboard, a pipe, or a file; converting each
expression to postfix with the usual precedence and left associativity; printing the original
and the converted expression; optional prompts; reading files written on Windows or MS-DOS;
reporting malformed expressions, invalid answers, and unreadable files; help and version
information.
Out of scope: evaluating expressions, unary minus, functions, exponentiation, other notations
(prefix, expression trees), writing files, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                | Primary interest                                                    |
| :--- | :----------------- | :------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| SH-1 | Student            | Types expressions by hand on Linux, macOS, or Windows to check conversions | An immediate, correct answer; clear prompts; precise error messages |
| SH-2 | Script author      | Feeds prepared expression files through the tool in scripts and batch jobs | Predictable output bytes and exit statuses                          |
| SH-3 | Instructor         | Uses the tool to produce reference answers for exercises                   | The textbook's precedence rules and report layout, exactly          |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice               | A complete, unambiguous specification                               |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                 | Deterministic, byte-exact behavior                                  |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                      | Priority | Source     |
| :---- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to convert an infix expression with `+ - * / %` and parentheses to postfix, with `* / %` binding tighter than `+ -` and operators of equal precedence grouped from the left.                     | M        | SH-1, SH-3 |
| UR-02 | As a student, I want operands to be names or numbers of several characters, such as `rate` or `40`, not only single letters.                                                                                          | S        | SH-1       |
| UR-03 | As an instructor, I want each result to show the original expression above its postfix form, with the postfix tokens separated by single spaces.                                                                      | M        | SH-3       |
| UR-04 | As a student, I want to convert one expression after another, answering whether I want another, until I say no or end the input.                                                                                      | M        | SH-1       |
| UR-05 | As a script author, I want to pipe a dialog into the tool or name a file holding it, so I can process prepared exercises.                                                                                             | M        | SH-2       |
| UR-06 | As a student, I want to see each conversion as soon as I have typed the expression.                                                                                                                                   | M        | SH-1       |
| UR-07 | As a student, I want the tool to prompt me for the expression and the answer when I request it, without the prompts appearing in the report I save.                                                                   | S        | SH-1       |
| UR-08 | As a student, I want a malformed expression (unbalanced parentheses, a missing operand, a stray character) reported with its line and the first problem found, and then to be able to go on with the next expression. | M        | SH-1       |
| UR-09 | As a script author, I want a non-zero exit status whenever an expression was rejected, an answer was not understood, or the input could not be read.                                                                  | M        | SH-2       |
| UR-10 | As a student, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                                   | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                                | M        | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                    | M        | SH-2       |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform; and the tool to follow the curriculum's common CLI conventions.                      | M        | SH-4, SH-5 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to convert long expressions quickly.                                             | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the keyboard

A student runs `dp-infix --prompt`, sees `Enter infix expression:types `A + B * C`and
Enter, and at once sees`Infix: A + B * C`and`Postfix: A B C * +`, followed by
`Another? (y/n)The student types `n` and the tool exits with status 0. (UR-01, UR-03,
UR-04, UR-06, UR-07)

### 4.2 A prepared exercise sheet

An instructor keeps a file in which expression lines alternate with `y` lines and the last
answer is `n`, and runs `dp-infix sheet.txt > answers.txt`. The file holds two lines per
expression and nothing else. (UR-03, UR-05)

### 4.3 Names and numbers

A student converts `rate * (hours + 40) % 7` and gets `rate hours 40 + * 7 %`. (UR-01, UR-02)

### 4.4 A mistake

A student types `(A + B` and sees `dp-infix: -:1: unmatched '('` on standard error, then the
`Another?` question; answering `y` lets the student type the corrected expression. When the
session ends, the exit status is 1 because one expression was rejected. (UR-08, UR-09)

### 4.5 An old exercise file

A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like the same file with LF line endings. (UR-10)

### 4.6 Discovery and mistakes on the command line

A user runs `dp-infix --help` to see the rules, and `dp-infix a.txt b.txt` is rejected because
the tool reads one file. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must not wait for the end of the input before answering.                           |

## 6. User acceptance criteria

The users will accept `dp-infix` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term               | Meaning                                                                                              |
| :----------------- | :--------------------------------------------------------------------------------------------------- |
| Infix notation     | The usual way of writing arithmetic, with each operator between its two operands: `A + B`            |
| Postfix notation   | Reverse Polish notation, with each operator after its two operands: `A B +`; it needs no parentheses |
| Operand            | A name or number in an expression, such as `A`, `x1`, or `40`                                        |
| Precedence         | The rule that decides which operator applies first: `*`, `/`, and `%` before `+` and `-`             |
| Left associativity | Operators of equal precedence apply from left to right: `A - B - C` means `(A - B) - C`              |
| Dialog             | The alternation of an expression and the answer to `Another? (y/n)`                                  |
| End of input       | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard           |
| Exit status        | The integer a process returns to its caller; 0 means success                                         |

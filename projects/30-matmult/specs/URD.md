<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-matmult](#user-requirements-document-urd--dp-matmult)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Checking an exercise](#41-checking-an-exercise)
    - [4.2 A matrix file in a pipeline](#42-a-matrix-file-in-a-pipeline)
    - [4.3 A product that is too large](#43-a-product-that-is-too-large)
    - [4.4 A typo](#44-a-typo)
    - [4.5 An old data file](#45-an-old-data-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-matmult

| Field               | Value                                       |
| :------------------ | :------------------------------------------ |
| Document ID         | URD-30                                      |
| Project             | `30-matmult` — Matrix Multiplication Engine |
| Product             | `dp-matmult`                                |
| Version             | 1.0.0                                       |
| Status              | Approved (pre-written by the curriculum)    |
| Successor documents | `SRS.md` (SRS-30), `user-manual.md`         |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-matmult` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-30), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-matmult` multiplies two square matrices of whole numbers. A student checking homework can
type the size and the two matrices row by row and see each matrix confirmed before the next is
typed; a script can pipe in a file and get the same report. The product is exact for every
result that fits in a 64-bit integer, and a result that does not fit is reported instead of
being printed wrong.

### 1.3 Scope

In scope: reading a size and two square matrices from the keyboard, a pipe, or a file;
printing both matrices and their product; optional prompts; reading data files written on
Windows or MS-DOS; reporting invalid data, results that are too large, and unreadable files;
help and version information.
Out of scope: rectangular matrices, sizes above 20, fractional elements, results of unlimited
size, other matrix operations, writing files, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                 | Primary interest                                                     |
| :--- | :----------------- | :-------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| SH-1 | Student            | Types small matrices by hand on Linux, macOS, or Windows to check exercises | Clear prompts; each matrix confirmed before the next; helpful errors |
| SH-2 | Script author      | Pipes matrix files through the tool in shell scripts                        | Predictable output bytes and exit statuses                           |
| SH-3 | Numerical analyst  | Relies on the results being exact                                           | No silent wrap-around; overflow reported precisely                   |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                | A complete, unambiguous specification                                |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                  | Deterministic, byte-exact behavior                                   |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                         | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to give a matrix size from 1 to 20 and then two square matrices of that size, row by row.                                           | M        | SH-1       |
| UR-02 | As a student, I want both matrices printed back under clear headings, so I can check that they were read as I meant them.                                | M        | SH-1       |
| UR-03 | As a student, I want the product of the two matrices printed, row by row, under its own heading.                                                         | M        | SH-1       |
| UR-04 | As a numerical analyst, I want every product element to be exact, and a product that is too large for 64-bit integers reported instead of printed wrong. | M        | SH-3       |
| UR-05 | As a script author, I want to pipe the data into the tool or name a file, so I can process data I already have.                                          | M        | SH-2       |
| UR-06 | As a student, I want to see the first matrix as soon as I have typed it, before I type the second.                                                       | S        | SH-1       |
| UR-07 | As a student, I want the tool to ask for the size and for each matrix when I request it, without the prompts appearing in the report I save.             | S        | SH-1       |
| UR-08 | As a script author, I want an invalid size or element, or data that ends too early, reported with its position and a non-zero exit status.               | M        | SH-2       |
| UR-09 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                   | M        | SH-2       |
| UR-10 | As a student, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                 | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query.                                                                                   | M        | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                       | M        | SH-2       |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, following the curriculum's common CLI conventions.                              | M        | SH-4, SH-5 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to answer quickly.  | M        | SH-5       |

## 4. Usage scenarios

### 4.1 Checking an exercise

A student runs `dp-matmult --prompt`, sees `Input matrix size:types `2`, sees
`Input first matrix by row`, types `1 2`and`3 4`, and at once sees the heading `Matrix m1:`and the two rows. After`Input second matrix by row`the student types`2 0`and`1 2`, and
sees `Matrix m2:`, then `Product m3:`with the rows`4 4`and`10 8`. (UR-01, UR-02, UR-03,
UR-06, UR-07)

### 4.2 A matrix file in a pipeline

A script runs `dp-matmult data.txt > report.txt`. The report holds the three headed matrices
and nothing else; the prompts never appear. (UR-02, UR-03, UR-05)

### 4.3 A product that is too large

Both matrices contain the number 3037000500, whose square exceeds 9223372036854775807, in
positions that meet in row 1, column 2 of the product. The tool prints both matrices,
reports `integer overflow in product row 1, column 2`, prints no product, and exits with
status 1. (UR-04)

### 4.4 A typo

The second matrix in a file contains `x8`. The tool prints the first matrix, reports
`bad.txt:5: invalid integer 'x8'`, and exits with status 1. (UR-08)

### 4.5 An old data file

A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like a file with LF line endings. (UR-10)

### 4.6 Discovery and mistakes

A user runs `dp-matmult --help` to see the input format, and `dp-matmult a.txt b.txt` is
rejected because the tool reads one file. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must not wait for the end of the input before printing the first matrix.           |

## 6. User acceptance criteria

The users will accept `dp-matmult` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term            | Meaning                                                                                                                                                |
| :-------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Matrix          | A square table of _N_ rows and _N_ columns of whole numbers                                                                                            |
| Size            | The number _N_ of rows (and of columns) of both matrices, 1 … 20                                                                                       |
| Row-major order | Row 1 from left to right, then row 2, and so on: the order in which elements are typed                                                                 |
| Product         | The matrix whose element in row _i_, column _j_ is the sum over _k_ of (row _i_, column _k_ of the first matrix) × (row _k_, column _j_ of the second) |
| Overflow        | A result, or a step of computing it, outside −9223372036854775808 … 9223372036854775807                                                                |
| End of input    | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard                                                             |
| Exit status     | The integer a process returns to its caller; 0 means success                                                                                           |

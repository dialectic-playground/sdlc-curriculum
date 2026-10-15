<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-films](#user-requirements-document-urd--dp-films)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 A keyboard session](#41-a-keyboard-session)
    - [4.2 A batch of films](#42-a-batch-of-films)
    - [4.3 A tie](#43-a-tie)
    - [4.4 A broken sample set](#44-a-broken-sample-set)
    - [4.5 A typo in a query](#45-a-typo-in-a-query)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-films

| Field               | Value                                                   |
| :------------------ | :------------------------------------------------------ |
| Document ID         | URD-41                                                  |
| Project             | `41-films` — 1-Nearest Neighbor Film Success Classifier |
| Product             | `dp-films`                                              |
| Version             | 1.0.0                                                   |
| Status              | Approved (pre-written by the curriculum)                |
| Successor documents | `SRS.md` (SRS-41), `user-manual.md`                     |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-films` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-41), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

A film studio wants a quick, explainable forecast for films it has not yet released. It keeps a
sample set of past films: for each, how often the director's earlier films were hits, how often
the leading actors' earlier films were hits, and whether the film itself was a hit. `dp-films`
reads that sample set and then answers, for each new film described by the same two
percentages, "hit" or "flop" — the outcome of the most similar past film. The same question
must always get the same answer, on every computer.

### 1.3 Scope

In scope: reading a sample set of up to 100 films (by default `films.dat`); classifying any
number of films, typed at the keyboard or read from a file; prompting at the keyboard; reading
files written on Windows or MS-DOS; reporting mistakes in the sample set and in the queries;
help and version information.
Out of scope: other classification methods (several neighbors, weights), other features or
outcomes, showing distances, changing the sample set, configuration files, and environment
variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder             | Description                                                                               | Primary interest                                                    |
| :--- | :---------------------- | :---------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| SH-1 | Analyst at the keyboard | Types the two percentages of each film and reads the verdict, on Linux, macOS, or Windows | Prompts, an immediate answer, clear messages                        |
| SH-2 | Script author           | Classifies a file of films in a batch job or pipeline                                     | Predictable output bytes and exit statuses                          |
| SH-3 | Data curator            | Maintains the sample set                                                                  | Every mistake in the sample set found and located before it is used |
| SH-4 | Learner (assignee)      | Implements the tool in a language repository of their choice                              | A complete, unambiguous specification                               |
| SH-5 | Grader / CI             | Runs automated acceptance tests on three operating systems                                | Deterministic, byte-exact behavior                                  |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                   | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As an analyst, I want the tool to use the sample set `films.dat` in the current directory unless I name another file.                                                                              | M        | SH-1, SH-3 |
| UR-02 | As an analyst, I want to give each film as two percentages (director, then cast) and be told `The film is a HIT!` or `The film is a flop.`, until I end the input.                                 | M        | SH-1       |
| UR-03 | As an analyst, I want each film to get the outcome of the most similar film in the sample set, measured by straight-line distance between the percentage pairs, with ties settled by a fixed rule. | M        | SH-1, SH-3 |
| UR-04 | As a script author, I want to classify a whole file of films, or standard input, with one verdict per line and nothing else on standard output.                                                    | M        | SH-2       |
| UR-05 | As an analyst, I want each verdict to appear as soon as I have typed the second percentage.                                                                                                        | S        | SH-1       |
| UR-06 | As an analyst, I want optional prompts that tell me what to type, which never mix with the verdicts when output is saved.                                                                          | S        | SH-1       |
| UR-07 | As a data curator, I want a sample set with a wrong value, a missing value, too many films, or no films at all to be rejected with its line number before any film is classified.                  | M        | SH-3       |
| UR-08 | As a script author, I want an invalid or incomplete query to be reported with its line number, keeping the verdicts already given, and a non-zero exit status.                                     | M        | SH-2       |
| UR-09 | As an analyst, I want sample sets and query files written on Windows or MS-DOS (CRLF line endings, a Ctrl-Z end-of-file mark) to be read correctly.                                                | S        | SH-1, SH-3 |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                             | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before anything is read.                                                                        | M        | SH-2       |
| UR-12 | As a grader, I want identical verdicts, bytes, and line endings on Linux, macOS, and Windows, including for films that are equally near to two sample films.                                       | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                               | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to classify large batches quickly.                            | M        | SH-5       |

## 4. Usage scenarios

### 4.1 A keyboard session

An analyst runs `dp-films --prompt` in the directory that holds `films.dat`. The tool asks for
the director's percentage; the analyst types `75.0`. It asks for the cast's percentage; the
analyst types `85.0`, and `The film is a HIT!` appears at once. After further films the analyst
ends the input (Ctrl-D, or Ctrl-Z and Enter on Windows), and the tool exits with status 0.
(UR-01, UR-02, UR-05, UR-06)

### 4.2 A batch of films

A script runs `dp-films -s studio.dat upcoming.txt > verdicts.txt`, where `upcoming.txt` holds
one film per line. `verdicts.txt` holds one verdict per film, in order. (UR-04)

### 4.3 A tie

A film is exactly as near to a sample hit as to a sample flop. It gets the outcome of whichever
of the two comes first in the sample set, every time, on every system. (UR-03, UR-12)

### 4.4 A broken sample set

The curator mistyped an outcome code as `2` on line 3 of the sample set. `dp-films` reports
`dp-films: bad-code.dat:3: value out of range '2'` and exits with status 1 without asking for
or classifying any film. (UR-07)

### 4.5 A typo in a query

Line 3 of a query file reads `90 seventy`. The verdicts for lines 1 and 2 are printed, then
`dp-films: bad-query.txt:3: invalid number 'seventy'`, and the exit status is 1. (UR-08)

### 4.6 Discovery and mistakes

A user runs `dp-films --help` to see the options. `dp-films one.txt two.txt` is rejected,
because only one query file can be named. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale, terminal settings, or processor.                           |

## 6. User acceptance criteria

The users will accept `dp-films` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term                | Meaning                                                                                    |
| :------------------ | :----------------------------------------------------------------------------------------- |
| Sample set          | The films whose outcome is known, used to classify new films (the textbook's "sample set") |
| Director percentage | The percentage of hits among the earlier films of a film's director                        |
| Cast percentage     | The percentage of hits among the earlier films of a film's leading actors                  |
| Outcome code        | 1 for a hit, 0 for a flop                                                                  |
| Query               | A film to classify: a director percentage and a cast percentage                            |
| Verdict             | The line `The film is a HIT!` or `The film is a flop.`                                     |
| Nearest neighbor    | The sample film at the smallest distance from the query                                    |
| Exit status         | The integer a process returns to its caller; 0 means success                               |

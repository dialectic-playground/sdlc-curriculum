# User Requirements Document (URD) — dp-bargraph2, dp-grade

| Field | Value |
| :-- | :-- |
| Document ID | URD-20 |
| Project | `20-bargraph-grade` — Modular Procedural Decomposition & Evaluation |
| Products | `dp-bargraph2`, `dp-grade` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-20), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-bargraph2` and `dp-grade` need, in their own
terms. It is the starting point for the Software Requirements Specification (SRS-20), which
turns each need into precise, testable system behavior.

### 1.2 Product vision
Two small programs show what dividing a program into procedures buys. `dp-bargraph2` is the
bar-graph tool of Project 16 rebuilt from two reusable procedures — one that echoes a title,
one that draws a bar — and it must remain a drop-in replacement for `dp-bargraph`. `dp-grade`
helps an instructor decide, student by student, whether a weighted combination of a mid-term
and a final-exam score is a pass. It can be used at the keyboard, where it asks its questions,
or fed a prepared file of answers, and a borderline average always gets the grade the decimal
numbers imply, on every computer.

### 1.3 Scope
In scope: drawing the Project 16 bar graph; computing pass/fail grades from two scores on a
scale of 0 to 10 and a mid-term weight from 0 to 1; reading answers from the keyboard, a pipe,
or a file; optional prompts; reporting malformed answers with a line number; help and version
information.
Out of scope: letter grades other than P and F, other thresholds or scales, more than two
exams, printing the numeric average, storing grades, and student names.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Instructor | Grades students at the keyboard, or from a prepared file, on Linux, macOS, or Windows | Correct grades, especially at the threshold; clear questions |
| SH-2 | Script author | Pipes data into either tool and uses the output and exit status | Predictable output bytes and exit statuses |
| SH-3 | Maintainer | Keeps `dp-bargraph` and `dp-bargraph2` in service side by side | The two tools are interchangeable |
| SH-4 | Learner (assignee) | Implements both tools in a language repository of their choice | A complete, unambiguous specification and a clear required structure |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a maintainer, I want `dp-bargraph2` to draw exactly the same graph as `dp-bargraph` for the same input, so either tool can be used. | M | SH-3 |
| UR-02 | As a maintainer, I want `dp-bargraph2` to report bad data exactly as `dp-bargraph` does. | M | SH-3 |
| UR-03 | As an instructor, I want files with Windows line endings or a trailing Ctrl-Z to be read exactly like other files. | M | SH-1 |
| UR-04 | As an instructor, I want to answer whether to compute another grade, then give the mid-term score, the final score, and the mid-term weight, in that order, separated by spaces or line breaks as I like. | M | SH-1 |
| UR-05 | As an instructor, I want the session to end when I answer 0 or when my file of answers ends. | M | SH-1, SH-2 |
| UR-06 | As an instructor, I want a score outside 0–10, a weight outside 0–1, or any answer that is not a number rejected with the line where it occurs, so a typing mistake never produces a grade. | M | SH-1 |
| UR-07 | As an instructor, I want the average computed exactly from the numbers I typed, so that an average of exactly 7 always fails and nothing is passed or failed by a rounding accident. | M | SH-1 |
| UR-08 | As an instructor, I want each grade shown as a single line, `Grade is: P` or `Grade is: F`. | M | SH-1, SH-2 |
| UR-09 | As an instructor at the keyboard, I want to be asked for each answer, without the questions mixing into output that I redirect to a file. | S | SH-1 |
| UR-10 | As a script author, I want a missing or unreadable file reported clearly, with an exit status that shows the failure. | M | SH-2 |
| UR-11 | As a user of either tool, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before anything is read. | M | SH-2 |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-14 | As a learner, I want both tools to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-15 | As a learner, I want the required division of each program into procedures stated clearly, so I can practise procedural decomposition and have it reviewed. | M | SH-4 |
| UR-16 | As a user, I want both tools to respond instantly. | S | SH-1 |
| UR-17 | As a grader, I want both tools to install and uninstall with standard commands, regardless of their implementation language. | M | SH-5 |

## 4. Usage scenarios

### 4.1 The same graph
A maintainer runs `dp-bargraph2 bargraph.in` and `dp-bargraph bargraph.in` and compares the
outputs: they are identical. (UR-01)

### 4.2 Grading at the keyboard
An instructor runs `dp-grade --prompt`. The tool asks
`Compute another grade (1 = Yes, 0 = No)? `; the instructor types `1`, is asked
`Enter mid term, final, weight: `, and types `8 6 0.5`. The tool prints `Grade is: F`, because
the average is exactly 7, and asks again. The instructor types `0` and the tool exits with
status 0. (UR-04, UR-05, UR-07, UR-08, UR-09)

### 4.3 Grading from a file
An instructor prepares `grades.txt` with one round per line, such as `1 10 5 0.8`, and runs
`dp-grade grades.txt > results.txt`. The file holds one grade line per round and nothing else;
the file of answers does not need a final `0`. (UR-04, UR-05, UR-08)

### 4.4 A borderline weight
An instructor grades a student with 7 in both exams and a mid-term weight of 0.2. The average
is exactly 7, so the grade is `F` on every computer — although a naive binary floating-point
calculation gives 7.000000000000001. (UR-07)

### 4.5 A typing mistake
An instructor types `11` as a mid-term score. The tool reports
`dp-grade: grades.txt:4: value out of range '11'` and exits with status 1; the grades printed
before it stand. (UR-06)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as native executables or language-runtime launchers. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must give the same grades whatever the processor's or compiler's floating-point behavior. |

## 6. User acceptance criteria

The users will accept `dp-bargraph2` and `dp-grade` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. Both help texts exactly match the ones published in the user manual.
4. A design review confirms the procedural structure required by SRS-20 NFR-05.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Round | One answer 1 followed by a mid-term score, a final-exam score, and a weight |
| Weight | The share of the mid term in the average, from 0 to 1; the final exam gets the rest |
| Average | Weight × mid term + (1 − weight) × final |
| Pass (P) | An average greater than 7 |
| Fail (F) | An average of 7 or less |
| Prompt | A question the tool writes before reading an answer, only when asked to with `--prompt` |
| Procedure | A named unit of code that performs one task and can be called repeatedly |
| Exit status | The integer a process returns to its caller; 0 means success |

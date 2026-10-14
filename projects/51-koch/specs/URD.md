# User Requirements Document (URD) — dp-koch

| Field | Value |
| :-- | :-- |
| Document ID | URD-51 |
| Project | `51-koch` — Recursive Fractal Geometry: The Koch Snowflake |
| Product | `dp-koch` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-51), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-koch` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-51), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-koch` draws the von Koch curve and snowflake, the classic fractal in which every straight
segment is replaced by four shorter ones with a triangular bump in the middle. Instead of
drawing on a screen, it writes the exact coordinates of every vertex, or an SVG picture that
any browser can show. A student can explore the levels one after another in a short dialog; a
script can generate a figure with one command. The numbers are the same to the last digit on
every computer and in every implementation.

### 1.3 Scope
In scope: Koch curves and snowflakes of levels 0 to 6; a chosen base length; coordinates as
text or an SVG document; the textbook's dialog (a level, then "do another?") read from the
keyboard, a pipe, or a file; a one-shot command-line mode; optional prompts; reporting invalid
dialog input and unreadable files; help and version information.
Out of scope: other fractals, levels above 6, other image formats (PNG, PostScript), colors and
styling, choosing the start point or orientation, writing files directly, configuration files,
and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Student explorer | Draws figures of increasing level at the keyboard on Linux, macOS, or Windows | A simple dialog; a picture to look at |
| SH-2 | Script author | Generates coordinates or SVG files in scripts and build jobs | Predictable output bytes and exit statuses |
| SH-3 | Teacher | Uses the figures to explain recursion and fractal dimension | Correct geometry; segment counts that match the theory |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior, including floating-point digits |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a script author, I want to draw one figure of a chosen level with a single command, without any dialog. | M | SH-2 |
| UR-02 | As a teacher, I want the figure to be the true Koch curve — four segments of one third the length per segment and level, so 4^k segments at level k — or the closed snowflake made of three curves. | M | SH-3 |
| UR-03 | As a grader, I want every vertex printed with fixed, documented precision, with the same digits from every implementation and on every computer. | M | SH-5 |
| UR-04 | As a student explorer, I want to enter a level, see the figure, and be asked whether to draw another, as in the textbook program. | M | SH-1 |
| UR-05 | As a student explorer, I want to see each figure as soon as I have entered its level, and to be able to feed the same dialog from a file or a pipe. | M | SH-1, SH-2 |
| UR-06 | As a student explorer, I want a picture I can open in a web browser. | S | SH-1 |
| UR-07 | As a student explorer, I want to be asked for each entry when I request it, without the questions appearing in the output I save. | S | SH-1 |
| UR-08 | As a script author, I want a mistyped level or answer reported with its position and a non-zero exit status, while the figures already drawn are kept. | M | SH-2 |
| UR-09 | As a student explorer, I want dialog files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-10 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-2 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-2 |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-14 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-15 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to draw even the largest figure quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 Exploring the levels
A student runs `dp-koch --prompt`, sees `Enter level (0-6): `, types `1`, and at once sees the
five vertices of the level-1 curve. Asked `Do another (y = yes, n = no)? `, the student types
`y`, then `2`, sees seventeen vertices, and finally answers `n`. The tool exits with status 0.
(UR-02, UR-04, UR-05, UR-07)

### 4.2 A picture for the lecture
A teacher runs `dp-koch --svg --snowflake --level 4 > snowflake.svg` and opens the file in a
browser: a closed snowflake with 768 segments. (UR-01, UR-02, UR-06)

### 4.3 Same digits everywhere
A grader compares `dp-koch -l 6` from implementations in three languages on three operating
systems. All 4097 vertex lines agree byte for byte, including coordinates that rounding errors
would otherwise print as `-0.000000`. (UR-03, UR-13)

### 4.4 A typo in the dialog
A dialog file contains `7` as its third entry. The tool writes the figures for the entries
before it, then reports `dialog.txt:3: value out of range '7'` and exits with status 1. (UR-08)

### 4.5 Discovery and mistakes
A user runs `dp-koch --help` to see the options, and `dp-koch --level 9` is rejected because
levels end at 6. (UR-11, UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, graphics hardware, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: it must not wait for the end of the input before drawing. |

## 6. User acceptance criteria

The users will accept `dp-koch` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Koch curve | The fractal obtained by repeatedly replacing each segment with four segments of one third its length, the middle two forming a triangular bump |
| Level | The number of times the replacement is applied: level 0 is a straight segment |
| Snowflake | Three Koch curves on the sides of an equilateral triangle, bumps pointing outward |
| Vertex | A corner point of the figure, given by its x and y coordinates |
| SVG | Scalable Vector Graphics, a text-based picture format shown by web browsers |
| Exit status | The integer a process returns to its caller; 0 means success |

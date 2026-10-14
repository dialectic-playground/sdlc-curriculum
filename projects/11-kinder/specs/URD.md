# User Requirements Document (URD) — dp-kinder

| Field | Value |
| :-- | :-- |
| Document ID | URD-11 |
| Project | `11-kinder` — Console Output & Environment Verification |
| Product | `dp-kinder` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-11), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-kinder` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-11), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-kinder` prints one fixed line, `ANSI--A kinder and gentler C!`, and exits. Its value lies
not in what it prints but in what it proves: that a toolchain can build, install, and run a
program on Linux, macOS, and Windows, and that the program behaves like every other tool of
the curriculum when it is given help requests, stray words, or mistyped options.

### 1.3 Scope
In scope: printing the message to standard output, help and version information, and clear
usage errors.
Out of scope: any other message, options that change the message, reading standard input or
files, localization, colors, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Runs the command by hand in a shell on Linux, macOS, or Windows | A recognizable result; helpful errors |
| SH-2 | Script author | Calls the tool from shell scripts or CI jobs to check an installation | Predictable output bytes and exit statuses |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to run the tool and see the line `ANSI--A kinder and gentler C!`, exactly as the textbook prints it, so I can confirm my toolchain works. | M | SH-1 |
| UR-02 | As a script author, I want success to be signaled with exit status 0, so I can chain the tool with `&&`. | M | SH-2 |
| UR-03 | As a script author, I want the tool to ignore whatever is connected to its standard input, so it never waits for input in a script or pipeline. | M | SH-2 |
| UR-04 | As a terminal user, I want a built-in help screen, so I can find out what the tool does. | M | SH-1 |
| UR-05 | As a script author, I want to query the tool's version, so I can confirm which specification it implements. | M | SH-2 |
| UR-06 | As a script author, I want stray words and invalid options rejected with a clear message and a distinct exit status, never silently ignored, so my scripts can detect mistakes. | M | SH-2 |
| UR-07 | As a learner, I want the tool to follow the curriculum's common CLI conventions, including where `--help` and `--version` take effect and what `--` means, so what I learn here carries over to the later projects. | M | SH-3 |
| UR-08 | As a grader, I want identical output bytes on Linux, macOS, and Windows, including line endings, so a single set of expected outputs verifies every platform. | M | SH-4 |
| UR-09 | As a terminal user, I want the tool to start and finish instantly. | S | SH-1 |
| UR-10 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language. | M | SH-4 |

## 4. Usage scenarios

### 4.1 Checking a new installation
A learner types `dp-kinder` and sees `ANSI--A kinder and gentler C!` on one line. The command
exits with status 0. (UR-01, UR-02)

### 4.2 In a pipeline
A CI job runs `dp-kinder < /dev/null > out.txt && cmp out.txt expected.txt`. The tool does not
read its standard input, and `out.txt` contains exactly one LF-terminated line on every
operating system. (UR-02, UR-03, UR-08)

### 4.3 A mistake
A user types `dp-kinder hello`. The tool prints a one-line explanation, points to `--help`, and
exits with a non-zero status. Nothing is written to standard output. (UR-06)

### 4.4 Discovery
A user runs `dp-kinder --help` to see what the tool does, and `dp-kinder --version` to check
the version. Adding a stray word after `--help` still shows the help. (UR-04, UR-05, UR-07)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale, console code page, or terminal settings. |

## 6. User acceptance criteria

The users will accept `dp-kinder` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Message | The line `ANSI--A kinder and gentler C!` followed by a line feed |
| Operand | A command-line word that is not an option, such as `hello` or `-` |
| Exit status | The integer a process returns to its caller; 0 means success |
| Usage error | An invalid combination of command-line arguments |

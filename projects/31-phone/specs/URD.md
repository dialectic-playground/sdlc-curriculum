# User Requirements Document (URD) — dp-phone

| Field | Value |
| :-- | :-- |
| Document ID | URD-31 |
| Project | `31-phone` — Student Directory Lookup via Selection Sort & Binary Search |
| Product | `dp-phone` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-31), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-phone` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-31), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-phone` is a school office's telephone directory. The office keeps its students in a
fixed-width file, `students.dat`: last name, first name, and telephone number in fixed
columns, in no particular order. A clerk starts `dp-phone`, types a student's last name, and
immediately sees that student's record, or is told that the name is not in the directory. The
tool loads and checks the whole file once, sorts it, and then answers each name with a binary
search, so every lookup is fast however many students there are.

### 1.3 Scope
In scope: loading the student file (by default `students.dat`, or another file or standard
input); checking that every record has the fixed layout; answering last names typed at the
keyboard or read from a file or pipe, one per line; an optional prompt; reading files written on
Windows or MS-DOS; help and version information.
Out of scope: searching by first name or telephone number, partial or case-insensitive
matching, listing every student with the same last name, adding, changing, or deleting
records, and saving the sorted directory.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Office clerk | Looks up students at a terminal on Linux, macOS, or Windows | An immediate, unambiguous answer for each name typed |
| SH-2 | Script author | Feeds a list of names from a file or pipe and processes the answers | Predictable output bytes and exit statuses; one answer line per name |
| SH-3 | Directory maintainer | Edits `students.dat` by hand or exports it from another system | A clear message, with a line number, when a record is malformed |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification, including the sort and search algorithms |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As an office clerk, I want the tool to load `students.dat` from the current directory when I start it with no arguments. | M | SH-1 |
| UR-02 | As an office clerk, I want to type a last name and see the student's whole record, or a message that the name is not in the directory. | M | SH-1 |
| UR-03 | As an office clerk, I want last names that contain spaces, such as `Von Neumann`, to be looked up exactly as I type them. | M | SH-1 |
| UR-04 | As an office clerk, I want each answer to appear as soon as I press Enter, and to stop with the usual end-of-input key. | M | SH-1 |
| UR-05 | As an office clerk, I want an optional prompt that asks for each name, without the prompt getting mixed into saved output. | S | SH-1 |
| UR-06 | As a script author, I want to read the names from a file or standard input and to use another student file, including standard input. | M | SH-2 |
| UR-07 | As a script author, I want exactly one answer line for each non-empty name, and blank lines to be ignored. | M | SH-2 |
| UR-08 | As a directory maintainer, I want a malformed record to be reported with its line number before any name is answered. | M | SH-3 |
| UR-09 | As a directory maintainer, I want student files and name lists written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-3 |
| UR-10 | As a script author, I want every failure (a missing file, a malformed record) to give a clear message and a non-zero exit status. | M | SH-2 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, without any file being read. | M | SH-2 |
| UR-13 | As a learner, I want the tool to sort with selection sort and look names up with binary search, exactly as specified, so that I practise both algorithms. | M | SH-4 |
| UR-14 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions. | M | SH-4, SH-5 |
| UR-15 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to answer quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 At the office counter
A clerk runs `dp-phone --prompt` in the directory that holds `students.dat`, sees
`Enter a student's name, or signal EOF to halt: `, types `Turing`, and sees
`Record: Turing                   Alan                     508-416-0633`. Typing `Knuth`
answers `Knuth is not in our directory.` Ctrl-D (Ctrl-Z, Enter on Windows) ends the session
with exit status 0. (UR-01, UR-02, UR-04, UR-05)

### 4.2 A name with a space
The clerk types `Von Neumann` and sees Johnny Von Neumann's record. (UR-03)

### 4.3 A list of names
A script runs `dp-phone callers.txt > answers.txt`, where `callers.txt` holds one last name per
line and a few blank lines. `answers.txt` has one line per name, in the same order. (UR-06,
UR-07)

### 4.4 A damaged directory
A maintainer has deleted one digit of a telephone number on line 4 of `students.dat`. The tool
reports `dp-phone: students.dat:4: invalid record length 61, expected 62`, answers no names,
and exits with status 1. (UR-08, UR-10)

### 4.5 Another directory
`dp-phone -f staff.dat` loads `staff.dat` instead; `export-students | dp-phone -f - names.txt`
loads the records from a pipe and the names from `names.txt`. (UR-06)

### 4.6 Discovery and mistakes
A user runs `dp-phone --help` to see the options. `dp-phone names.txt more.txt` is rejected,
because only one name list can be read, and no file is opened. (UR-11, UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings; names are compared byte for byte. |

## 6. User acceptance criteria

The users will accept `dp-phone` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Student file | The file of student records: `students.dat` unless another is chosen |
| Record | One line of the student file: a 25-column last name, a 25-column first name, and a 12-column telephone number |
| Directory | The records of the student file, sorted |
| Name | One line of input that the user wants looked up as a last name |
| Exit status | The integer a process returns to its caller; 0 means success |

# User Requirements Document (URD) — dp-size

| Field | Value |
| :-- | :-- |
| Document ID | URD-39 |
| Project | `39-size` — Binary File Byte Size Inspector |
| Product | `dp-size` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-39), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-size` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-39), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-size` answers one question exactly: how many bytes does this file hold? A programmer types
the name of a source file without its `.c` extension, and the tool reports the file's size by
reading every byte of it — the same number `wc -c` or a directory listing shows, whatever the
file contains and whatever operating system it runs on. Line endings, NUL bytes, and old MS-DOS
end-of-file marks never change the count.

### 1.3 Scope
In scope: measuring files named without their extension, given on the command line or typed
(or piped) one per line on standard input; choosing another extension or none; an optional
prompt for interactive use; reporting missing files, directories, and malformed names; help and
version information.
Out of scope: measuring standard input itself, directories and their totals, human-readable
units (KiB, MiB), file-system metadata such as modification times, wildcards, configuration
files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Runs the tool by hand, typing names at the prompt, on Linux, macOS, or Windows | A familiar dialog; exact answers |
| SH-2 | Script author | Calls the tool with names as arguments or on standard input | Predictable output bytes and exit statuses; a record that names its file |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification; understanding binary versus text input |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to give the name of a C source file without its extension and be told its size in bytes. | M | SH-1 |
| UR-02 | As a script author, I want to give several names, as arguments or one per line on standard input, and have each measured in order. | M | SH-2 |
| UR-03 | As a script author, I want to choose another extension, or none at all, so I can measure files that are not C sources. | S | SH-2 |
| UR-04 | As a terminal user, I want the size to be the exact number of bytes in the file, whatever bytes it contains (NUL bytes, CRLF line endings, Ctrl-Z bytes) and however large it is. | M | SH-1, SH-3 |
| UR-05 | As a script author, I want each result to name the file it belongs to, in the textbook's `Byte size:` layout, with nothing else on standard output. | M | SH-2 |
| UR-06 | As a script author, I want one missing file not to stop the others from being measured, and a non-zero exit status if any name failed. | M | SH-2 |
| UR-07 | As a terminal user, I want a clear message naming the file when it does not exist, is a directory, or cannot be read, and when a name is empty. | M | SH-1 |
| UR-08 | As a terminal user, I want names typed or piped on Windows, with CRLF line endings or a final Ctrl-Z, to be read correctly. | S | SH-1 |
| UR-09 | As a terminal user, I want to be prompted for each name, as the textbook program did, without the prompt mixing into the results. | S | SH-1 |
| UR-10 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before any file is read. | M | SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions. | M | SH-3, SH-4 |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to measure large files quickly in little memory. | M | SH-4 |

## 4. Usage scenarios

### 4.1 The textbook dialog
A user runs `dp-size --prompt`, sees `File name (NO extension):`, types `size`, and is told
that `size.c` holds 562 bytes. The tool prompts again; the user ends the input with Ctrl-D
(Ctrl-Z then Enter on Windows). (UR-01, UR-09)

### 4.2 Several files at once
A script runs `dp-size main util io` and reads three records, for `main.c`, `util.c`, and
`io.c`, in that order. Another pipes a list of names into `dp-size`. (UR-02, UR-05)

### 4.3 Other extensions
`dp-size -e .h defs` measures `defs.h`; `dp-size -e '' Makefile` measures `Makefile`. (UR-03)

### 4.4 A binary file
A file written on Windows has CRLF line endings, a NUL byte, and a Ctrl-Z at its end. The size
`dp-size` reports is exactly the size the directory listing shows, on every platform. (UR-04)

### 4.5 A missing file
`dp-size missing size` reports `dp-size: missing.c: No such file or directory`, still measures
`size.c`, and exits with status 1. (UR-06, UR-07)

### 4.6 Discovery and mistakes
A user runs `dp-size --help` to see the options. `dp-size -e txt notes` is rejected, because
the extension must begin with a dot, and no file is read. (UR-10, UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must report the same byte size for the same file on every platform; no text-mode translation. |

## 6. User acceptance criteria

The users will accept `dp-size` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Name | A file name without its extension, as the user gives it |
| Extension | The suffix appended to each name: `.c` unless another is chosen |
| Byte size | The number of bytes stored in a file |
| Binary mode | Reading a file's bytes exactly as stored, with no line-ending or end-of-file translation |
| Ctrl-Z | The byte `0x1A`, which old MS-DOS programs used to mark the end of a text file |
| Exit status | The integer a process returns to its caller; 0 means success |

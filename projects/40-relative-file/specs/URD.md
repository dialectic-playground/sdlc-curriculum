# User Requirements Document (URD) — dp-relfile

| Field | Value |
| :-- | :-- |
| Document ID | URD-40 |
| Project | `40-relative-file` — Direct-Access Hashed Relative File Storage Engine |
| Product | `dp-relfile` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-40), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-relfile` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-40), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-relfile` is a tiny database in one file, built the way record-keeping systems were built
before relational databases: a *relative file* of 100 fixed-size slots, where the position of a
record is computed from its key, so a record is found by reading one or a few slots instead of
the whole file. Users add, find, and remove records by a 4-digit key, either one command at a
time or through the classic numbered menu, and can look inside the file to see where each
record landed. The file has the same bytes on every operating system and survives from one run
to the next.

### 1.3 Scope
In scope: creating the relative file when it is missing; adding, finding, and removing records
by key; reusing the slots of removed records; listing the occupied and deleted slots; the
numbered menu dialog, from the keyboard or a file, with optional prompts; detecting duplicate
keys, a full file, and a damaged file; choosing the file; help and version information.
Out of scope: files of other sizes or record layouts, updating a record in place, listing
records in key order, growing the file, compacting tombstones, concurrent access and locking,
non-ASCII data, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Clerk | Keeps records interactively through the menu, on Linux, macOS, or Windows | The familiar menu; clear answers |
| SH-2 | Script author | Adds, finds, and removes records from scripts | One command per operation; predictable output and exit statuses |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification of the file format and the hashing |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior; a file whose layout tests can observe |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a clerk, I want the file to be created, empty, the first time I use the tool, so there is nothing to set up. | M | SH-1 |
| UR-02 | As a clerk, I want each record to have a 4-digit key and up to 30 characters of data, and mistakes in either to be rejected. | M | SH-1 |
| UR-03 | As a clerk, I want to add a record and find it again by its key, even when several keys compete for the same place in the file. | M | SH-1 |
| UR-04 | As a clerk, I want to remove a record without losing any other record. | M | SH-1 |
| UR-05 | As a script author, I want to be told the outcome of every operation, and to have a duplicate key, a missing record, or a full file reported clearly with a non-zero exit status. | M | SH-2 |
| UR-06 | As a clerk, I want records to persist from one run to the next, and the place of a removed record to be reused. | M | SH-1 |
| UR-07 | As a learner, I want to see which slot holds which record, and which slots hold removed records, so I can follow the hashing. | S | SH-3, SH-4 |
| UR-08 | As a script author, I want to run single operations as commands, or a whole menu session from a file, and to be told the line of any malformed input. | M | SH-2 |
| UR-09 | As a clerk, I want a damaged or unusable file to be rejected with a clear message and never be damaged further. | M | SH-1 |
| UR-10 | As a clerk, I want the textbook's numbered menu, with its prompts when I ask for them, without the prompts mixing into the results. | S | SH-1 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, without any file being created or changed. | M | SH-2 |
| UR-13 | As a grader, I want identical output and identical file bytes on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions. | M | SH-3, SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and every operation to be fast. | M | SH-4 |

## 4. Usage scenarios

### 4.1 First use
A clerk runs `dp-relfile add 1234 'Ada Lovelace'` in an empty directory. The tool creates
`relative.dat` with 100 free slots, stores the record, and answers `Added 1234 in slot 70`.
`dp-relfile find 1234` later answers `Found 1234 in slot 70: Ada Lovelace`. (UR-01, UR-03,
UR-06)

### 4.2 Collisions
The keys `0000`, `0097`, and `9700` all hash to slot 0. Added in that order, they land in slots
0, 1, and 2, and each can be found. `dp-relfile slots` shows the three records. (UR-03, UR-07)

### 4.3 Removal and reuse
The clerk removes `0097`. `0194`, stored beyond it, can still be found; `dp-relfile slots` shows
slot 1 as `deleted`. The next record that hashes to slot 0 reuses slot 1. (UR-04, UR-06, UR-07)

### 4.4 The menu
A clerk runs `dp-relfile --prompt`, sees the numbered menu, picks `1`, types a key and data,
picks `2` to look a record up, and `0` to leave. A script feeds the same answers from a file
with `dp-relfile < session.txt`. (UR-08, UR-10)

### 4.5 Mistakes and failures
`dp-relfile add 123 x` is rejected because the key has three digits, and no file is touched.
Adding an existing key reports `duplicate key`; finding a missing key reports
`no such record`; both exit with status 1. (UR-02, UR-05, UR-12)

### 4.6 A damaged file
Someone truncates `relative.dat`. The next run reports
`relative.dat: not a relative file (size 3499, expected 3500)` and changes nothing. (UR-09)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must write the relative file with the same bytes on every platform, so a file can be copied between systems. |

## 6. User acceptance criteria

The users will accept `dp-relfile` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Relative file | A file of fixed-size slots in which a record's position is computed from its key |
| Slot | One of the 100 record positions, numbered 0 to 99 |
| Key | The 4-digit identifier of a record |
| Hashing | Computing a record's home slot from its key: the key modulo 97 |
| Collision | Two keys with the same home slot; the later one goes to the next available slot |
| Tombstone | A slot whose record was removed; searches pass over it and additions may reuse it |
| Exit status | The integer a process returns to its caller; 0 means success |

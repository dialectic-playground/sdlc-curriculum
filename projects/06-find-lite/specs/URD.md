# User Requirements Document (URD) — dp-find

| Field | Value |
| :-- | :-- |
| Document ID | URD-06 |
| Project | `06-find-lite` — Recursive File Discovery Suite |
| Product | `dp-find` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-06), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-find` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-06), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-find` walks one or more directory trees and reports the entries that satisfy a condition
the user writes on the command line: a name pattern, a type, a size, an age, or any boolean
combination of these. For each matching entry it prints the path or runs a command. It is a
focused, portable subset of the POSIX `find` utility. Its listing order and output bytes are
identical on Linux, macOS, and Windows, so scripts and tests that use it never depend on the
operating system or on the order in which a file system happens to return directory entries.

### 1.3 Scope
In scope: recursive traversal of one or more starting paths, depth limits, name matching with
glob patterns (case-sensitive and ASCII case-insensitive), type, size, modification-age, and
emptiness tests, boolean operators with parentheses, printing paths, running a command for each
match, and clear diagnostics for unreadable or missing paths and for malformed expressions.
Out of scope: following symbolic links, permission, owner, inode, and access-time tests,
deleting or modifying files directly, batching many paths into one command (`find`'s `-exec … +`),
formatted output (`-printf`), regular-expression name tests, and configuration files.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Searches for files by hand in a shell on Linux, macOS, or Windows | Familiar `find` syntax, readable errors |
| SH-2 | Script author | Uses the tool in build scripts and CI jobs to select files and act on them | Stable order, exact output bytes, meaningful exit statuses |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |
| SH-5 | Windows user | Works with deep source trees and protected system folders | No failures from long paths; graceful handling of access-denied folders |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to list every file and directory below a folder, including the folder itself, so I can see what a tree contains. | M | SH-1 |
| UR-02 | As a terminal user, I want to search several starting folders in one command, and the current folder when I name none. | M | SH-1 |
| UR-03 | As a terminal user, I want to select entries whose name matches a wildcard pattern such as `*.txt`, optionally ignoring letter case. | M | SH-1 |
| UR-04 | As a script author, I want to restrict results to regular files or to directories. | M | SH-2 |
| UR-05 | As a script author, I want to select files by size (larger than, smaller than, or exactly a given size) using familiar units. | S | SH-2 |
| UR-06 | As a script author, I want to select files by how many days ago they were last modified. | S | SH-2 |
| UR-07 | As a terminal user, I want to find empty files and empty directories, so I can clean them up. | S | SH-1 |
| UR-08 | As a script author, I want to limit how deep the search descends and to skip entries that are too shallow. | M | SH-2 |
| UR-09 | As a script author, I want to combine conditions with AND, OR, NOT, and parentheses, with the same meaning as POSIX `find`. | M | SH-2 |
| UR-10 | As a script author, I want to run a program for every matching entry, with the entry's path passed as an argument, without a shell interpreting it, and to use the program's success as a condition. | M | SH-2 |
| UR-11 | As a grader, I want results listed in one fixed order with `/` separators on every operating system, so a single set of expected outputs verifies all platforms. | M | SH-4 |
| UR-12 | As a script author, I want a missing or unreadable path to be reported without stopping the rest of the search, and to be told through the exit status that something failed. | M | SH-2, SH-5 |
| UR-13 | As a script author, I want a malformed search expression to be rejected with a precise message before any searching or command execution happens. | M | SH-2 |
| UR-14 | As a Windows user, I want trees whose paths exceed the traditional 260-character limit to be searched completely. | M | SH-5 |
| UR-15 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1 |
| UR-16 | As a terminal user, I want searches of large trees to start producing results immediately and to use little memory. | S | SH-1 |
| UR-17 | As a learner, I want the tool to follow the curriculum's common CLI conventions wherever its `find`-style syntax allows, so what I learned in earlier projects carries over. | M | SH-3 |
| UR-18 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-4 |

## 4. Usage scenarios

### 4.1 Survey a tree
A user types `dp-find src` and sees `src` followed by every entry beneath it, one path per line,
each directory's contents in a fixed alphabetical (byte-wise) order, with each directory listed
just before its contents. (UR-01, UR-11)

### 4.2 Find source files
A script runs `dp-find . -type f -name '*.c'` to collect every C source file below the current
directory. It receives paths such as `./lib/core.c`. (UR-02, UR-03, UR-04)

### 4.3 Clean up
A user runs `dp-find build -empty` to list empty files and directories, then
`dp-find build -type f -size +10M` to find unexpectedly large artifacts, and
`dp-find logs -type f -mtime +30` to find log files untouched for over a month.
(UR-05, UR-06, UR-07)

### 4.4 Shallow search
A user runs `dp-find . -mindepth 1 -maxdepth 1 -type d` to list just the immediate
subdirectories. (UR-08)

### 4.5 Combined conditions and commands
A CI job runs `dp-find docs -type f '(' -name '*.md' -o -name '*.txt' ')' -exec lint {} ';'` to
run a checker on every documentation file. The checker's own output appears in order with the
search. (UR-09, UR-10)

### 4.6 Something is wrong
A user mistypes a start folder: `dp-find srcc docs`. The tool reports that `srcc` does not exist,
still lists `docs`, and exits with status 1. Another user types `dp-find . -nme x`; the tool
explains that `-nme` is unknown, points to `--help`, lists nothing, and exits with status 2.
(UR-12, UR-13)

### 4.7 Deep trees and protected folders on Windows
A Windows user searches a dependency folder whose nested paths exceed 260 characters, and a
profile folder containing a subfolder they cannot open. Every reachable entry is listed; the
protected subfolder is reported as `Permission denied`, and the search continues. (UR-12, UR-14)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must never modify, create, or delete files itself (commands run through `-exec` may). |

## 6. User acceptance criteria

The users will accept `dp-find` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.
4. The long-path and permission-denied behaviors (scenario 4.7) are demonstrated by the
   implementer's own integration tests.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Start path | A folder or file named on the command line where the search begins |
| Entry | A file, directory, or other file system object reached during the search |
| Depth | How many levels below its start path an entry is; the start path has depth 0 |
| Glob | A wildcard pattern such as `*.txt` or `data-[0-9]?` |
| Expression | The conditions and actions written after the start paths |
| Exit status | The integer a process returns to its caller; 0 means success |

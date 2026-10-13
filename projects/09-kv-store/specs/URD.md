# User Requirements Document (URD) — dp-kv

| Field | Value |
| :-- | :-- |
| Document ID | URD-09 |
| Project | `09-kv-store` — Local Key-Value Storage Engine (CLI + API) |
| Product | `dp-kv` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-09), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-kv` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-09), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-kv` is a small, dependable key-value store that lives in a single local file. It is in the
spirit of an embedded database such as SQLite and of the string commands of Redis, but with a
deliberately tiny feature set: text values stored under short keys. What it lacks in features it
makes up for in engineering: every write is atomic and durable, several programs can use the
same store at the same time without losing updates, the file format is human-readable and
byte-for-byte identical across implementations and operating systems, and the same store can be
reached from the terminal or from other programs through a lightweight local HTTP API.

### 1.3 Scope
In scope: storing, retrieving, deleting, and listing text values by key from the command line;
exporting and importing the whole store; safe concurrent use by several processes; crash-safe
writes; a local HTTP/REST interface to the same store; help and version information; clear
errors.
Out of scope: binary values, numeric types, expiry/TTL, transactions spanning several keys,
replication, authentication, TLS, remote (network file system) stores, and storage of more data
than fits comfortably in memory.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Keeps notes, settings, or small records in a store from a shell on Linux, macOS, or Windows | Simple commands, helpful errors |
| SH-2 | Script author | Uses the store as shared state between shell scripts, cron jobs, and CI steps | Predictable output and exit statuses, safe concurrent use |
| SH-3 | Application developer | Reads and writes the store from another program over local HTTP | A small, well-defined JSON API |
| SH-4 | Operator | Backs up, inspects, versions, and restores store files | A readable, stable, diffable file format; no data loss |
| SH-5 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-6 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to store a text value under a key with one command, replacing any previous value, so I can save information quickly. | M | SH-1 |
| UR-02 | As a terminal user, I want to print the value stored under a key, so I can use it in the shell. | M | SH-1, SH-2 |
| UR-03 | As a terminal user, I want to delete a key, so stale information disappears. | M | SH-1 |
| UR-04 | As a script author, I want to list the keys, optionally only those that start with a given prefix, in a stable order, so I can iterate over related entries (for example every `user:` key). | M | SH-2 |
| UR-05 | As an operator, I want to export the whole store and to import an exported store, either merging it into an existing store or replacing the existing contents, so I can back up, restore, and combine stores. | M | SH-4 |
| UR-06 | As an operator, I want the store file to be plain, readable JSON whose exact bytes depend only on its contents, so I can inspect it, keep it under version control, and compare stores written by different implementations or on different operating systems. | M | SH-4, SH-6 |
| UR-07 | As an operator, I never want a crash, power failure, or full disk during a write to leave a damaged or half-written store; the store must hold either the old or the new contents. | M | SH-4 |
| UR-08 | As a script author, I want several programs to read and write the same store at the same time without any update being lost or any reader seeing a half-written store. | M | SH-2, SH-3 |
| UR-09 | As an application developer, I want to read, write, delete, and list keys over a local HTTP API with JSON bodies, so programs in any language can use the store without running the command-line tool. | S | SH-3 |
| UR-10 | As an application developer, I want the HTTP API to be reachable only from my own machine unless I explicitly choose otherwise, because it has no authentication. | M | SH-3, SH-4 |
| UR-11 | As a script author, I want to choose the store file for each command, or once for a whole session through an environment variable, with a sensible default. | M | SH-2 |
| UR-12 | As a script author, I want "key not found", invalid usage, and other failures to be reported with clear messages and distinct exit statuses, so my scripts can react to each. | M | SH-2 |
| UR-13 | As an operator, I want a damaged or foreign store file to be detected and reported, and never silently overwritten, so I do not lose data that could still be recovered. | M | SH-4 |
| UR-14 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-15 | As a terminal user, I want keys to be simple to type and values to be any text, including non-ASCII characters, spaces, and line breaks, preserved exactly. | M | SH-1 |
| UR-16 | As a grader, I want identical output bytes on Linux, macOS, and Windows, including line endings, so one set of expected outputs verifies every platform. | M | SH-6 |
| UR-17 | As a learner, I want the tool to follow the curriculum's common CLI conventions wherever they apply, so what I learned in earlier projects carries over. | M | SH-5 |
| UR-18 | As a script author, I want commands to finish quickly even when the store holds thousands of keys. | S | SH-2 |
| UR-19 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-6 |

## 4. Usage scenarios

### 4.1 Saving and reading a value
A user runs `dp-kv set editor vim` and then `dp-kv get editor`, which prints `vim`. The store
`kv.json` in the current directory is created by the first command. (UR-01, UR-02, UR-11)

### 4.2 Grouped keys
A script stores `user:1001` and `user:1002`, then runs `dp-kv list --prefix=user:` to print just
those two keys, in the same order every time. (UR-04)

### 4.3 Shared state between scripts
Two CI jobs that run at the same time each record their result with `dp-kv set`. Afterwards both
results are in the store; neither overwrote the other's update. (UR-08)

### 4.4 Backup and restore
An operator runs `dp-kv export > backup.json` every night and commits the file to version
control; the diff shows exactly the keys that changed. After a mistake, `dp-kv import --replace
backup.json` restores the store. (UR-05, UR-06)

### 4.5 A program uses the HTTP API
A developer starts `dp-kv serve --port=0`, reads the chosen port from the line
`dp-kv: listening on http://127.0.0.1:PORT`, and lets a web dashboard `PUT` and `GET` keys as
JSON. A colleague's machine on the same network cannot connect, because the server listens on
the loopback address only. Meanwhile the CLI keeps working on the same store. (UR-09, UR-10)

### 4.6 A crash
The machine loses power while a script is writing to the store. After the reboot, the store
contains either the value before or the value after that write — never a truncated file.
(UR-07)

### 4.7 Mistakes
A user types `dp-kv get colour` for a key that does not exist and sees
`dp-kv: key not found: colour` with exit status 1. Typing `dp-kv fetch colour` instead prints
`dp-kv: unknown command 'fetch'`, a pointer to `--help`, and exits with status 2. A store file
that someone edited by hand and broke is reported as `not a valid dp-kv store file`, and
`dp-kv set` refuses to overwrite it. (UR-12, UR-13)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require elevated privileges, configuration files, or any network access other than the local socket that `serve` listens on. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | The store must be a local file; correctness on network file systems is not required. |
| UC-6 | Must work with the operating system's native file-locking facility on each platform; no lock server or daemon may be required. |

## 6. User acceptance criteria

The users will accept `dp-kv` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The implementer's integration tests for concurrency, crash safety, locking, and the HTTP API
   (SRS-09 section 9) pass on all three platforms.
4. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Store | The single file that holds all keys and values |
| Key | The name under which a value is stored, for example `user:1001` |
| Value | The text stored under a key |
| Export / import | Writing the whole store out as a document / reading such a document back in |
| Merge | Import mode in which imported keys are added to (or overwrite) the existing ones |
| Replace | Import mode in which the store's contents become exactly the imported keys |
| Atomic write | A write whose result is all-or-nothing, even if the process or machine fails midway |
| Lock | An operating-system mechanism that stops two processes from changing the store at the same time |
| Loopback | The network address (`127.0.0.1`) that only programs on the same machine can reach |
| Exit status | The integer a process returns to its caller; 0 means success |

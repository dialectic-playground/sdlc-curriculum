# Project 40 — Direct-Access Hashed Relative File Storage Engine (`dp-relfile`)

> Keep records in a binary file of 100 fixed-size slots, placed by hashing their keys — the
> way a professional storage engine would: a byte-exact file format, linear probing with
> wrap-around and tombstones, duplicate and full-file detection, rejection of damaged files,
> scriptable commands alongside the classic menu, and identical files on Linux, macOS, and
> Windows.

## Purpose

Project 40 is adapted from §8.8 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a menu-driven program that adds, finds, and removes records in a *relative file*, where the
position of each 35-byte record is computed from its 4-digit key (key mod 97) and collisions
are resolved by linear probing. It is a hash table that lives on disk. The project teaches
direct-access file I/O — positioning a file at a computed byte offset and reading or writing
one record in place — together with open addressing, the tombstones that keep probe chains
intact after a removal, and the bounded probing that keeps a saturated table from looping
forever. Around that core it adds what a real tool needs: single-operation commands for
scripts, a `slots` command to inspect the layout, validation of every key, datum, and file, and
exact diagnostics.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| The textbook's file format: 100 slots × 35 bytes (status, 4-digit key, 30 bytes of data) | Other sizes, layouts, or growable files |
| Auto-initialization of a missing file to 3500 bytes of free slots | Re-initializing or repairing an existing file |
| Home slot key mod 97; linear probing with wrap-around; tombstones reused by later adds | Other hash functions, rehashing, compaction |
| `add`, `find`, `remove`, and `slots` commands; `-f`/`--file` (default `relative.dat`) | Updating a record in place, listing in key order |
| The numbered menu dialog from standard input, with optional prompts (`-p`, `--prompt`) | Full-screen or line-editing interfaces |
| Duplicate-key and full-file detection; validation of keys and data | Non-ASCII data |
| Rejection of a file of the wrong size or with an invalid record | Locking, concurrent access, crash-safe transactions |
| CONV-34 diagnostics for malformed dialog input; CONV-16 file errors; `--help`, `--version` | Configuration files, environment variables |

## Learning objectives

1. Read and write single fixed-size records at computed byte offsets in a binary file, without
   loading or rewriting the whole file (FR-11, NFR-02).
2. Implement open addressing with linear probing and wrap-around, and explain why removal must
   leave a tombstone rather than a free slot (FR-05, FR-08).
3. Make insertion correct in the presence of tombstones — no duplicate keys — and make probing
   terminate in a table with no free slot (FR-05, FR-06).
4. Define and validate a binary file format, so that a damaged file is rejected before it is
   used (FR-02).
5. Offer the same operations through two front ends, a command line and a menu dialog, built on
   one set of operation functions (FR-10, FR-12, NFR-05).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-19, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Files shared by both suites: `people.dat` (a valid relative file with a collision chain and a tombstone), `short.dat` and `badstatus.dat` (damaged relative files), and `session.txt` (a menu session) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.
Most tests have several steps: a later step runs `dp-relfile` again in the same directory, so
`find` and `slots` show what earlier steps wrote to the relative file.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-relfile`, with unit tests and the file-inspecting integration tests
   that the SRS verification section calls for.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-relfile into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

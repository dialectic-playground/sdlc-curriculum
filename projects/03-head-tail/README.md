# Project 03 — Stream Slicing Utility (`dp-head`, `dp-tail`)

> Print the beginning or the end of files and streams, by lines or by bytes, and follow growing
> files, with memory use that stays small and fixed even on multi-gigabyte inputs, and
> byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 03 is the first project with two cooperating tools and the first where *how* data is
read matters as much as *what* is printed. Taking the last ten lines of a 40 GB log by reading
it from the start is correct but useless; reading it into memory is worse. You will design
slicing strategies for seekable files (seek, and scan backwards in fixed-size blocks) and for
non-seekable streams (bounded ring buffers), share the common logic between the two tools, and
make an inherently endless feature, `tail -f`, deterministic enough to test.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| First / last N lines or bytes (`-n`, `-c`), defaults of 10 lines | Obsolete forms `head -5`, `tail +5` |
| All but the last N (`dp-head -n -N`, `-c -N`) | NUL-delimited lines (`-z`) |
| From line / byte N onward (`dp-tail -n +N`, `-c +N`) | Follow by name, `--retry`, `--pid`, `-F` |
| `K`/`M`/`G` count suffixes | Other GNU suffixes (`b`, `kB`, `KiB`, …) |
| File headers with `-q` / `-v`, several files, standard input | inotify/kqueue change notification |
| Polling follow mode (`-f`, `-s`, `--max-polls`) | Editing or truncating files |
| CONV-16 file errors that do not stop processing | Locale-dependent behavior |

## Learning objectives

1. Implement slicing with memory bounded independently of input size, choosing between seeking
   and streaming at run time by inspecting what kind of input you were given.
2. Read a file backwards in fixed-size blocks and get every boundary case right: an LF exactly
   at a block edge, lines longer than a block, a final line without LF, an empty file.
3. Handle 64-bit offsets and counts portably (files larger than 4 GiB on every OS).
4. Factor logic shared by two executables (number parsing, headers, error handling) into one
   tested unit.
5. Make a time-based feature (polling follow mode) deterministic and testable.
6. Pass binary data through untouched on Windows (no CRLF translation in either direction).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-18) |
| `specs/SRS.md` | System requirements (FR-01 … FR-16, NFR-01 … NFR-10) |
| `specs/user-manual.md` | Complete user manual, including both normative help texts |
| `tests/fixtures/` | Input files shared by both suites |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md` covering both tools.
2. Implementations of `dp-head` and `dp-tail` sharing their common code, with unit tests that
   exercise block-boundary cases using a small configurable block size (NFR-08).
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain, building and
   installing both executables (see `assignment/src/README.md`).
4. Evidence for NFR-02/NFR-03: a short demonstration (recorded in the master test plan) of
   `dp-tail -n 10` on a file of at least 4 GiB, with its run time and peak memory.

## Quick start

```sh
make all            # build dp-head and dp-tail into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, the large-file demonstration meets NFR-02 and NFR-03, and
every RTM row is *Verified*.

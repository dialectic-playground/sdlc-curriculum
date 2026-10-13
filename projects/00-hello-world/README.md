# Project 00 — Standard Terminal Hello World (`dp-hello`)

> Print `Hello, World!` the way a professional command-line tool would: with option parsing,
> input validation, exact diagnostics, correct exit statuses, and byte-identical output on
> Linux, macOS, and Windows.

## Purpose

Project 00 establishes the conventions every later project relies on: the shared CLI conventions
(`shared/CLI-CONVENTIONS.md`), the universal Makefile contract, the black-box test harness, and
the white-box engineering deliverables. The tool is deliberately small, so that all the effort
goes into *engineering discipline* rather than algorithms.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Default and named greetings (`--name`) | Localization / translated greetings |
| Repeated greetings (`--count`, 1–1000) | Colors, interactive input |
| `--help`, `--version` | Configuration files, environment variables |
| CONV-13 usage errors with exit status 2 | Reading stdin or files |

## Learning objectives

1. Parse short, long, bundled, and attached-value options without a third-party library
   (CONV-07 … CONV-12).
2. Validate input and report errors with *exact*, specified messages and exit statuses.
3. Produce identical bytes on every OS, including LF-only output on Windows (CONV-03).
4. Wire a language toolchain into the universal `Makefile` contract.
5. Practise the full white-box lifecycle on a small problem: HLD → LLD → code → RTM → test plan.

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-12) |
| `specs/SRS.md` | System requirements (FR-01 … FR-11, NFR-01 … NFR-07) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-hello`, with unit tests.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-hello into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

# Project 09 — Local Key-Value Storage Engine (CLI + API) (`dp-kv`)

> Build a tiny embedded database in the spirit of SQLite and a subset of Redis: text values
> under keys in one local JSON file, with atomic and durable writes, cross-process file locking,
> a byte-exact canonical file format, and a lightweight local HTTP/REST API over the same store.

## Purpose

Earlier projects read input and wrote output. Project 09 owns *persistent state* that several
processes share. The algorithms are simple; the engineering is not: a correct store must never
lose an update when two writers race, never expose a half-written file to a reader, never be
left damaged by a crash, and must behave the same on Linux, macOS, and Windows even though their
file-locking and rename semantics differ (`flock(2)` versus `LockFileEx`, POSIX `rename` versus
`MoveFileExW`). The project also introduces a second front end — an HTTP server — on the same
storage engine, which forces a clean separation between the engine and its interfaces.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| `set`, `get`, `del`, `list [--prefix]` on a single JSON store file | Binary or typed values, TTL/expiry, multi-key transactions |
| `export` and `import` (merge or `--replace`, file or stdin) | Replication, remote stores, network file systems |
| Store selection via `--store`, `DP_KV_STORE`, or `./kv.json` | Configuration files |
| Byte-exact canonical JSON store format; strict validation of stores and imports | Repairing damaged stores automatically |
| Shared/exclusive locking on `PATH.lock` (flock / LockFileEx) with a 5 s timeout | Lock servers, daemons |
| Atomic durable replacement (temp file + fsync + rename) | Write-ahead logs, partial updates |
| `serve`: HTTP/1.x JSON API on loopback by default (`/v1/keys`, `/v1/health`) | TLS, authentication, keep-alive, HTTP/2 |
| `--help`, `--version`, exact diagnostics and exit statuses | Localization, colors |

## Learning objectives

1. Design a subcommand-style command line (global options, a command word, command options) on
   top of the shared CLI conventions.
2. Specify and implement a canonical serialization so that independent implementations write
   byte-identical files, and a strict validator that rejects everything else.
3. Make updates crash-safe with the temp-file + fsync + atomic-rename pattern, and explain why
   writing in place is unsafe.
4. Coordinate concurrent processes with advisory file locks, and map one protocol onto two
   platform primitives: `flock(2)` on POSIX and `LockFileEx` on Windows (and learn why `fcntl`
   record locks are the wrong tool here).
5. Wrap a storage engine in a minimal HTTP/REST API with exact status codes, JSON bodies, and
   error precedence, and keep it safe by binding to loopback.
6. Write integration tests for behavior a black-box harness cannot observe: races, crashes,
   lock contention, and a running server.

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-19) |
| `specs/SRS.md` | System requirements (FR-01 … FR-33, NFR-01 … NFR-10), store format, HTTP API, required integration tests IT-01 … IT-08 |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Shared fixtures: canonical store `data.json`, import document `import.json`, damaged store `corrupt.json` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`. The master test plan
   MUST include the integration tests IT-01 … IT-08 of SRS section 9.
2. An implementation of `dp-kv`, with unit tests (document codec and validator, key/value
   rules, argument parsing) and the integration tests, runnable on all three operating systems.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-kv into BIN_DIR
make test           # unit + integration tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

Then try it:

```sh
dp-kv set greeting 'Hello, World!'
dp-kv get greeting
dp-kv export
dp-kv serve --port=0      # in another terminal: curl http://127.0.0.1:PORT/v1/keys
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI — including the integration tests for concurrency, crash safety, locking, and the
HTTP API — `make lint` is clean, and every RTM row is *Verified*.

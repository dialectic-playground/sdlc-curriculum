# Project 41 — 1-Nearest Neighbor Film Success Classifier (`dp-films`)

> Learn from a sample set of past films, then classify new films as hits or flops by their
> nearest neighbor — the way a professional tool would: a validated sample set, reproducible
> floating-point distances, an exact tie-breaking rule, optional prompts on standard error,
> exact diagnostics, and byte-identical answers on Linux, macOS, and Windows.

## Purpose

Project 41 is adapted from §9.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.
A film is described by two features: the percentage of hits among the earlier films of its
director, and the same percentage for the leading members of its cast. A sample set of films
whose outcome is known (`films.dat`, 20 films) is the training data. Each new film is
classified with the **1-nearest-neighbor rule**: it gets the outcome of the sample film at the
smallest Euclidean distance, compared as squared distances so no square root is needed.

The algorithm is a few lines. The engineering is in the details that make answers reproducible:
validating the sample set before anything is classified, defining the arithmetic exactly (two
distances that are equal in decimal can differ in binary floating point), breaking ties by a
stated rule, and answering each query as soon as it has been typed.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Sample set from `films.dat`, or the file named by `-s`/`--sample` (`-` is standard input) | Several sample sets, *k* > 1 neighbors, weighting, normalization |
| 1 to 100 sample films; percentages 0 … 100; outcome codes 0 and 1 | Other features, other outcome classes |
| Queries (two percentages each) from standard input or one FILE operand, until the end of the input | Interactive editing, a file-name dialog |
| Squared Euclidean distance in IEEE 754 binary64; the first nearest sample film wins | Exact decimal or extended-precision arithmetic |
| One verdict line per query, written as soon as the query is complete | Distances or neighbors in the output |
| Prompts on standard error with `-p`/`--prompt` (CONV-36) | Prompts on standard output |
| CRLF input, trailing Ctrl-Z (CONV-37), data diagnostics with line numbers (CONV-34) | Configuration files, environment variables |

## Learning objectives

1. Implement the 1-nearest-neighbor rule with squared distances and a deterministic
   tie-breaking rule (FR-05).
2. Specify and reproduce floating-point arithmetic exactly: decimal-to-binary conversion, the
   order of operations, and the absence of fused multiply-add (FR-05, NFR-02).
3. Load and validate a whole training set before serving any query, with precise diagnostics
   for every kind of bad record (FR-02).
4. Serve an interactive query loop that streams answers and prompts on standard error without
   changing standard output (FR-07, FR-08).
5. Map a textbook keyboard dialog onto a command-line interface (§2.5 of the SRS).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-15, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Inputs shared by both suites: `films.dat` (from the textbook's companion disk), `readme.txt`, `queries.txt`, `pair.dat`, `center.txt`, `bad-query.txt`, `bad-code.dat` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

`films.dat` is the textbook's sample set, byte for byte: two blank lines, then 20 films of
three values each. Do not modify it.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-films`, with unit tests.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-films into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

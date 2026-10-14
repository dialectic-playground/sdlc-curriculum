# Project 48 — A* Heuristic Graph Search for European Cities (`dp-astar`)

> Find the shortest road route from any of 19 European cities to Vienna with the A* search,
> reading the textbook's own MS-DOS data files — tabs, wrapped matrix rows, one-way roads,
> Ctrl-Z padding and all — with every step of OPEN/CLOSED bookkeeping, reopening, and
> tie-breaking specified so that every implementation finds the same route, and can show
> the same trace, on Linux, macOS, and Windows.

## Purpose

Project 48 is adapted from §10.9 of Johnsonbaugh & Kalin, *Applications Programming in ANSI
C*. The tool reads 19 cities with straight-line estimates of their distance to Vienna from
`names.dat`, and a 19 × 19 matrix of road distances from `distance.dat`, in which 1000 means
"no road". It asks for a start city and searches with A*: it always expands the open city
with the smallest *f* = *g* + *h*, moves expanded cities to CLOSED, and reopens a closed city
when a shorter route to it turns up. It then prints the route and its length. The data are
less tidy than the section's description suggests: the matrix is not symmetric (Vienna has
no outgoing roads at all, and a few other roads are one-way), and five of the estimates are
larger than the true remaining distance. The specification therefore treats each entry as a
one-way road and defines the search exactly, and the reference model's results replace the
description's example distances, which are wrong.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| `names.dat` and `distance.dat` by default; `-n`, `--names` and `-d`, `--distances` to choose others | Several data sets in one run; editing the data |
| Up to 1000 cities; every matrix entry a one-way road unless it is exactly 1000 | Symmetrizing the matrix; coordinates or computed estimates |
| A* with OPEN/CLOSED, reopening, and lowest-index tie-breaking | Other search algorithms; several start cities per run |
| Start city as an operand or read from standard input, matched without regard to ASCII case | Fuzzy or prefix matching of city names |
| Goal Vienna by default; `-g`, `--goal` for another city of the data | Estimates recomputed for another goal |
| Route with ` -> ` and the total distance; `No path` when the goal cannot be reached | Turn-by-turn listings, alternative routes |
| `-t`, `--trace`: every OPEN/CLOSED step of the search | Timing measurements |
| `-p`, `--prompt` with the textbook's prompt on standard error (CONV-36) | Prompts on standard output |
| Tabs, wrapped rows, CRLF, trailing Ctrl-Z (CONV-37); CONV-34 data diagnostics | Repairing invalid data |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Implement A* with explicit OPEN and CLOSED sets, path relaxation, reopening, and
   back-pointer traceback (FR-08, FR-09).
2. Make a search deterministic by specifying the selection rule completely, including ties,
   and verify it through a trace (FR-08, FR-11).
3. Understand what an admissible heuristic guarantees, and observe that the textbook's
   estimates are not all admissible (FR-08, SRS §2.5).
4. Parse legacy data files whose layout (tabs, rows wrapped over lines, Ctrl-Z padding) is
   irrelevant once they are read as tokens, and validate them completely before acting
   (FR-01 … FR-03).
5. Match names case-insensitively in a way that does not depend on the locale (FR-05,
   NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-15) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Files shared by both suites: `names.dat` and `distance.dat` (from the textbook's companion disk), `short.dat`, `start.txt`, `reopen-names.dat`, `reopen-dist.dat`, `tie-names.dat`, `tie-dist.dat` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

`names.dat` and `distance.dat` are byte-for-byte copies of the companion-disk files,
including their tabs and trailing Ctrl-Z bytes; do not "clean them up". The other fixtures
were written for this project: small data sets that make reopening and tie-breaking
visible, and inputs for the start city.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-astar`, with unit tests — including the route and distance from
   every one of the 19 textbook cities, and the reopening and tie-breaking data sets.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-astar into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

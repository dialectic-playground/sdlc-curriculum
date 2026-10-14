# Project 47 — Graph Breadth-First Search: Adjacency Matrix vs. Adjacency List (`dp-bfs-adj`, `dp-bfs-link`)

> Search the same graph breadth-first with two different representations, an adjacency matrix
> and adjacency lists built by insertion at the head, and see that both are correct and yet
> visit the vertices in a different order — an order the specification pins down to the
> byte, so that every implementation, in every language and on every operating system,
> prints exactly the same lines.

## Purpose

Project 47 is adapted from §10.8 of Johnsonbaugh & Kalin, *Applications Programming in ANSI
C*. Its two tools search a graph whose vertices are the seven deadly sins, starting at Anger,
and print `X has been visited.` for each vertex in the order it is discovered. `dp-bfs-adj`
holds the graph as a matrix and examines a vertex's neighbors in ascending order of vertex
number; `dp-bfs-link` holds it as linked adjacency lists, each built by inserting new
neighbors at the head, and so examines them in the reverse of the order in which the edges
were listed. Both orders are legitimate breadth-first searches; the difference between them
is the lesson. Both tools search a built-in graph by default and can read any other graph
from a fully specified file format, which is validated completely before anything is printed.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| The built-in seven-sins graph (7 vertices, 9 undirected edges) | Directed or weighted graphs |
| Graphs read from a file or standard input (`-g`, `--graph`): 1–1000 vertices, simple undirected edges | Several graph files; vertex names with spaces |
| A start vertex chosen with `-s`, `--start` (default 0) | Depth-first search, shortest-path output, levels |
| Neighbor order fixed by the representation: matrix ascending, lists by head insertion | Any other neighbor order (sorted lists, hash sets) |
| Only the start vertex's connected component is visited | Reporting unreachable vertices |
| Whole-file validation before output; CONV-34 data diagnostics; CRLF and a trailing Ctrl-Z | Partial output after a data error; prompts |
| `--help`, `--version`, CONV-13 usage errors for both tools | Configuration files, environment variables |

## Learning objectives

1. Build an adjacency matrix and adjacency lists from the same edge list, and compare their
   memory use and the cost of examining a vertex's neighbors (FR-06, FR-07, NFR-03).
2. Implement breadth-first search with a FIFO queue and a visited set, so that every reachable
   vertex is visited exactly once, even in a graph with cycles (FR-05).
3. Recognize that a traversal order is a consequence of the data structure, and specify it
   precisely enough that independent implementations agree byte for byte (FR-06, FR-07,
   NFR-02).
4. Parse a small token-based file format completely, with a precise diagnostic for every way
   it can be wrong, before producing any output (FR-02 … FR-04).
5. Share input handling and the search between two tools, so that they differ only in the
   representation (NFR-05).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-13, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual for both tools, including both normative help texts |
| `tests/fixtures/` | Graph files shared by both suites: `sins.txt` (the built-in graph written as a file), `order.txt`, `islands.txt`, `bad-edge.txt` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file, and its description does not list every
edge of the graph; the built-in edge set (SRS FR-01) was designed for this project to be
consistent with it. Every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the two graph representations and the components the tools share.
2. Implementations of `dp-bfs-adj` and `dp-bfs-link`, with unit tests — including the
   neighbor order of every vertex of the built-in graph in both representations.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-bfs-adj and dp-bfs-link into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-bfs-adj, dp-bfs-link](#software-requirements-specification-srs--dp-bfs-adj-dp-bfs-link)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
    - [2.5 Relationship to the textbook program (informative)](#25-relationship-to-the-textbook-program-informative)
    - [2.6 Relationship to CLI-CONV](#26-relationship-to-cli-conv)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
    - [4.1 Graph input](#41-graph-input)
    - [4.2 Search and output](#42-search-and-output)
    - [4.3 Command line](#43-command-line)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-bfs-adj, dp-bfs-link

| Field                     | Value                                                                      |
| :------------------------ | :------------------------------------------------------------------------- |
| Document ID               | SRS-47                                                                     |
| Project                   | `47-bfs` — Graph Breadth-First Search: Adjacency Matrix vs. Adjacency List |
| Products                  | `dp-bfs-adj`, `dp-bfs-link` (canonical names)                              |
| Version                   | 1.0.0                                                                      |
| Status                    | Approved (pre-written by the curriculum)                                   |
| Parent document           | `URD.md` (URD-47)                                                          |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                               |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                                       |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-bfs-adj` and `dp-bfs-link`. It
is complete and precise enough that independent implementations in any programming language
produce **byte-identical** output for every invocation. It is the authoritative source for
design (HLD/LLD), testing, and grading.

### 1.2 Scope

Both tools search an undirected graph breadth-first from a start vertex and write one line
per visited vertex, in discovery order. The graph is a built-in graph of seven vertices (the
seven deadly sins) or is read from a file or standard input. `dp-bfs-adj` represents the
graph as an adjacency matrix and `dp-bfs-link` as adjacency lists built by insertion at the
head; the representation determines the order in which a vertex's neighbors are examined, and
therefore the output order. Everything else is the same for both tools.

### 1.3 Definitions

| Term                     | Definition                                                                                                                                                                         |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                       | The line-feed byte, `0x0A`                                                                                                                                                         |
| _the tool_               | Either `dp-bfs-adj` or `dp-bfs-link`; `<tool>` in a message is the canonical name of the tool that writes it                                                                       |
| GRAPH                    | The value of `-g`/`--graph`, if given                                                                                                                                              |
| START                    | The value of `-s`/`--start`, or `0` if neither is given                                                                                                                            |
| Input                    | The byte sequence read from the file GRAPH, or from standard input when GRAPH is `-`                                                                                               |
| Source                   | The name used for the input in diagnostics: GRAPH exactly as given (so `-` for standard input)                                                                                     |
| Token, line number       | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1                  |
| _n_                      | The number of vertices of the graph, 1 ≤ _n_ ≤ 1000                                                                                                                                |
| Vertex                   | An integer 0 … _n_ − 1; vertex _i_ has the name _name_(_i_), a non-empty byte string without whitespace                                                                            |
| Edge list                | The sequence *e*₁ … *e*ₘ of edges in the order the graph description lists them; edge *e*ₖ is an ordered pair (*u*ₖ, *v*ₖ) of different vertices and joins them in both directions |
| Neighbors of _x_         | The vertices _y_ such that some edge is (_x_, _y_) or (_y_, _x_)                                                                                                                   |
| Neighbor sequence of _x_ | The neighbors of _x_ in the order in which the tool examines them (FR-06, FR-07)                                                                                                   |
| Visit line               | The bytes _name_(_x_) followed by `s been visited.` and LF                                                                                                                         |

### 1.4 References

- URD-47: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains both normative help texts)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §10.8 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-bfs-adj` and `dp-bfs-link` are standalone executables. Their interfaces are the command
line, the graph file or standard input, standard output, standard error, and the exit status.
They belong to the curriculum's applications-programming track (Projects 11–52) and adapt
§10.8 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. They complement the
queues of `dp-queue1` and `dp-queue2` (Project 45), which breadth-first search uses, and the
informed search of `dp-astar` (Project 48).

### 2.2 Product functions

1. Provide the built-in seven-sins graph, or read a graph from a file or standard input.
2. Validate the whole graph description before any output is written.
3. Represent the graph as an adjacency matrix (`dp-bfs-adj`) or as adjacency lists built by
   head insertion (`dp-bfs-link`).
4. Search the graph breadth-first from the start vertex and write each vertex as it is
   discovered.
5. Report unreadable input, invalid graph descriptions, and an out-of-range start vertex.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- `dp-bfs-adj` MUST store the graph as an _n_ × _n_ adjacency matrix and `dp-bfs-link` as one
  linked list of neighbors per vertex (NFR-05). The orders of FR-06 and FR-07 are the
  natural consequences of those representations; an implementation MUST NOT obtain them from
  a hash-based set or map, whose iteration order is unspecified.

### 2.4 Assumptions

- The graph description may contain any bytes; only the tokens that FR-03 allows are
  accepted.
- Vertex names are labels only; two vertices may have the same name.

### 2.5 Relationship to the textbook program (informative)

The textbook programs of §10.8 build a fixed graph of seven vertices — 0 Anger, 1 Lust,
2 Envy, 3 Gluttony, 4 Pride, 5 Sloth, 6 Covetousness — once as an adjacency matrix and once
as adjacency lists, search it breadth-first from Anger with a queue, and print
`<sin> has been visited.` for each vertex when it is discovered. The tools keep:

- the seven vertex names and their numbering, Anger as the default start vertex, and the
  visit line wording exactly, one line per vertex, with no header or summary;
- breadth-first search with a FIFO queue, marking a vertex visited (and printing it) when it
  is enqueued, so each vertex is printed exactly once;
- the two representations and the neighbor order each naturally produces: ascending vertex
  number for a matrix row; head insertion for linked lists.

It changes or adds the following, for the reasons given:

- **The built-in edge set is designed here.** The section's description does not list the
  edges. It states only that Anger is joined to Lust, Envy, and Gluttony, that Pride and Sloth
  are at distance 2 from Anger, and that Covetousness is at distance 3. FR-01 fixes nine
  edges consistent with all of that, including two cycles (Anger–Lust–Envy and
  Lust–Pride–Envy), so that the visited guard matters, and chosen so that the two tools
  print different orders.
- **The neighbor order of the lists is specified.** The order of linked lists depends on the
  order in which edges are inserted. FR-07 fixes it as the order of the edge list, with each
  edge inserting at the head of both endpoints' lists, so that the difference from the matrix
  order is deterministic and testable.
- **Graphs can be read from a file** (`-g`, `--graph`), in the format of FR-03, and the start
  vertex can be chosen (`-s`, `--start`). This lets the tests, and instructors, vary the
  graph; the built-in graph is exactly the graph that `tests/fixtures/sins.txt` describes.
- **Disconnected graphs** are defined (FR-05): only the start vertex's component is visited,
  and unreachable vertices are not mentioned, as in the textbook's loop.
- **Invalid graph descriptions are diagnosed** (FR-04) with CONV-34 messages before any
  output; self-loops and repeated edges are rejected, because a repeated edge would put a
  neighbor in a linked list twice and make the two representations disagree about the graph.
- **No prompts.** The textbook programs read no input, so the tools have no prompts and do
  not accept `-p`.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the graph description is read as tokens; line numbers), CONV-33 (the
counts and vertex numbers use the _integer_ grammar, further restricted as FR-03 states),
CONV-34 (data diagnostics, with the standard messages `invalid integer`, `value out of
range`, and `unexpected end of input`, and the further messages `self-loop`,
`duplicate edge`, and `unexpected token`; no visit line has been written when one is
reported), and CONV-37 (the graph description is _text data_). CONV-35 does not apply,
because no real number is written; CONV-36 does not apply, because the tools have no prompts;
CONV-38 does not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12,
diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard
input is read only when GRAPH is `-` (CONV-26). Vertex names are copied from the input to the
output byte for byte (CONV-04).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-bfs-adj  [-g FILE | --graph=FILE] [-s VERTEX | --start=VERTEX]
dp-bfs-link [-g FILE | --graph=FILE] [-s VERTEX | --start=VERTEX]
dp-bfs-adj  --help | --version
dp-bfs-link --help | --version
```

### 3.2 Options

Both tools have the same options.

| Short | Long        | Argument          | Default            | Description                                                         |
| :---- | :---------- | :---------------- | :----------------- | :------------------------------------------------------------------ |
| `-g`  | `--graph`   | FILE (required)   | the built-in graph | Read the graph description from FILE; `-` is standard input (FR-02) |
| `-s`  | `--start`   | VERTEX (required) | `0`                | Start the search at vertex VERTEX (FR-09)                           |
| —     | `--help`    | none              | —                  | Print the help text and exit 0                                      |
| —     | `--version` | none              | —                  | Print the version line and exit 0                                   |

Option syntax (`-gFILE`, `--graph FILE`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. If an option is repeated, the last occurrence wins (CONV-11); only the winning value
is checked. FILE may begin with `-` when it is attached (`--graph=-x`, `-g-x`) or supplied as
the next token. An empty FILE is an invalid option value. VERTEX MUST consist only of the
ASCII digits `0`–`9` (leading zeros allowed) and its value MUST lie in 0 … 999; any other
VERTEX, including an empty one or one with a sign, is an invalid option value (FR-13).

### 3.3 Operands

Neither tool accepts operands. The graph file is given with `-g`.

### 3.4 Standard input

Read only when GRAPH is `-` (FR-02), to its end, as raw bytes; no newline translation of any
kind is performed on any platform.

### 3.5 Standard output

The visit lines (FR-08), in discovery order; nothing else. Nothing is written if any error
is detected. On a usage error, or when `--help` / `--version` is handled, the output is as
specified by FR-11 … FR-13 instead.

### 3.6 Standard error

Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition                                                                                                                                                            |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The search completed and its visit lines were written, or `--help` / `--version` was handled                                                                         |
| 1      | The graph file could not be read (FR-10), the graph description is invalid (FR-04), the start vertex does not exist (FR-09), or standard output could not be written |
| 2      | Usage error (FR-13)                                                                                                                                                  |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are public fixture files in
`tests/fixtures/`: `sins.txt` is the built-in graph of FR-01 written in the format of FR-03;
`order.txt` has 6 vertices `North East South West Up Down` and the edge list (0, 3), (0, 1),
(0, 2), (1, 4), (3, 4), (2, 5); `islands.txt` has 5 vertices `Ada Babbage Church Dijkstra
Euler` and the edge list (0, 1), (2, 3); `bad-edge.txt` has the 7 sins, the edge count 3, and
the edges `0 1`, `0 2`, and `3 7` on lines 4, 5, and 6. A visit order written as a list of
names stands for the corresponding visit lines.

### 4.1 Graph input

**FR-01: Built-in graph.**
Without `-g`/`--graph`, the tool MUST search the built-in graph: _n_ = 7, with the names
`Anger`, `Lust`, `Envy`, `Gluttony`, `Pride`, `Sloth`, `Covetousness` for vertices 0 … 6, and
the edge list, in this order,
(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 4), (3, 5), (4, 6), (5, 6).
That is, Anger–Lust, Anger–Envy, Anger–Gluttony, Lust–Envy, Lust–Pride, Envy–Pride,
Gluttony–Sloth, Pride–Covetousness, Sloth–Covetousness. The built-in graph behaves exactly
as if this description were read from a file (FR-03); no file and no standard input is read.
_AC:_ `dp-bfs-adj` and `dp-bfs-adj --graph=sins.txt` write the same bytes; so do
`dp-bfs-link` and `dp-bfs-link -g sins.txt`. _(UR-01)_

**FR-02: Graph file.**
If GRAPH is `-`, the tool MUST read standard input to its end. Otherwise it MUST open the file
GRAPH (a path relative to the current directory unless absolute) and read it to its end as raw
bytes. The whole input is read and validated (FR-03, FR-04) before any visit line is written.
_AC:_ `dp-bfs-link -g - < order.txt` writes the same bytes as `dp-bfs-link -g order.txt`.
_(UR-04)_

**FR-03: Graph description format.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32); line
structure has no meaning, so CRLF input reads exactly like LF input, and any mixture of
whitespace may separate tokens. The tokens MUST be, in this order:

1. _n_: a valid _integer_ (CONV-33) with 1 ≤ _n_ ≤ 1000;
2. _n_ name tokens, _name_(0) … _name_(_n_ − 1): any tokens, used as bytes;
3. _m_: a valid _integer_ with 0 ≤ _m_ ≤ _n_(_n_ − 1)/2;
4. _m_ pairs of tokens *u*ₖ *v*ₖ (_k_ = 1 … _m_), each a valid _integer_ with
   0 ≤ *u*ₖ, *v*ₖ ≤ _n_ − 1, such that *u*ₖ ≠ *v*ₖ and no earlier pair joins the same two
   vertices in either order;

and nothing else. Each pair is the edge (*u*ₖ, *v*ₖ) of the edge list, in input order. A sign
and leading zeros are allowed in every integer (`+2`, `007`). The format is illustrated by
`sins.txt`:

```text
7
Anger Lust Envy Gluttony Pride Sloth Covetousness
9
0 1
0 2
0 3
1 2
1 4
2 4
3 5
4 6
5 6
```

_AC:_ `order.txt`, with three edges per line and two spaces between pairs, is accepted;
`dp-bfs-adj -g order.txt` writes the visit order North, East, South, West, Up, Down.
A description with CRLF line endings and a trailing run of `0x1A` bytes reads like the same
description with LF endings. _(UR-04, UR-09)_

**FR-04: Invalid graph descriptions.**
The tokens are checked in input order, and the first violation of FR-03 MUST be reported as
`<tool>: <source>:<line>: <message>` (CONV-34), after which the tool exits with status 1
without writing any visit line. `<source>` is as defined in section 1.3. `<line>` and
`<message>` are:

| Violation                                                                      | `<line>`                 | `<message>`               |
| :----------------------------------------------------------------------------- | :----------------------- | :------------------------ |
| _n_, _m_, or a vertex token _K_ is not a valid _integer_                       | line of _K_              | `invalid integer 'K'`     |
| _n_, _m_, or a vertex token _K_ is a valid _integer_ outside its range (FR-03) | line of _K_              | `value out of range 'K'`  |
| The input ends before all the tokens of FR-03 have been read                   | end-of-input line number | `unexpected end of input` |
| The pair _U_ _V_ has *u*ₖ = *v*ₖ                                               | line of _V_              | `self-loop 'U V'`         |
| The pair _U_ _V_ joins two vertices that an earlier pair already joins         | line of _V_              | `duplicate edge 'U V'`    |
| A token _K_ follows the last pair (or _m_ when _m_ = 0)                        | line of _K_              | `unexpected token 'K'`    |

_K_, _U_, and _V_ are the tokens' exact bytes (CONV-34); in the last two rows they are
separated by one space, whatever separated them in the input. Within a pair, *u*ₖ is checked
(grammar and range) before *v*ₖ, and the self-loop and duplicate checks follow both. A
`0x1A` byte that is followed by any other byte is ordinary data (CONV-37).
_AC:_ `dp-bfs-link -g bad-edge.txt` → stdout empty, stderr
`dp-bfs-link: bad-edge.txt:6: value out of range '7'\n`, exit 1. A description whose vertex
count is `0` gives `value out of range '0'`; three vertices with `m` = 4 give
`value out of range '4'`; the pair `2` `2` gives `self-loop '2 2'`; the pair `+2 00` after
`0 2` gives `duplicate edge '+2 00'`; a `#` after the last pair gives
`unexpected token '#'`; an empty standard input gives `dp-bfs-link: -:1: unexpected end of
input`. _(UR-07)_

### 4.2 Search and output

**FR-05: Breadth-first search.**
After the graph has been validated and START checked (FR-09), the tool MUST perform the
following search, with _s_ the value of START, a set of visited vertices, and a FIFO queue:

1. Mark _s_ visited, write its visit line, and append _s_ to the queue.
2. While the queue is not empty: remove the vertex _x_ at its front; for each vertex _y_ of
   the neighbor sequence of _x_ (FR-06, FR-07), in order, if _y_ is not visited, mark _y_
   visited, write its visit line, and append _y_ to the queue.

Each vertex reachable from _s_ is therefore written exactly once, in discovery order, and a
vertex that is not reachable from _s_ is not written at all. Every vertex at distance _d_
from _s_ is written before every vertex at distance _d_ + 1. A graph with _m_ = 0 writes only
the visit line of _s_.
_AC:_ `dp-bfs-adj -g islands.txt` writes Ada, Babbage; `dp-bfs-link -g islands.txt -s 4`
writes only Euler. In the output of both tools for the built-in graph, Anger is first, Lust,
Envy, and Gluttony precede Pride and Sloth, and Covetousness is last. _(UR-02, UR-06)_

**FR-06: Neighbor order of `dp-bfs-adj`.**
`dp-bfs-adj` MUST examine the neighbors of a vertex _x_ in ascending order of vertex number,
as a scan of row _x_ of the adjacency matrix from column 0 to column _n_ − 1 does. The order
of the edge list has no influence. For the built-in graph the neighbor sequences are:
0: 1 2 3; 1: 0 2 4; 2: 0 1 4; 3: 0 5; 4: 1 2 6; 5: 3 6; 6: 4 5.
_AC:_ `dp-bfs-adj` → stdout `Anger has been visited.\nLust has been visited.\nEnvy has been
visited.\nGluttony has been visited.\nPride has been visited.\nSloth has been
visited.\nCovetousness has been visited.\n`, stderr empty, exit 0; `dp-bfs-adj --start=4`
writes Pride, Lust, Envy, Covetousness, Anger, Sloth, Gluttony. _(UR-03)_

**FR-07: Neighbor order of `dp-bfs-link`.**
`dp-bfs-link` MUST build its adjacency lists as follows: all lists start empty; then, for each
edge (*u*ₖ, *v*ₖ) of the edge list in order _k_ = 1 … _m_, it inserts *v*ₖ at the head of the
list of *u*ₖ, and then *u*ₖ at the head of the list of *v*ₖ. It MUST examine the neighbors of
_x_ in list order, from the head. Consequently the neighbor sequence of _x_ is the reverse of
the order in which the edges that contain _x_ appear in the edge list, whichever endpoint _x_
is. For the built-in graph the neighbor sequences are:
0: 3 2 1; 1: 4 2 0; 2: 4 1 0; 3: 5 0; 4: 6 2 1; 5: 6 3; 6: 5 4.
_AC:_ `dp-bfs-link` writes Anger, Gluttony, Envy, Lust, Sloth, Pride, Covetousness;
`dp-bfs-link -s 4` writes Pride, Covetousness, Envy, Lust, Sloth, Anger, Gluttony;
`dp-bfs-link -g order.txt` writes North, South, East, West, Down, Up. _(UR-03)_

**FR-08: Output format.**
Each visited vertex _x_ is written as its visit line: _name_(_x_) exactly as its bytes appear
in the description, one space, `has been visited.`, and a single LF. There are no other
lines: no header, no blank lines, no summary, and no trailing spaces.
_AC:_ a one-vertex graph named `Zoë` (UTF-8) writes `Zoë has been visited.\n`. _(UR-02)_

**FR-09: Start vertex.**
The search starts at vertex START (default 0). START's syntax and its range 0 … 999 are
checked as option values (FR-13). After the graph has been validated, if START ≥ _n_, the tool
MUST write `<tool>: start vertex '<START>' out of range 0-<n−1>`, where `<START>` is the value
exactly as given and `<n−1>` is the decimal value of _n_ − 1, and exit with status 1 without
writing any visit line. A graph error (FR-04, FR-10) is reported instead of this one.
_AC:_ `dp-bfs-adj -s 7` → stderr `dp-bfs-adj: start vertex '7' out of range 0-6\n`, exit 1;
`dp-bfs-adj -s 7 -s 006` writes Covetousness first (last occurrence wins, leading zeros
allowed); with a one-vertex graph, `-s 1` gives `start vertex '1' out of range 0-0`.
_(UR-05)_

**FR-10: Unreadable input.**
If GRAPH does not exist, cannot be opened, is a directory, or a read error occurs, the tool
MUST write `<tool>: <source>: <reason>` with `<reason>` from the CONV-16 table, and exit with
status 1 without writing any visit line.
_AC:_ `dp-bfs-adj -g missing.txt` → stderr
`dp-bfs-adj: missing.txt: No such file or directory\n`, exit 1; `dp-bfs-link -g subdir`,
where `subdir` is a directory, → `dp-bfs-link: subdir: Is a directory`. _(UR-08)_

### 4.3 Command line

**FR-11: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read.
_AC:_ `dp-bfs-adj --help` and `dp-bfs-link --help` match the user manual exactly;
`dp-bfs-adj extra --help` also prints the help. _(UR-10)_

**FR-12: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ `dp-bfs-adj --version` → `dp-bfs-adj (dialectic-playground) 1.0.0\n`;
`dp-bfs-link -s x --version` → the `dp-bfs-link` version line, exit 0. _(UR-10)_

**FR-13: Usage errors.**
Unknown options (including `-p` and `--prompt`, which these tools do not have), missing
option arguments, and arguments supplied to `--help` or `--version`, MUST be reported with
the CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT
be abbreviated (CONV-08). An invalid VERTEX (section 3.2) or an empty FILE MUST be reported as
`<tool>: invalid argument '<value>' for '<option>'`, where `<option>` is `-s`, `--start`,
`-g`, or `--graph` as the user wrote it. Any operand MUST be reported as
`<tool>: extra operand '<first operand>'`. Option values and operands are checked after the
whole argument list has been scanned (CONV-12). When a usage error occurs, the tool MUST NOT
read standard input or any file and MUST NOT write anything to standard output.
_AC:_ `dp-bfs-adj sins.txt` → `dp-bfs-adj: extra operand 'sins.txt'`; `dp-bfs-adj -s 1000`
→ `dp-bfs-adj: invalid argument '1000' for '-s'`; `dp-bfs-link --start=-1` →
`dp-bfs-link: invalid argument '-1' for '--start'`; `dp-bfs-link -g ''` →
`dp-bfs-link: invalid argument '' for '-g'`; `dp-bfs-link -g subdir -s 1000` reports the
invalid argument, not the directory; each followed by the CONV-14 line, exit 2, stdout
empty. _(UR-11, UR-13)_

## 5. Non-functional requirements

| ID     | Category                                            | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Verification                              |
| :----- | :-------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------- |
| NFR-01 | Portability                                         | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: deterministic traversal order | The output order MUST depend only on the graph description, START, and the tool, never on the platform, the language's collection library, memory addresses, or hashing: neighbor sequences MUST be produced by the matrix scan of FR-06 and the head-inserted lists of FR-07, and the visited set and queue MUST NOT reorder vertices. The graph file MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-03 decides what a trailing Ctrl-Z run means. Vertex names are written byte for byte, with no re-encoding. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                         | For a graph of 1000 vertices and 100 000 edges (about 1 MiB), each tool MUST finish in under 1 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware. Peak memory MUST stay under 64 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31); `dp-bfs-adj` uses Θ(*n*²) memory for its matrix and `dp-bfs-link` Θ(_n_ + _m_) for its lists. Start-up and exit for the built-in graph MUST take under 100 ms native (300 ms interpreted).                                                                                                                                     | Measurement                               |
| NFR-04 | Robustness                                          | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                   | Unit + black-box tests                    |
| NFR-05 | Maintainability                                     | Option parsing, reading and validating the graph description, the graph representation, the search, and output MUST be separate units. The two tools MUST share every unit except the representation: one breadth-first search function MUST work on either representation through its neighbor sequences (Principles 3, 13, 18). `dp-bfs-adj`'s representation MUST be an _n_ × _n_ matrix, and `dp-bfs-link`'s one linked list per vertex with insertion at the head.                                                                                                                                                               | Design review                             |
| NFR-06 | Testability                                         | The parser, both representations, and the search MUST be unit-testable without I/O. Unit tests MUST cover the neighbor sequences of every vertex of the built-in graph in both representations (FR-06, FR-07), every row of the table in FR-04, a graph with _m_ = 0, and a disconnected graph.                                                                                                                                                                                                                                                                                                                                       | Code review                               |
| NFR-07 | Build                                               | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | CI                                        |
| NFR-08 | Security                                            | The tools MUST read only GRAPH (or standard input), MUST NOT create or modify any file, read environment variables, or run subprocesses. Memory MUST be bounded by the limits of FR-03 (at most 1000 vertices).                                                                                                                                                                                                                                                                                                                                                                                                                       | Inspection                                |

## 6. Diagnostics (complete list)

The messages are the same for both tools; `<tool>` is the canonical name of the tool that
writes them.

Usage errors (exit status 2). Each is followed by `Try '<tool> --help' for more information.`

| Trigger                                        | Exact first line                                                       |
| :--------------------------------------------- | :--------------------------------------------------------------------- |
| Unknown short option `x`                       | `<tool>: invalid option -- 'x'`                                        |
| Unknown or abbreviated long option token `T`   | `<tool>: unrecognized option 'T'`                                      |
| `-g` / `-s` without an argument                | `<tool>: option requires an argument -- 'g'` (or `'s'`)                |
| `--graph` / `--start` without an argument      | `<tool>: option '--graph' requires an argument` (or `'--start'`)       |
| `--help=…` / `--version=…`                     | `<tool>: option '--help' doesn't allow an argument` (or `'--version'`) |
| Empty FILE for `-g` or `--graph`               | `<tool>: invalid argument '' for '-g'` (or `'--graph'`)                |
| VERTEX `V` not all digits, empty, or above 999 | `<tool>: invalid argument 'V' for '-s'` (or `'--start'`)               |
| Operand `X`                                    | `<tool>: extra operand 'X'`                                            |

Runtime errors (exit status 1; the tool stops at the first one and writes no visit line):

| Trigger                                                                           | Exact message                                             |
| :-------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| GRAPH `F` does not exist                                                          | `<tool>: F: No such file or directory`                    |
| GRAPH `F` cannot be opened or read because access is denied                       | `<tool>: F: Permission denied`                            |
| GRAPH `F` is a directory                                                          | `<tool>: F: Is a directory`                               |
| A component of GRAPH `F` is not a directory                                       | `<tool>: F: Not a directory`                              |
| Any other open or read failure of GRAPH `F` (including standard input, `F` = `-`) | `<tool>: F: Input/output error`                           |
| Token `K` on line `L` of source `S` is not a valid _integer_                      | `<tool>: S:L: invalid integer 'K'`                        |
| Token `K` on line `L` of source `S` is outside its range                          | `<tool>: S:L: value out of range 'K'`                     |
| Source `S` ends early; `L` is its end-of-input line number                        | `<tool>: S:L: unexpected end of input`                    |
| Edge `U V` (second token on line `L`) joins a vertex to itself                    | `<tool>: S:L: self-loop 'U V'`                            |
| Edge `U V` (second token on line `L`) repeats an earlier edge                     | `<tool>: S:L: duplicate edge 'U V'`                       |
| Token `K` on line `L` follows the last edge                                       | `<tool>: S:L: unexpected token 'K'`                       |
| START `V` is not less than _n_                                                    | `<tool>: start vertex 'V' out of range 0-N` (N = _n_ − 1) |
| Standard output cannot be written (other than a broken pipe)                      | `<tool>: write error`                                     |

## 7. Verification

| Method                                                                                          | Applies to                  |
| :---------------------------------------------------------------------------------------------- | :-------------------------- |
| Black-box test (public, `tests/public/`, 10 cases; cases 03, 04, 05, 07, and 09 have two steps) | FR-01 … FR-08, FR-11, FR-13 |
| Black-box test (hidden, `tests/private/`, 10 cases; every case has several steps)               | FR-02 … FR-13               |
| Unit test (written by the implementer)                                                          | FR-03 … FR-07, NFR-06       |
| Measurement                                                                                     | NFR-03                      |
| Inspection / review                                                                             | NFR-02, NFR-05, NFR-08      |

Public test map:

| Test | Command(s)                                                     | Verifies                              |
| :--- | :------------------------------------------------------------- | :------------------------------------ |
| 01   | `dp-bfs-adj`                                                   | FR-01, FR-05, FR-06, FR-08            |
| 02   | `dp-bfs-link`                                                  | FR-01, FR-05, FR-07, FR-08            |
| 03   | `dp-bfs-adj --graph=sins.txt`; `dp-bfs-link -g sins.txt`       | FR-01, FR-02, FR-03                   |
| 04   | `dp-bfs-adj --start=4`; `dp-bfs-link -s 4`                     | FR-06, FR-07, FR-09                   |
| 05   | `dp-bfs-adj -g order.txt`; `dp-bfs-link -g order.txt`          | FR-03, FR-06, FR-07 (edge-list order) |
| 06   | `dp-bfs-link -g - < order.txt`                                 | FR-02 (standard input)                |
| 07   | `dp-bfs-adj -g islands.txt`; `dp-bfs-link -g islands.txt -s 4` | FR-05 (disconnected graph)            |
| 08   | `dp-bfs-link -g bad-edge.txt`                                  | FR-04                                 |
| 09   | `dp-bfs-adj --help`; `dp-bfs-link --help`                      | FR-11                                 |
| 10   | `dp-bfs-adj sins.txt`                                          | FR-13                                 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements          |
| :--------------- | :--------------------------- |
| UR-01            | FR-01, FR-05                 |
| UR-02            | FR-05, FR-08                 |
| UR-03            | FR-06, FR-07, NFR-02, NFR-05 |
| UR-04            | FR-02, FR-03, CONV-26        |
| UR-05            | FR-09                        |
| UR-06            | FR-05                        |
| UR-07            | FR-04, CONV-34               |
| UR-08            | FR-10, CONV-16               |
| UR-09            | FR-03, NFR-02, CONV-37       |
| UR-10            | FR-11, FR-12                 |
| UR-11            | FR-13                        |
| UR-12            | NFR-01, NFR-02, CONV-03      |
| UR-13            | FR-13, CLI-CONV              |
| UR-14            | NFR-03, NFR-07               |

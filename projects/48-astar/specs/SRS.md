<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-astar](#software-requirements-specification-srs--dp-astar)
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
    - [4.1 Data files](#41-data-files)
    - [4.2 Cities](#42-cities)
    - [4.3 Search and output](#43-search-and-output)
    - [4.4 Command line](#44-command-line)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-astar

| Field                     | Value                                                      |
| :------------------------ | :--------------------------------------------------------- |
| Document ID               | SRS-48                                                     |
| Project                   | `48-astar` — A* Heuristic Graph Search for European Cities |
| Product                   | `dp-astar` (canonical name)                                |
| Version                   | 1.0.0                                                      |
| Status                    | Approved (pre-written by the curriculum)                   |
| Parent document           | `URD.md` (URD-48)                                          |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)               |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                       |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-astar`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-astar` reads a city table (cities with estimated distances to a goal) and a table of
one-way road distances, obtains a start city from its operand or from standard input, and
searches for a route from the start city to the goal city (Vienna by default) with the A*
algorithm as specified in FR-08. It writes the route found and its length, or a line saying
that there is no route, and optionally a trace of every step of the search.

### 1.3 Definitions

| Term               | Definition                                                                                                                                                         |
| :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                 | The line-feed byte, `0x0A`                                                                                                                                         |
| NAMES              | The value of `-n`/`--names`, or `names.dat` if neither is given                                                                                                    |
| DISTANCES          | The value of `-d`/`--distances`, or `distance.dat` if neither is given                                                                                             |
| GOAL               | The value of `-g`/`--goal`, or `vienna` if neither is given                                                                                                        |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1  |
| _N_                | The number of cities in the city table, 1 ≤ _N_ ≤ 1000                                                                                                             |
| City               | An index 0 … _N_ − 1, in city-table order; city _i_ has the name _name_(_i_) (a token) and the estimate _h_(_i_)                                                   |
| _d_(_i_, _j_)      | The entry in row _i_, column _j_ of the distance table                                                                                                             |
| Road               | A pair (_i_, _j_) with _i_ ≠ _j_ and _d_(_i_, _j_) ≠ 1000; it leads **from** _i_ **to** _j_ and has length _d_(_i_, _j_). The table is not assumed to be symmetric |
| Fold               | ASCII case folding: each byte `0x41`–`0x5A` (`A`–`Z`) is replaced by the byte 32 higher (`a`–`z`); every other byte, including every byte ≥ `0x80`, is unchanged   |
| Match              | Two byte strings match if their folds are equal                                                                                                                    |
| Title form         | A city name with its first byte replaced by the corresponding upper-case letter if it is `0x61`–`0x7A` (`a`–`z`); `vienna` → `Vienna`                              |
| Decimal            | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                             |

### 1.4 References

- URD-48: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §10.9, and its companion-disk files `names.dat` and `distance.dat` (informative; see
  §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-astar` is a standalone executable. Its interfaces are the command line, the two data
files, standard input, standard output, standard error, and the exit status. It belongs to
the curriculum's applications-programming track (Projects 11–52) and adapts §10.9 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. It follows the uninformed
breadth-first search of `dp-bfs-adj` and `dp-bfs-link` (Project 47).

### 2.2 Product functions

1. Read and validate the city table and the distance table completely.
2. Look up the goal city and the start city, ignoring ASCII case.
3. Obtain the start city from the operand, or from standard input with an optional prompt.
4. Search with A*: OPEN and CLOSED sets, minimum-_f_ selection with a fixed tie-break,
   relaxation, and reopening.
5. Write the route and its total distance, or that there is no route; optionally write a
   trace of the search.
6. Report unreadable files, invalid data, and unknown cities; display help and version
   information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- All distances are integers, and the search MUST use integer arithmetic. With the limits of
  FR-01 and FR-02, every _g_ and _f_ value is at most 999 × 1000000 + 1000000 = 1000000000,
  so 32-bit signed integers suffice.

### 2.4 Assumptions

- The current working directory is where the default files `names.dat` and `distance.dat` are
  looked for; relative paths are relative to it.
- The data files may contain any bytes; only what FR-01 and FR-02 allow is accepted.
- The estimates are not assumed to be admissible (never larger than the true remaining
  distance); FR-08 defines the result whether they are or not.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §10.9 reads the 19 cities and their estimated distances to Vienna
from `names.dat` and a 19 × 19 table of road distances from `distance.dat` (1000 meaning no
road), asks `Enter start city:searches with A* — OPEN and CLOSED lists, expanding the
open city with the smallest _f_ = _g_ + _h_, updating a city's back pointer, _g_, and _f_
when a shorter route is found, and reopening it if it was closed — and prints the route and
its total distance. `dp-astar` keeps:

- the two data files, as the defaults in the current directory, read byte for byte as they
  are on the companion disk;
- the value 1000 as "no road", Vienna as the goal, and the prompt text `Enter start city:
- the A* rules as the section describes them, with the goal test made when a city is
  selected from OPEN (FR-08);
- the report wording: `Optimal path to Vienna:`, the route with `->` between cities, and
  `Total distance: <n> kilometers`.

It changes or adds the following, for the reasons given:

- **The README's example distances are wrong.** It gives 186 km for Prague and
  311 + 186 = 497 km (via Prague) for Berlin. In `distance.dat`, the road from Prague to
  Vienna is 185 km (186 is Prague's _estimate_ in `names.dat`), and the road from Berlin to
  Prague is 219 km (311 is the road from Bern to Munich), so the routes are
  `prague -> vienna`, 185 km, and `berlin -> prague -> vienna`, 404 km. The acceptance
  criteria use the values computed from the data (FR-09).
- **The distance table is directed.** The section's description calls the table a matrix of
  distances between adjacent cities, but `distance.dat` is not symmetric: Vienna's row has no
  roads at all, while Belgrade, Budapest, Munich, Prague, Trieste, and Warsaw have roads to
  Vienna; Bern has roads to Genoa (304) and Munich (311) that are absent in the other
  direction; and Belgrade's row holds 263 in Brussels' column, while Budapest's row holds 263
  in Belgrade's column. The data files are authoritative and are not repaired, so entry
  (_i_, _j_) is the road **from** _i_ **to** _j_ (section 1.3). Searching towards Vienna never
  needs a road out of Vienna, which is presumably why the table's author left them out.
- **Only 1000 means "no road".** The description also speaks of roads with distance below
  1000, but `distance.dat` contains a road of 1104 km between Bern and Madrid. Every entry
  other than 1000 is a road (section 1.3). For the textbook data this choice changes no
  route to Vienna: from Madrid, the road to Bern is opened but the route via Genoa is shorter.
- **The estimates are not all admissible.** Five estimates exceed the true remaining
  distance: Belgrade 601 (true 501), Budapest 186 (155), Copenhagen 769 (766), Prague 186
  (185), and Warsaw 557 (464). A* then no longer guarantees a shortest route in general.
  For the textbook data the routes found from all 19 cities are nevertheless the shortest
  ones; the heading `Optimal path to …` is kept from the textbook. The fixture
  `reopen-names.dat` uses a deliberately inadmissible estimate to make reopening happen.
- **Determinism.** The description does not say which city is expanded when several open
  cities have the same _f_, or in which order a city's neighbors are examined. FR-08 fixes
  both (lowest city index first), and `--trace` (FR-11) makes every step observable.
- **The start city** may be given as an operand, or is read from standard input as the
  textbook does, with the prompt written only with `-p`, `--prompt`, to standard error
  (FR-06, FR-07). City names are matched without regard to ASCII case (FR-05); the output
  always uses the spelling of the city table.
- **Other data and goals.** `-n`, `--names` and `-d`, `--distances` choose other data files,
  and `-g`, `--goal` another goal (the estimates must then be estimates for that goal). The
  table size is not fixed at 19: it is the number of cities in the city table.
- **Output layout.** The blank line the README shows after the typed city existed only to
  separate the answer from the echoed keyboard input and is not written. A goal that cannot
  be reached, which the textbook does not handle, is reported as `No path from … to ….`
  (FR-10).
- **Validation.** Both files are read and validated completely before the start city is read
  or anything is written, and every problem is diagnosed with a CONV-34 message (FR-03).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (both data files and the start city on standard input are read as
tokens; line numbers), CONV-33 (estimates and distances use the _integer_ grammar, further
restricted to 0 … 1000000), CONV-34 (data diagnostics, with the standard messages
`invalid integer`, `value out of range`, and `unexpected end of input`, and the further
messages `too many cities`, `duplicate city`, `unexpected token`, and
`unknown start city`; nothing has been written to standard output when one is reported),
CONV-36 (`-p`, `--prompt`), and CONV-37 (both data files and standard input are _text
data_). CONV-35 does not apply, because no real number is written, and CONV-38 does not
apply, because nothing is random. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read only
when the start city is not given as an operand, or the operand is `-` (CONV-10, CONV-26).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-astar [-n FILE | --names=FILE] [-d FILE | --distances=FILE]
         [-g CITY | --goal=CITY] [-t | --trace] [-p | --prompt] [CITY]
dp-astar --help
dp-astar --version
```

### 3.2 Options

| Short | Long          | Argument        | Default        | Description                                                                               |
| :---- | :------------ | :-------------- | :------------- | :---------------------------------------------------------------------------------------- |
| `-n`  | `--names`     | FILE (required) | `names.dat`    | Read the city table from FILE (FR-01)                                                     |
| `-d`  | `--distances` | FILE (required) | `distance.dat` | Read the distance table from FILE (FR-02)                                                 |
| `-g`  | `--goal`      | CITY (required) | `vienna`       | Search for a route to CITY (FR-05)                                                        |
| `-t`  | `--trace`     | none            | off            | Write a trace of the search before the result (FR-11)                                     |
| `-p`  | `--prompt`    | none            | off            | Write the prompt `Enter start city:o standard error before the start city is read (FR-07) |
| —     | `--help`      | none            | —              | Print the help text and exit 0                                                            |
| —     | `--version`   | none            | —              | Print the version line and exit 0                                                         |

Option syntax (bundling such as `-tp`, `-nFILE`, `--names FILE`, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. If an option is repeated, the last occurrence wins
(CONV-11); only the winning value is checked. An empty FILE, the FILE `-`, and an empty CITY
for `-g`/`--goal` are invalid option values (FR-14): standard input is reserved for the start
city, so a data file named `-` must be written as `./-`.

### 3.3 Operands

At most one CITY operand, the start city, used exactly as given (CONV-05). The operand `-`
means that the start city is read from standard input, as when no operand is given. Every
token after `--` is an operand.

### 3.4 Standard input

Read only when no CITY operand is given or the operand is `-` (FR-06), and then only as far
as needed to obtain the first token. Read as raw bytes; no newline translation of any kind is
performed on any platform.

### 3.5 Standard output

The trace (FR-11, only with `--trace`), followed by the result (FR-09 or FR-10). Nothing is
written to standard output if any error is detected. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-12 … FR-14 instead.

### 3.6 Standard error

The prompt (FR-07, only with `--prompt`) and diagnostics (section 6). Without `--prompt`,
nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                                                           |
| :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | A result was written — a route (FR-09) or `No path` (FR-10) — or `--help` / `--version` was handled                                                                                                 |
| 1      | A data file could not be read (FR-04) or is invalid (FR-03), the goal or start city is unknown or missing (FR-05, FR-06), standard input could not be read, or standard output could not be written |
| 2      | Usage error (FR-14)                                                                                                                                                                                 |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF. `names.dat` and `distance.dat` are the textbook data
files in `tests/fixtures/`; the other public fixture files there are: `start.txt`
(`Lisbon\n`); `short.dat` (`distance.dat` without its last entry, ending in LF, 56 lines);
`reopen-names.dat` and `reopen-dist.dat`, the cities `origin 0`, `alpha 0`, `beta 10`,
`target 0` with the roads origin→alpha 4, origin→beta 1, alpha→target 10, beta→alpha 1 and no
others; and `tie-names.dat` and `tie-dist.dat`, the cities `start`, `south`, `north`, `end`,
all with estimate 0, with the roads start→south 5, start→north 5, south→end 5, north→end 5.

### 4.1 Data files

**FR-01: City table.**
The tool MUST open the file NAMES and read it to its end as raw bytes. Its content is _text
data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very end is ignored.
The rest is divided into tokens (CONV-32), so line structure, tabs, CRLF line endings, and
alignment have no meaning. The tokens MUST form _N_ ≥ 1 consecutive pairs, _name_(_i_) and
_h_(_i_) for _i_ = 0 … _N_ − 1, and nothing else, where:

- _name_(_i_) is any token, and MUST NOT match (section 1.3) the name of an earlier city;
- _h_(_i_) is a valid _integer_ (CONV-33) with 0 ≤ _h_(_i_) ≤ 1000000;
- _N_ ≤ 1000.

The textbook's `names.dat` has _N_ = 19 (amsterdam … warsaw, with vienna as city 17).
_AC:_ the textbook's `names.dat`, whose lines mix spaces and TAB characters and which ends in
LF followed by a run of `0x1A` bytes with no final LF, is accepted with _N_ = 19. _(UR-08)_

**FR-02: Distance table.**
After the city table has been validated, the tool MUST open the file DISTANCES and read it to
its end as raw bytes; its content is _text data_ (CONV-37) and is divided into tokens
(CONV-32). The tokens MUST be exactly _N_ × _N_ valid _integers_, each in 0 … 1000000; the
token at position _i_ × _N_ + _j_ (counting from 0) is _d_(_i_, _j_). Rows need not start on
new lines; in the textbook's `distance.dat` each row of 19 entries is wrapped over two lines
and followed by a blank line. The diagonal entries _d_(_i_, _i_) are validated but otherwise
ignored. The value 1000 means that there is no road from _i_ to _j_; every other off-diagonal
value is the length of the road from _i_ to _j_ (section 1.3), including values above 1000.
_AC:_ the textbook's `distance.dat` is accepted; the road from Bern to Madrid (1104) is a
road (FR-11 AC); there is no road from Vienna to any city. _(UR-08)_

**FR-03: Invalid data.**
Each data file is checked in token order, the city table completely before the distance table
is opened. The first violation MUST be reported as `dp-astar: <file>:<line>: <message>`
(CONV-34), where `<file>` is NAMES or DISTANCES exactly as given, after which the tool exits
with status 1 without reading standard input or writing anything to standard output.
`<line>` and `<message>` are:

| Violation                                                                                          | `<line>`                 | `<message>`               |
| :------------------------------------------------------------------------------------------------- | :----------------------- | :------------------------ |
| An estimate or distance token _K_ is not a valid _integer_                                         | line of _K_              | `invalid integer 'K'`     |
| An estimate or distance token _K_ is a valid _integer_ outside 0 … 1000000                         | line of _K_              | `value out of range 'K'`  |
| A city table has no tokens, or ends after a name; a distance table has fewer than _N_ × _N_ tokens | end-of-input line number | `unexpected end of input` |
| A name token _K_ would be city number 1001                                                         | line of _K_              | `too many cities`         |
| A name token _K_ matches the name of an earlier city                                               | line of _K_              | `duplicate city 'K'`      |
| A distance table has a token _K_ after its first _N_ × _N_ tokens                                  | line of _K_              | `unexpected token 'K'`    |

_K_ is the token's exact bytes (CONV-34). For each city, the checks on its name (too many
cities, then duplicate) come before the checks on its estimate. In a distance table that is
too short, an invalid token is reported in preference to the end of input, because it comes
first.
_AC:_ `dp-astar --distances=short.dat prague` → stdout empty, stderr
`dp-astar: short.dat:57: unexpected end of input\n`, exit 1. An estimate `76O` gives
`invalid integer '76O'`; the entry `-628` gives `value out of range '-628'`; a city table with
`Rome` and later `ROME` gives `duplicate city 'ROME'`; an empty city table gives
`<file>:1: unexpected end of input`; a 1001st city gives `too many cities`; a distance table
with one entry too many gives `unexpected token` for that entry. _(UR-09)_

**FR-04: Unreadable files.**
If NAMES or DISTANCES does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-astar: <file>: <reason>`, with `<file>` as given and `<reason>` from
the CONV-16 table, and exit with status 1 without writing anything to standard output. NAMES
is opened and validated before DISTANCES is opened, so a problem with NAMES is reported
instead of any problem with DISTANCES.
_AC:_ `dp-astar -d subdir berlin`, where `subdir` is a directory, →
`dp-astar: subdir: Is a directory`; `dp-astar -n missing.dat -d subdir berlin` →
`dp-astar: missing.dat: No such file or directory` only; exit 1. _(UR-10)_

### 4.2 Cities

**FR-05: City lookup and goal.**
A city name given by the user — the goal, or the start city — denotes the city whose name
matches it (section 1.3); because names in the city table are unique under folding, there is
at most one. Only ASCII letters are folded; the comparison MUST NOT depend on the locale.
After both data files have been validated, the tool MUST look up GOAL; if no city matches,
it MUST write `dp-astar: unknown goal city '<GOAL>'`, with GOAL exactly as given, and exit with
status 1 without reading standard input or writing a prompt. Output always uses the names as
the city table spells them.
_AC:_ `dp-astar Vienna` and `dp-astar LISBON` are accepted and print `vienna` and `lisbon`;
`dp-astar -g PARIS brussels` writes the heading `Optimal path to Paris:`;
`dp-astar -g atlantis prague` → `dp-astar: unknown goal city 'atlantis'`, exit 1. _(UR-02,
UR-07)_

**FR-06: Start city.**
After the goal has been found: if a CITY operand other than `-` is given, it is the start
city's name. Otherwise the tool MUST read standard input, as _text data_, only as far as
needed to obtain its first token (CONV-32): reading stops at the first whitespace byte after
the token, and the rest of standard input is neither read nor checked. If the token extends
to the end of the input, a trailing run of `0x1A` bytes is removed from it (CONV-37), and a
token that consisted only of `0x1A` bytes is absent. Then:

- If standard input has no token, the tool MUST write
  `dp-astar: -:<line>: unexpected end of input`, `<line>` being the end-of-input line number
  of standard input, and exit with status 1.
- If no city matches an operand, the tool MUST write `dp-astar: unknown start city '<CITY>'`,
  with CITY exactly as given (an empty operand gives `''`).
- If no city matches a token read from standard input, the tool MUST write
  `dp-astar: -:<line>: unknown start city '<token>'`, with the token's line number and exact
  bytes (CONV-34).

In each case the exit status is 1 and nothing is written to standard output.
_AC:_ `dp-astar berln` → stderr `dp-astar: unknown start city 'berln'\n`, exit 1;
`dp-astar - < f`, where _f_ is `aples rome\n`, computes the route from naples;
a standard input of `COPENHAGEN\r\n` is accepted; `bern` followed by two `0x1A` bytes and no
LF is accepted as `bern`; `\nAtlantis\n` gives `dp-astar: -:2: unknown start city
'Atlantis'`; an empty standard input gives `dp-astar: -:1: unexpected end of input`.
_(UR-01, UR-03, UR-04)_

**FR-07: Prompt.**
`-p`, `--prompt` enables the single prompt of this tool, the 18 bytes `Enter start city:
(ending with one space, no LF). With prompts enabled, and only when the start city is read
from standard input (FR-06), the tool MUST write the prompt to standard error, and flush
standard error, immediately before it reads standard input — after both data files have been
validated and the goal found. The prompt is also written when standard input turns out to be
empty, and a diagnostic that follows it continues the same line (CONV-36). No prompt is
written when a CITY operand other than `-`is given, or when an earlier error occurs. The
prompt never changes standard output.
_AC:_`dp-astar --prompt < start.txt`→ stdout the route from lisbon (FR-09 AC), stderr`Enter start city:ith no LF, exit 0; `dp-astar -p` with empty standard input → stderr
`Enter start city: dp-astar: -:1: unexpected end of input\n`, exit 1;
`dp-astar -g PARIS -p brussels` writes no prompt. _(UR-03)_

### 4.3 Search and output

_*FR-08: A* search._*
With _s_ the start city and _t_ the goal city, the tool MUST perform the following search.
Each city has a state — NEW, OPEN, or CLOSED — and, once reached, the values _g_, _f_, and a
back pointer. Initially every city is NEW.

1. Set _g_(_s_) = 0, _f_(_s_) = _h_(_s_), and the state of _s_ to OPEN; _s_ has no back
   pointer.
2. If no city is OPEN, the search ends with **no path** (FR-10).
3. Select the OPEN city _u_ with the smallest _f_(_u_); if several OPEN cities have that
   smallest _f_, select the one with the lowest index.
4. If _u_ = _t_, the search ends with **success** (FR-09).
5. Set the state of _u_ to CLOSED.
6. For each city _v_ = 0, 1, …, _N_ − 1, in ascending order, such that (_u_, _v_) is a road
   (in particular _v_ ≠ _u_), let _g_′ = _g_(_u_) + _d_(_u_, _v_):
   - if _v_ is NEW: set _g_(_v_) = _g_′, _f_(_v_) = _g_′ + _h_(_v_), the back pointer of _v_
     to _u_, and the state of _v_ to OPEN (_open_);
   - otherwise, if _g_′ < _g_(_v_) (strictly): set _g_(_v_), _f_(_v_), and the back pointer
     in the same way, and the state of _v_ to OPEN — _v_ was either OPEN (_update_) or
     CLOSED (_reopen_);
   - otherwise _v_ is unchanged.
7. Continue with step 2.

The search always ends, because a city's _g_ only ever decreases and is the length of a
route without repeated cities. When _s_ = _t_, it ends with success at the first selection.
_AC:_ with `reopen-names.dat`, `reopen-dist.dat`, and goal `target` from `origin`, alpha is
expanded with _g_ = 4, reopened with _g_ = 2 when beta is expanded, and expanded again, so the
route is `origin -> beta -> alpha -> target` of 12 (FR-11 AC). With `tie-names.dat` and
`tie-dist.dat` from `start` to `end`, south and north are opened with the same _f_ = 5, south
(index 1) is selected first, and end is not updated from north because 10 is not less than
10, so the route is `start -> south -> end`. _(UR-06)_

**FR-09: Result.**
On success, the tool MUST write exactly three lines to standard output:

```text
Optimal path to <Goal>:
<route>
Total distance: <g> kilometers
```

`<Goal>` is the title form (section 1.3) of _name_(_t_). `<route>` is the sequence of cities
obtained by following back pointers from _t_ to _s_, written from _s_ to _t_: their names,
separated by `->` (space, hyphen, greater-than, space); when _s_ = _t_, it is the single
name. `<g>` is the decimal of _g_(_t_). Each line ends with a single LF; there are no other
spaces and no blank lines. `kilometers` is written even for a distance of 0 or 1.
_AC:_ `dp-astar prague` → stdout
`Optimal path to Vienna:\nprague -> vienna\nTotal distance: 185 kilometers\n`, stderr
empty, exit 0. With the textbook data the results are:

| Start      | Route                                               | Total |
| :--------- | :-------------------------------------------------- | ----: |
| amsterdam  | amsterdam -> munich -> vienna                       |   806 |
| belgrade   | belgrade -> vienna                                  |   501 |
| berlin     | berlin -> prague -> vienna                          |   404 |
| bern       | bern -> munich -> vienna                            |   591 |
| brussels   | brussels -> amsterdam -> munich -> vienna           |   970 |
| budapest   | budapest -> vienna                                  |   155 |
| copenhagen | copenhagen -> hamburg -> berlin -> prague -> vienna |   766 |
| genoa      | genoa -> trieste -> vienna                          |   678 |
| hamburg    | hamburg -> berlin -> prague -> vienna               |   586 |
| lisbon     | lisbon -> madrid -> genoa -> trieste -> vienna      |  1968 |
| madrid     | madrid -> genoa -> trieste -> vienna                |  1629 |
| munich     | munich -> vienna                                    |   280 |
| naples     | naples -> rome -> trieste -> vienna                 |   893 |
| paris      | paris -> brussels -> amsterdam -> munich -> vienna  |  1195 |
| prague     | prague -> vienna                                    |   185 |
| rome       | rome -> trieste -> vienna                           |   759 |
| trieste    | trieste -> vienna                                   |   317 |
| vienna     | vienna                                              |     0 |
| warsaw     | warsaw -> vienna                                    |   464 |

_(UR-01)_

**FR-10: No path.**
When the search ends with no path, the tool MUST write the single line
`No path from <start> to <Goal>.` + LF to standard output, where `<start>` is _name_(_s_) and
`<Goal>` the title form of _name_(_t_), and exit with status 0.
_AC:_ `dp-astar --goal=lisbon vienna` → stdout `No path from vienna to Lisbon.\n`, exit 0.
_(UR-04)_

**FR-11: Trace.**
With `-t`, `--trace`, the tool MUST write one trace line to standard output for each of the
following events, in the order in which they occur in FR-08, before the result of FR-09 or
FR-10:

| Event                                     | Line                             |
| :---------------------------------------- | :------------------------------- |
| Step 1 (_s_ opened)                       | `open <s> g=<g> f=<f>`           |
| Step 3 (_u_ selected, including the goal) | `select <u> g=<g> f=<f>`         |
| Step 6, _v_ was NEW                       | `open <v> g=<g> f=<f> via <u>`   |
| Step 6, _v_ was OPEN and improved         | `update <v> g=<g> f=<f> via <u>` |
| Step 6, _v_ was CLOSED and improved       | `reopen <v> g=<g> f=<f> via <u>` |

City names are as the city table spells them, `<g>` and `<f>` are the decimals of the city's
values after the event, and each line ends with a single LF, with single spaces as shown.
Without `--trace`, no trace line is written.
_AC:_ `dp-astar --trace berlin` writes
`open berlin g=0 f=386`, `select berlin g=0 f=386`, `open bern g=628 f=1118 via berlin`,
`open hamburg g=182 f=735 via berlin`, `open prague g=219 f=405 via berlin`,
`open warsaw g=345 f=902 via berlin`, `select prague g=219 f=405`,
`open munich g=393 f=657 via prague`, `open vienna g=404 f=404 via prague`,
`select vienna g=404 f=404`, then the result of FR-09. `dp-astar -t madrid` includes
`open bern g=1104 f=1594 via madrid` and `update brussels g=1030 f=1702 via paris`. With the
reopening data set, the trace includes `reopen alpha g=2 f=2 via beta` and
`update target g=12 f=12 via alpha`. _(UR-05)_

### 4.4 Command line

**FR-12: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No file or input is read and no
prompt is written.
_AC:_ `dp-astar --help` matches the user manual exactly; `dp-astar a b --help` also prints
it. _(UR-11)_

**FR-13: Version.**
`--version` MUST write `dp-astar (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-astar -d - --version` also prints it. _(UR-11)_

**FR-14: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--trace=…`, `--prompt=…`, `--help=…`, `--version=…`), MUST be reported with the CONV-13
messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be
abbreviated (CONV-08). An empty FILE or the FILE `-` for `-n`, `--names`, `-d`, or
`--distances`, and an empty CITY for `-g` or `--goal`, MUST be reported as
`dp-astar: invalid argument '<value>' for '<option>'`, with `<option>` as the user wrote it. A
second operand MUST be reported as `dp-astar: extra operand '<second operand>'`. Option values
and operands are checked after the whole argument list has been scanned (CONV-12). When a
usage error occurs, the tool MUST NOT read any file or standard input, write a prompt, or
write anything to standard output.
_AC:_ `dp-astar berlin prague` → `dp-astar: extra operand 'prague'`; `dp-astar -n '' berlin`
→ `dp-astar: invalid argument '' for '-n'`; `dp-astar --distances=- berlin` →
`dp-astar: invalid argument '-' for '--distances'`; `dp-astar --goal= berlin` →
`dp-astar: invalid argument '' for '--goal'`; `dp-astar --trace=yes` →
`dp-astar: option '--trace' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-12, UR-14)_

## 5. Non-functional requirements

| ID     | Category                                                                | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Verification                              |
| :----- | :---------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| NFR-01 | Portability                                                             | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: legacy data files and locale-independent matching | Both data files and standard input MUST be read in binary mode on every platform: CR bytes reach the tokenizer (where they are whitespace), TAB characters are whitespace, and a `0x1A` byte is never treated as end-of-file by the I/O layer — only FR-01, FR-02, and FR-06 decide what a trailing Ctrl-Z run means (the textbook files end in 85 and 29 such bytes). City names MUST be compared with the ASCII fold of section 1.3, never with a locale-dependent or Unicode case conversion (under a Turkish locale, for example, `I` does not lower-case to `i`). Names are written byte for byte, with no re-encoding. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                                             | For 1000 cities (a distance table of 1 000 000 entries, about 5 MiB), the tool MUST finish in under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 64 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). The selection of step 3 MAY scan all cities (O(*N*²) overall). Start-up and exit with the textbook data MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                         | Measurement                               |
| NFR-04 | Robustness                                                              | The tool MUST NOT crash, panic, or print a stack trace for any argument list, data file, or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                               | Unit + black-box tests                    |
| NFR-05 | Maintainability                                                         | Option parsing, reading and validating each data file, city lookup, reading the start city, the search, and output formatting MUST be separate units. The search MUST be one function of the data, the start, and the goal that returns the route (or no path) and the trace events, without doing I/O (Principles 13, 18).                                                                                                                                                                                                                                                                                                  | Design review                             |
| NFR-06 | Testability                                                             | The search and the city lookup MUST be unit-testable without files. Unit tests MUST cover every row of the result table of FR-09, the reopening and tie-breaking data sets of FR-08, start = goal, an unreachable goal, and every row of the table in FR-03.                                                                                                                                                                                                                                                                                                                                                                 | Code review                               |
| NFR-07 | Build                                                                   | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | CI                                        |
| NFR-08 | Security                                                                | The tool MUST read only NAMES, DISTANCES, and standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. Memory MUST be bounded by the limits of FR-01 and FR-02.                                                                                                                                                                                                                                                                                                                                                                                                                  | Inspection                                |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-astar --help' for more information.`

| Trigger                                                              | Exact first line                                                                                    |
| :------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| Unknown short option `x`                                             | `dp-astar: invalid option -- 'x'`                                                                   |
| Unknown or abbreviated long option token `T`                         | `dp-astar: unrecognized option 'T'`                                                                 |
| `-n` / `-d` / `-g` without an argument                               | `dp-astar: option requires an argument -- 'n'` (or `'d'`, `'g'`)                                    |
| `--names` / `--distances` / `--goal` without an argument             | `dp-astar: option '--names' requires an argument` (or `'--distances'`, `'--goal'`)                  |
| `--trace=…`, `--prompt=…`, `--help=…`, `--version=…`                 | `dp-astar: option '--trace' doesn't allow an argument` (or `'--prompt'`, `'--help'`, `'--version'`) |
| Empty FILE, or FILE `-`, for `-n`, `--names`, `-d`, or `--distances` | `dp-astar: invalid argument '' for '-n'` (or `'-'`, and the option as written)                      |
| Empty CITY for `-g` or `--goal`                                      | `dp-astar: invalid argument '' for '-g'` (or `'--goal'`)                                            |
| A second operand `X`                                                 | `dp-astar: extra operand 'X'`                                                                       |

Runtime errors (exit status 1; the tool stops at the first one and writes nothing to
standard output):

| Trigger                                                                   | Exact message                            |
| :------------------------------------------------------------------------ | :--------------------------------------- |
| Data file `F` does not exist                                              | `dp-astar: F: No such file or directory` |
| Data file `F` cannot be opened or read because access is denied           | `dp-astar: F: Permission denied`         |
| Data file `F` is a directory                                              | `dp-astar: F: Is a directory`            |
| A component of data file `F` is not a directory                           | `dp-astar: F: Not a directory`           |
| Any other open or read failure of data file `F`                           | `dp-astar: F: Input/output error`        |
| Token `K` on line `L` of data file `F` is not a valid _integer_           | `dp-astar: F:L: invalid integer 'K'`     |
| Token `K` on line `L` of data file `F` is outside 0 … 1000000             | `dp-astar: F:L: value out of range 'K'`  |
| Data file `F` ends early; `L` is its end-of-input line number             | `dp-astar: F:L: unexpected end of input` |
| Name token on line `L` of city table `F` would be city 1001               | `dp-astar: F:L: too many cities`         |
| Name token `K` on line `L` of city table `F` matches an earlier name      | `dp-astar: F:L: duplicate city 'K'`      |
| Token `K` on line `L` of distance table `F` follows the _N_ × _N_ entries | `dp-astar: F:L: unexpected token 'K'`    |
| No city matches GOAL `G`                                                  | `dp-astar: unknown goal city 'G'`        |
| No city matches the operand `C`                                           | `dp-astar: unknown start city 'C'`       |
| Standard input has no token; `L` is its end-of-input line number          | `dp-astar: -:L: unexpected end of input` |
| No city matches the token `K` on line `L` of standard input               | `dp-astar: -:L: unknown start city 'K'`  |
| Standard input cannot be read                                             | `dp-astar: -: Input/output error`        |
| Standard output cannot be written (other than a broken pipe)              | `dp-astar: write error`                  |

When `--prompt` is given and the start city is read from standard input, a diagnostic about
standard input follows the prompt on the same line of standard error (FR-07).

## 7. Verification

| Method                                                                                            | Applies to                                  |
| :------------------------------------------------------------------------------------------------ | :------------------------------------------ |
| Black-box test (public, `tests/public/`, 10 cases)                                                | FR-01 … FR-12                               |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 03, and 05 … 10 have several steps) | FR-01 … FR-11, FR-13, FR-14                 |
| Unit test (written by the implementer)                                                            | FR-01 … FR-03, FR-05, FR-08 … FR-11, NFR-06 |
| Measurement                                                                                       | NFR-03                                      |
| Inspection / review                                                                               | NFR-02, NFR-05, NFR-08                      |

Public test map:

| Test | Command                                                               | Verifies                                                          |
| :--- | :-------------------------------------------------------------------- | :---------------------------------------------------------------- |
| 01   | `dp-astar prague`                                                     | FR-01, FR-02, FR-06, FR-08, FR-09 (README's 186 corrected to 185) |
| 02   | `dp-astar berlin`                                                     | FR-08, FR-09 (README's 497 corrected to 404)                      |
| 03   | `dp-astar --prompt < start.txt`                                       | FR-05 (case), FR-06, FR-07                                        |
| 04   | `dp-astar Vienna`                                                     | FR-05, FR-08 (start = goal), FR-09                                |
| 05   | `dp-astar --trace berlin`                                             | FR-08, FR-11                                                      |
| 06   | `dp-astar -n reopen-names.dat -d reopen-dist.dat -g target -t origin` | FR-08 (reopening), FR-11                                          |
| 07   | `dp-astar --goal=lisbon vienna`                                       | FR-02 (directed table), FR-05, FR-10                              |
| 08   | `dp-astar berln`                                                      | FR-06 (unknown start city)                                        |
| 09   | `dp-astar --help`                                                     | FR-12                                                             |
| 10   | `dp-astar --distances=short.dat prague`                               | FR-02, FR-03                                                      |

## 8. Traceability (URD → SRS)

| User requirement | System requirements           |
| :--------------- | :---------------------------- |
| UR-01            | FR-06, FR-08, FR-09           |
| UR-02            | FR-05, NFR-02                 |
| UR-03            | FR-06, FR-07, CONV-36         |
| UR-04            | FR-06, FR-10                  |
| UR-05            | FR-11                         |
| UR-06            | FR-08, FR-11                  |
| UR-07            | FR-01, FR-02, FR-05           |
| UR-08            | FR-01, FR-02, NFR-02, CONV-37 |
| UR-09            | FR-03, CONV-34                |
| UR-10            | FR-04, CONV-16                |
| UR-11            | FR-12, FR-13                  |
| UR-12            | FR-14                         |
| UR-13            | NFR-01, NFR-02, CONV-03       |
| UR-14            | FR-14, CLI-CONV               |
| UR-15            | NFR-03, NFR-07                |

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-astar — User Manual](#dp-astar--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The data files](#the-data-files)
    - [The search](#the-search)
  - [OPTIONS](#options)
    - [Option syntax](#option-syntax)
  - [EXIT STATUS](#exit-status)
  - [DIAGNOSTICS](#diagnostics)
  - [EXAMPLES](#examples)
  - [HELP OUTPUT](#help-output)
  - [VERSION OUTPUT](#version-output)
  - [ENVIRONMENT](#environment)
  - [PLATFORM NOTES](#platform-notes)
  - [INSTALLATION](#installation)
  - [SEE ALSO](#see-also)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# dp-astar — User Manual

| Field         | Value                                                      |
| :------------ | :--------------------------------------------------------- |
| Product       | `dp-astar` 1.0.0                                           |
| Project       | `48-astar` — A* Heuristic Graph Search for European Cities |
| Applies to    | Linux, macOS, Windows                                      |
| Specification | `SRS.md` (SRS-48), `shared/CLI-CONVENTIONS.md`             |

---

## NAME

**dp-astar** — find the shortest road route to Vienna with the A* search

## SYNOPSIS

```text
dp-astar [-n FILE | --names=FILE] [-d FILE | --distances=FILE]
         [-g CITY | --goal=CITY] [-t | --trace] [-p | --prompt] [CITY]
dp-astar --help
dp-astar --version
```

## DESCRIPTION

`dp-astar` finds a route by road from the start city _CITY_ to Vienna and prints it with its
length:

```text
$ dp-astar berlin
Optimal path to Vienna:
berlin -> prague -> vienna
Total distance: 404 kilometers
```

Without _CITY_ (or with `-`), it reads the start city from standard input: the first word
typed, as the textbook program does. City names may be typed in any mix of upper and lower
case (`Berlin`, `BERLIN`); the output always uses the spelling of the city table.

### The data files

The map comes from two files in the current directory, both from the textbook's companion
disk:

- **`names.dat`**, the city table: each city's name followed by an estimate of its distance
  to Vienna in a straight line, for 19 cities from `amsterdam` to `warsaw`.
- **`distance.dat`**, the distance table: 19 × 19 numbers, row by row in the order of the city
  table. The number in row _i_, column _j_ is the length of the road **from** city _i_ **to**
  city _j_; `1000` means that there is no such road. Every other number is a road, even one
  above 1000 (Bern to Madrid is 1104).

The tables are read as words and numbers separated by any spaces, tabs, or line breaks, so
their layout does not matter: in `distance.dat` each row is wrapped over two lines. Files with
Windows (CRLF) line endings read the same, and Ctrl-Z bytes at the very end of a file (the
end-of-file padding of old MS-DOS files, present in both textbook files) are ignored.

The distance table is **not symmetric**, and `dp-astar` uses it exactly as it is. In
particular there are no roads out of Vienna at all, and a few roads exist in one direction
only. Use `-n` and `-d` to read other files in the same formats; the number of cities is the
number of entries in the city table, up to 1000, and estimates and distances are whole
numbers from 0 to 1000000. City names must be unique, ignoring case.

### The search

`dp-astar` uses the A* algorithm. For each city it reaches, it keeps _g_, the length of the
best route found so far from the start, and _f_ = _g_ + _h_, where _h_ is the city's
estimate. Reached cities are OPEN until they are expanded, then CLOSED. At each step the tool:

1. selects the OPEN city with the smallest _f_ — if several have the same _f_, the one that
   comes first in the city table;
2. stops if that city is the goal;
3. otherwise closes it and follows each of its roads, in city-table order: a city reached for
   the first time is opened; a city already reached is updated only if the new route is
   strictly shorter, and is moved back to OPEN (_reopened_) if it was closed.

If no city is left OPEN, there is no route, and the tool prints `No path from <start> to
<Goal>.` The route found is the shortest one whenever the estimates never exceed the true
remaining distances. Five estimates in `names.dat` do exceed them slightly (Belgrade,
Budapest, Copenhagen, Prague, and Warsaw), but the routes found from all 19 cities are still
the shortest ones.

With `--trace`, the tool first prints every step: `open`, `select`, `update`, and `reopen`
lines, each with the city's _g_ and _f_, and with `via` the city it was reached from.

## OPTIONS

**`-n FILE`, `--names=FILE`**
: Read the city table from _FILE_ instead of `names.dat`.

**`-d FILE`, `--distances=FILE`**
: Read the distance table from _FILE_ instead of `distance.dat`.

**`-g CITY`, `--goal=CITY`**
: Find a route to _CITY_ instead of Vienna. The estimates in the city table should then be
estimates of the distance to _CITY_.

**`-t`, `--trace`**
: Print every step of the search before the result.

**`-p`, `--prompt`**
: When the start city is read from standard input, first write `Enter start city:o
standard error. Standard output is the same with or without this option.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-astar` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-gparis`, `-g paris`, `--goal=paris`, and
  `--goal paris` are equivalent. Flags can be combined: `-tp`.
- Long options must be spelled out in full; `--dist` is not accepted.
- If an option is given more than once, the last one wins.
- Standard input is reserved for the start city, so `-n -` and `-d -` are errors; to read a
  data file that is really named `-`, write `./-`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                      |
| :----- | :------------------------------------------------------------------------------------------- |
| 0      | Success: a route, or `No path`, was printed; or help or version was printed                  |
| 1      | A data file could not be read or is invalid, or the start or goal city is unknown or missing |
| 2      | Usage error: an invalid option or value, or more than one city                               |

## DIAGNOSTICS

Every problem is reported on standard error as one line, and nothing is written to standard
output. Problems in a data file name the file and the line; problems with a start city read
from standard input name `-` and the line:

```text
$ dp-astar --distances=short.dat prague
dp-astar: short.dat:57: unexpected end of input
```

| Message                        | Cause                                                                                               | Fix                                               |
| :----------------------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| `F:L: invalid integer 'K'`     | An estimate or distance _K_ is not a whole number                                                   | Write it in digits                                |
| `F:L: value out of range 'K'`  | An estimate or distance is negative or above 1000000                                                | Correct the number                                |
| `F:L: unexpected end of input` | The city table is empty or ends with a name, or the distance table has fewer than _N_ × _N_ numbers | Complete the file                                 |
| `F:L: too many cities`         | The city table has more than 1000 cities                                                            | Use a smaller table                               |
| `F:L: duplicate city 'K'`      | Two cities have the same name, ignoring case                                                        | Rename one of them                                |
| `F:L: unexpected token 'K'`    | The distance table has more than _N_ × _N_ numbers                                                  | Remove the extra numbers, or check the city table |
| `unknown goal city 'G'`        | No city in the table is called _G_                                                                  | Check the spelling                                |
| `unknown start city 'C'`       | No city in the table is called _C_                                                                  | Check the spelling                                |
| `-:L: unknown start city 'K'`  | The city _K_ read from standard input is not in the table                                           | Check the spelling                                |
| `-:L: unexpected end of input` | Standard input was empty                                                                            | Type a city name, or give it as an argument       |
| `F: No such file or directory` | The data file _F_ does not exist                                                                    | Check the spelling and the current directory      |
| `F: Permission denied`         | You may not read _F_                                                                                | Check the permissions                             |
| `F: Is a directory`            | _F_ is a directory                                                                                  | Name a file instead                               |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                                                     | Correct the path                                  |
| `F: Input/output error`        | Any other failure to read _F_ (or `-`, standard input)                                              | Check the device or file system                   |
| `write error`                  | The output could not be written                                                                     | Free space or redirect the output elsewhere       |

Usage errors are written to standard error as two lines, and no file is read:

```text
$ dp-astar berlin prague
dp-astar: extra operand 'prague'
Try 'dp-astar --help' for more information.
```

| Message                                      | Cause                                                       | Fix                                           |
| :------------------------------------------- | :---------------------------------------------------------- | :-------------------------------------------- |
| `invalid option -- 'x'`                      | Unknown short option `-x`                                   | Check the option letter                       |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                          | Spell the option in full                      |
| `option requires an argument -- 'n'`         | `-n`, `-d`, or `-g` given without a value                   | Supply a value                                |
| `option '--names' requires an argument`      | `--names`, `--distances`, or `--goal` given without a value | Supply a value                                |
| `option '--trace' doesn't allow an argument` | `--trace=…`, `--prompt=…`, `--help=…`, or `--version=…`     | Remove the `=…`                               |
| `invalid argument '' for '-n'`               | An empty file name, or `-`, for a data file                 | Give a file name (`./-` for a file named `-`) |
| `invalid argument '' for '--goal'`           | An empty goal city                                          | Give a city name                              |
| `extra operand 'C'`                          | More than one start city                                    | Give one city                                 |

## EXAMPLES

Routes from two cities (the README of the textbook section gives 186 and 497 km; the data
files say 185 and 404):

```text
$ dp-astar prague
Optimal path to Vienna:
prague -> vienna
Total distance: 185 kilometers
$ dp-astar Berlin
Optimal path to Vienna:
berlin -> prague -> vienna
Total distance: 404 kilometers
```

Be asked for the city:

```text
$ dp-astar --prompt
Enter start city: Lisbon
Optimal path to Vienna:
lisbon -> madrid -> genoa -> trieste -> vienna
Total distance: 1968 kilometers
```

Watch the search:

```text
$ dp-astar --trace berlin
open berlin g=0 f=386
select berlin g=0 f=386
open bern g=628 f=1118 via berlin
open hamburg g=182 f=735 via berlin
open prague g=219 f=405 via berlin
open warsaw g=345 f=902 via berlin
select prague g=219 f=405
open munich g=393 f=657 via prague
open vienna g=404 f=404 via prague
select vienna g=404 f=404
Optimal path to Vienna:
berlin -> prague -> vienna
Total distance: 404 kilometers
```

A small map on which a closed city is reopened (`reopen-names.dat`, `reopen-dist.dat`):

```text
$ dp-astar -n reopen-names.dat -d reopen-dist.dat -g target -t origin
open origin g=0 f=0
select origin g=0 f=0
open alpha g=4 f=4 via origin
open beta g=1 f=11 via origin
select alpha g=4 f=4
open target g=14 f=14 via alpha
select beta g=1 f=11
reopen alpha g=2 f=2 via beta
select alpha g=2 f=2
update target g=12 f=12 via alpha
select target g=12 f=12
Optimal path to Target:
origin -> beta -> alpha -> target
Total distance: 12 kilometers
```

No roads lead out of Vienna:

```text
$ dp-astar --goal=lisbon vienna
No path from vienna to Lisbon.
```

## HELP OUTPUT

`dp-astar --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-astar [OPTION]... [CITY]
Find the shortest road route from CITY to Vienna with the A* search.

With no CITY, or when CITY is -, read the start city from standard input.
City names are matched without regard to ASCII case.  The cities and their
estimated distances to the goal are read from names.dat, and the road
distances from distance.dat, where 1000 means that there is no road.

Options:
  -n, --names=FILE      read the cities and estimates from FILE
                          (default names.dat)
  -d, --distances=FILE  read the road distances from FILE
                          (default distance.dat)
  -g, --goal=CITY       find a route to CITY instead of vienna
  -t, --trace           show every step of the search before the result
  -p, --prompt          write the prompt 'Enter start city: ' to standard
                          error before the start city is read
      --help            display this help and exit
      --version         output version information and exit
```

## VERSION OUTPUT

```text
dp-astar (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-astar` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
City names are compared by folding only the ASCII letters `A`–`Z` to `a`–`z`, the same in
every locale; numbers are always read and written with ASCII digits.

## PLATFORM NOTES

- **Windows:** output uses LF line endings, not CRLF. The data files are read as raw bytes,
  so the textbook's MS-DOS files work unchanged: CRLF line endings are accepted and the
  trailing Ctrl-Z bytes are ignored, but a Ctrl-Z byte in the middle of a file is ordinary
  data. At the prompt, type the city name and press Enter; Ctrl-Z followed by Enter ends the
  input without a city.
- **macOS / Linux:** at the prompt, Ctrl-D ends the input without a city.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-bfs-adj` and `dp-bfs-link` (project 47), uninformed breadth-first search;
`dp-phone` (project 31), which also reads a fixed data file from the textbook's disk;
`tsort(1)`.

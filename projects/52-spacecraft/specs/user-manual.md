# dp-ship — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-ship` 1.0.0 |
| Project | `52-spacecraft` — Object-Oriented Spacecraft Domain Modeling |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-52), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-ship** — model spacecraft and report their basics and trip times

## SYNOPSIS

```text
dp-ship [FILE]
dp-ship --help
dp-ship --version
```

## DESCRIPTION

`dp-ship` models spacecraft. Each ship has a name, a mass in kilograms, a velocity in
kilometers per hour, the distance of its trip in kilometers, and the number of astronauts it
holds. A ship's velocity can be adjusted up or down, but never below zero; its trip time is the
distance divided by the velocity, in hours.

### The textbook scenario

Without *FILE*, `dp-ship` replays the scenario of the textbook: it creates a ship with default
values, then MightyMite (mass 5000, velocity 63567, distance 560989, 4 astronauts), raises
MightyMite's velocity by 2000 and lowers it by 1000, and reports:

```text
$ dp-ship
??? has a mass of 0
and a velocity of 0 and holds 0 astronauts for a trip of 0 kilometers.

MightyMite has a mass of 5000
and a velocity of 63567 and holds 4 astronauts for a trip of 560989 kilometers.

MightyMite has a mass of 5000
and a velocity of 64567 and holds 4 astronauts for a trip of 560989 kilometers.

MightyMite requires 8.68848 hours for trip.
```

### Scripts

With *FILE*, `dp-ship` runs the script in that file instead (standard input when *FILE* is
`-`). A script has one command per line; words are separated by spaces or tabs. Empty lines are
ignored, and so is any line whose first word starts with `#`.

| Command | Meaning |
| :-- | :-- |
| `new ID` | Create a ship called *ID* with the default values: name `???`, mass, velocity, distance, and capacity 0 |
| `new ID MASS VEL DIST CAP NAME` | Create a ship called *ID* with mass *MASS*, velocity *VEL*, distance *DIST*, capacity *CAP*, and name *NAME* (the textbook's order) |
| `adjust ID DIFF` | Add *DIFF* (which may be negative) to the ship's velocity; a result below 0 becomes 0 |
| `print ID` | Report the ship's basics: two lines, then an empty line |
| `trip ID` | Report the hours the ship needs for its trip |

*ID* is the name the script uses for a ship (like a variable name); *NAME* is the name printed
in reports. Neither may contain spaces. *MASS*, *VEL*, and *DIST* are non-negative numbers,
written with digits, an optional sign, an optional decimal point, and an optional exponent
(`5000`, `0.25`, `1.2e9`); *DIFF* is such a number of either sign; *CAP* is a non-negative
whole number. Ship *IDs* and command names are case-sensitive.

A ship whose velocity is 0 cannot make its trip, and `trip` says so:

```text
MightyMite cannot make the trip at a velocity of 0.
```

Windows (CRLF) scripts work unchanged, and one or more Ctrl-Z bytes at the very end of a script
are ignored. The whole script is read before the first command runs; commands then run in
order, and the first invalid line stops the script.

### Numbers in reports

Masses, velocities, distances, and trip times are written with up to six significant digits,
like C's `%g` format: trailing zeros are dropped (`5000`, not `5000.000000`), and very large or
very small values use an exponent (`1234567` is written `1.23457e+06`, `0.00001` is written
`1e-05`). Capacities are written in full. Output is identical on every operating system.

## OPTIONS

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-ship` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--hel` is not accepted.
- `--` ends option processing, so `dp-ship -- -x` runs a script named `-x`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the scenario or the whole script ran, or help or version was printed |
| 1 | The script could not be read, or it contained an invalid line |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems in a script name the script (`-` for standard input) and the line number. Reports
printed before the problem are kept, and the exit status is 1:

```text
$ dp-ship bad.txt
MightyMite has a mass of 5000
and a velocity of 63567 and holds 4 astronauts for a trip of 560989 kilometers.

dp-ship: bad.txt:3: invalid number 'fast'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: unknown command 'N'` | Line *L* starts with a word that is not `new`, `adjust`, `print`, or `trip` | Check the spelling (commands are lowercase) |
| `S:L: extra argument 'X'` | Line *L* has more words than its command takes | Remove the surplus words |
| `S:L: missing argument for 'N'` | Line *L* has too few words for command *N* (`new` takes 1 or 6) | Supply every value |
| `S:L: ship 'I' already exists` | `new` reuses the *ID* of an existing ship | Choose another *ID* |
| `S:L: unknown ship 'I'` | No ship with *ID* *I* has been created | Create it with `new` first |
| `S:L: invalid number 'X'` | A mass, velocity, distance, or difference is not a number | Write it with digits, `.`, and an optional exponent |
| `S:L: invalid integer 'X'` | The capacity is not a whole number | Write it with digits only |
| `S:L: value out of range 'X'` | A mass, velocity, distance, or capacity is negative, or an adjustment makes the velocity too large to represent | Use a non-negative value, or a smaller adjustment |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The reports could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-ship fleet.txt clamp.txt
dp-ship: extra operand 'clamp.txt'
Try 'dp-ship --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | `dp-ship` has no short options |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Use `--help` or `--version` |
| `option '--help' doesn't allow an argument` | A value was given with `=` to `--help` or `--version` | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-ship` once per script |

## EXAMPLES

Replay the textbook scenario as a script:

```text
$ cat scenario.txt
# The textbook scenario as a script
new s1
print s1
new s2 5000 63567 560989 4 MightyMite
print s2
adjust s2 2000
adjust s2 -1000
print s2
trip s2
$ dp-ship scenario.txt | tail -1
MightyMite requires 8.68848 hours for trip.
```

Plan a probe's trip:

```text
$ printf 'new probe 721.9 61500.5 1.2e9 0 Voyager\nprint probe\ntrip probe\n' | dp-ship -
Voyager has a mass of 721.9
and a velocity of 61500.5 and holds 0 astronauts for a trip of 1.2e+09 kilometers.

Voyager requires 19512 hours for trip.
```

Bring a ship to a standstill and start again:

```text
$ dp-ship clamp.txt
MightyMite has a mass of 5000
and a velocity of 0 and holds 4 astronauts for a trip of 560989 kilometers.

MightyMite cannot make the trip at a velocity of 0.
MightyMite requires 2.24396e+06 hours for trip.
??? cannot make the trip at a velocity of 0.
```

Use the exit status in a script:

```sh
if dp-ship mission.txt > report.txt; then
    echo "mission planned"
fi
```

## HELP OUTPUT

`dp-ship --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-ship [OPTION]... [FILE]
Model spacecraft and report their basics and trip times.

With no FILE, run the textbook scenario.  Otherwise run the command script in
FILE (standard input when FILE is -), one command per line:
  new ID                          create ship ID with default values
  new ID MASS VEL DIST CAP NAME   create ship ID with the given values
  adjust ID DIFF                  add DIFF to the velocity (never below 0)
  print ID                        report the ship's basics
  trip ID                         report the time the ship needs for its trip
Empty lines and lines whose first word starts with # are ignored.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-ship (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-ship` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** scripts are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes
  at the very end of a script are ignored, but a Ctrl-Z byte anywhere else is part of a word
  (a line holding only a Ctrl-Z byte is an unknown command). Output uses LF line endings, not
  CRLF. Exponents always have at least two digits (`1e-05`), as on every other platform.
- **macOS / Linux:** in shells such as bash or zsh, quote ship names that contain `?`, `*`, or
  `$` when you type a script with `printf` or `echo`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-cars2` (project 28), modular design with records passed between functions; `dp-elephnt1`
(project 43), a dynamic data structure; `dp-koch` (project 51); `dp-kv` (project 09), a stateful
store; `bc(1)` for checking the arithmetic.

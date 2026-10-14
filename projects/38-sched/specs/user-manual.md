# dp-sched — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-sched` 1.0.0 |
| Project | `38-sched` — Greedy Interval Activity Scheduling |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-38), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-sched** — find a largest set of activities that do not overlap

## SYNOPSIS

```text
dp-sched FILE
dp-sched --help
dp-sched --version
```

## DESCRIPTION

`dp-sched` reads a list of activities from *FILE*, or from standard input when *FILE* is `-`,
and prints a largest possible set of them that can share one resource without overlapping:

```text
$ dp-sched sched.in
Optimal schedule:

    1    5
    5    7
    9   12
   13   16
```

The report is the heading `Optimal schedule:`, a blank line, and the chosen activities, each
printed exactly as its line appears in *FILE*, in order of finish time. A file with no
activities produces just the heading and the blank line.

### The input file

Each line describes one activity in two fixed columns:

| Columns | Contents |
| :-- | :-- |
| 1–5 | Start time, a whole number from 0 to 99999, padded with spaces |
| 6–10 | Finish time, a whole number from 0 to 99999, padded with spaces |

Every line must be exactly 10 bytes long, not counting its line ending, and the finish time must
be later than the start time. Numbers are normally right-justified (`   12`), but any padding
with spaces is accepted, as are a `+` sign and leading zeros. Lines may end with LF or CRLF, the
last line needs no line ending, and one or more Ctrl-Z bytes at the very end of the file (the
end-of-file mark of old MS-DOS data files) are ignored.

### How activities are chosen

An activity occupies the time from its start up to its finish, so an activity may begin at the
very moment another one finishes: `1 5` and `5 7` do not overlap. `dp-sched` sorts the
activities by finish time and walks through them once, taking every activity that starts no
earlier than the finish of the last one taken. This greedy rule always yields a schedule with
as many activities as possible.

When several activities finish at the same time, the one that comes first in the file is
considered first. So the same file always gives the same schedule, and you can express a
preference among equally good activities by their order in the file.

### Errors in the file

The whole file is checked before anything is printed. The first problem is reported with the
line number, and no schedule is printed:

```text
$ dp-sched bad.in
dp-sched: bad.in:3: invalid integer 'six'
```

## OPTIONS

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-sched` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--he` is not accepted.
- Exactly one *FILE* must be given.
- `--` ends option processing: `dp-sched -- -plan.in` reads the file `-plan.in`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the schedule, help, or version was printed |
| 1 | The file could not be read, or it contains a malformed line |
| 2 | Usage error: an invalid option, or a missing or unexpected argument |

## DIAGNOSTICS

Every problem is reported on standard error as one line, and the exit status is 1. Problems
with the data name the input (`-` for standard input) and the line number.

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid line length N, expected 10` | Line *L* is *N* bytes long without its line ending (a blank line has length 0) | Write exactly two 5-column fields; remove trailing spaces and blank lines |
| `S:L: missing start time` | Columns 1–5 of line *L* are blank | Fill in the start time |
| `S:L: missing finish time` | Columns 6–10 of line *L* are blank | Fill in the finish time |
| `S:L: invalid integer 'V'` | A field of line *L* holds *V*, which is not a whole number (a tab, a decimal point, letters) | Write the time in digits, padded with spaces |
| `S:L: value out of range 'V'` | A field of line *L* holds a negative number *V* | Use times from 0 to 99999 |
| `S:L: finish time is not later than start time` | The activity on line *L* ends when or before it starts | Correct the times |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other failure to read *F* | Check the device or file system |
| `write error` | The schedule could not be written to standard output | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; no file is read:

```text
$ dp-sched
dp-sched: missing operand
Try 'dp-sched --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` (`dp-sched` has none) | Remove it |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…` | Remove the `=…` |
| `missing operand` | No *FILE* given | Name the file of activities, or `-` for standard input |
| `extra operand 'F'` | More than one *FILE* | Schedule one file at a time |

## EXAMPLES

Schedule the textbook's nine activities (see the DESCRIPTION).

Equal finish times: the earlier line wins.

```text
$ cat ties.in
    1    2
    4    6
    2    6
    6    9
    0    3
$ dp-sched ties.in
Optimal schedule:

    1    2
    4    6
    6    9
```

Read the activities from a pipeline:

```sh
printf '    0   30\n   30   60\n   15   45\n' | dp-sched -
```

Count the activities chosen:

```sh
dp-sched requests.in | tail -n +3 | wc -l
```

## HELP OUTPUT

`dp-sched --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-sched [OPTION]... FILE
Find a largest set of activities that do not overlap.

Each line of FILE describes one activity: its start time in columns 1-5 and
its finish time in columns 6-10, as whole numbers from 0 to 99999 padded with
spaces.  An activity may start at the time another one finishes.  The
activities are sorted by finish time (equal finish times keep the order of the
file) and chosen greedily; the chosen lines are printed as they appear in
FILE.  When FILE is -, read standard input.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-sched (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-sched` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Times are always read with ASCII digits.

## PLATFORM NOTES

- **Windows:** files with CRLF line endings are read correctly, and the chosen lines are
  printed without their CR, so the report always ends lines with LF only. A Ctrl-Z byte at the
  very end of a file is ignored, but one on a line of its own followed by a line break is an
  error. Both `/` and `\` work as directory separators in file names.
- **All systems:** columns are counted in bytes; a TAB is not expanded to spaces and is not
  valid padding.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-phone` (project 31), which also reads fixed-width records and sorts them;
`sort(1)`, `cut(1)`.

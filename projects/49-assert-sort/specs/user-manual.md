# dp-assert-sort — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-assert-sort` 1.0.0 |
| Project | `49-assert-sort` — Formal Program Verification via Assertions & Loop Invariants |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-49), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-assert-sort** — sort integers by selection sort, checking assertions and the loop invariant

## SYNOPSIS

```text
dp-assert-sort [-t | --trace] [-f FAULT | --fault=FAULT] [FILE]
dp-assert-sort --help
dp-assert-sort --version
```

## DESCRIPTION

`dp-assert-sort` reads whole numbers from *FILE*, or from standard input when there is no
*FILE* or *FILE* is `-`, sorts them in ascending order, and prints them one per line.

```text
$ echo 5 4 3 2 1 | dp-assert-sort
1
2
3
4
5
```

### How the numbers are sorted

`dp-assert-sort` uses selection sort. For *n* numbers it makes *n* − 1 passes, numbered from
0. In pass *i* it finds the smallest of the numbers at positions *i* to *n* − 1 (the leftmost
one if several are equal), and swaps it with the number at position *i*. Positions are
counted from 0.

### What is checked

After finding the minimum in pass *i*, and before swapping, the tool asserts that its position
`min_ind` lies inside the array:

```text
min_ind >= 0 && min_ind < n
```

After the swap it asserts the **loop invariant** `sorted(a, i, n)`:

1. the numbers at positions 0 to *i* are in ascending order, and
2. no number after position *i* is smaller than the number at position *i*.

After the last pass, the invariant says that the whole list is sorted. The checks are made on
the actual numbers, in every pass, every time the tool runs.

If a check fails, `dp-assert-sort` names the pass, the assertion, and the numbers that violate
it, prints no sorted numbers, and exits with status 1:

```text
dp-assert-sort: assertion failed in pass 2: sorted(a, 2, 5) (a[3] = 3 < a[2] = 4)
```

The part in parentheses shows the first violation: here the number 3 at position 3 is smaller
than the number 4 at position 2. For the bounds assertion it shows the faulty position and the
length, for example `(min_ind = 5, n = 5)`.

### Watching the checks

With `--trace`, the tool writes one line to standard error after every invariant check that
holds, showing the pass, the position of the minimum, and the whole list after the swap:

```text
$ dp-assert-sort --trace textbook.txt
pass 0: min_ind = 4 in bounds; a = 1 4 3 2 5; sorted(a, 0, 5) holds
pass 1: min_ind = 3 in bounds; a = 1 2 3 4 5; sorted(a, 1, 5) holds
pass 2: min_ind = 2 in bounds; a = 1 2 3 4 5; sorted(a, 2, 5) holds
pass 3: min_ind = 3 in bounds; a = 1 2 3 4 5; sorted(a, 3, 5) holds
1
2
3
4
5
```

The sorted numbers go to standard output, so `dp-assert-sort --trace data.txt > sorted.txt`
shows the trace and saves only the numbers. (On a terminal the two streams may interleave
differently from what is shown here.)

### Injecting faults

`--fault=FAULT` breaks one step of the algorithm on purpose, so you can see the checks catch
it. *FAULT* is a fault *KIND*, optionally followed by `:` and a pass number:

| KIND | What goes wrong |
| :-- | :-- |
| `skip-swap` | The swap is left out. |
| `off-by-one` | The position one after the minimum is used instead of the minimum's own. |
| `search-from-next` | The search for the minimum starts at position *i* + 1 instead of *i*. |

`--fault=off-by-one` injects the fault in every pass; `--fault=off-by-one:2` only in pass 2.
A pass number beyond the last pass injects nothing. The same fault on the same input always
gives the same result.

A fault is reported only if it actually makes the list wrong. If the minimum is already in
place, skipping its swap does no harm, and every check holds:

```text
$ dp-assert-sort --fault=skip-swap:3 textbook.txt
1
2
3
4
5
```

### Numbers

Numbers are whole numbers from −9223372036854775808 to 9223372036854775807, written in decimal
digits with an optional `+` or `-` sign; leading zeros are allowed. They are separated by any
mix of spaces, tabs, and line breaks, so files with Windows (CRLF) line endings read the same
as any other. Each number is printed as a plain decimal: `+3` is printed as `3`, `0042` as
`42`, and `-0` as `0`.

All numbers are checked before sorting starts. The first entry that is not a valid number is
reported with its line number, and nothing is sorted. One or more Ctrl-Z bytes at the very end
of the input (the end-of-file mark of old MS-DOS data files) are ignored.

## OPTIONS

**`-t`, `--trace`**
: After every invariant check that holds, write a trace line to standard error.

**`-f FAULT`, `--fault=FAULT`**
: Inject the fault *FAULT* (`KIND` or `KIND:PASS`; see "Injecting faults"). If the option is
  given more than once, the last one counts.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-assert-sort` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--tr` is not accepted.
- Short options can be combined: `-tf skip-swap` means `-t -f skip-swap`.
- Options and the file name can be given in any order: `dp-assert-sort data.txt -t` works.
- `--` ends option processing, so `dp-assert-sort -- -t` reads a file named `-t`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the numbers were sorted with every check holding (an empty input is fine), or help or version was printed |
| 1 | An assertion failed, the input contained an invalid number, or the input could not be read |
| 2 | Usage error: an invalid option or fault, or more than one file |

## DIAGNOSTICS

A failed check is reported in one line; nothing is written to standard output:

```text
$ dp-assert-sort --fault=off-by-one textbook.txt
dp-assert-sort: assertion failed in pass 0: min_ind >= 0 && min_ind < n (min_ind = 5, n = 5)
```

Problems with the data name the input (`-` for standard input) and the line number:

```text
$ dp-assert-sort bad.txt
dp-assert-sort: bad.txt:3: invalid integer '0x9'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `assertion failed in pass I: min_ind >= 0 && min_ind < n (…)` | The position used in pass *I* is outside the list (only with `--fault`) | This is what the fault demonstrates |
| `assertion failed in pass I: sorted(a, I, N) (…)` | After pass *I* the invariant does not hold (only with `--fault`) | This is what the fault demonstrates |
| `S:L: invalid integer 'K'` | Entry *K* on line *L* is not a whole number, or is outside the 64-bit range | Write the number in digits only, without separators or decimals |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-assert-sort --fault=bogus textbook.txt
dp-assert-sort: invalid argument 'bogus' for '--fault'
Try 'dp-assert-sort --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-t` or `-f` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'f'` | `-f` was the last argument | Give a fault after `-f` |
| `option '--fault' requires an argument` | `--fault` was the last argument | Give a fault after `--fault` |
| `option '--trace' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `invalid argument 'V' for '--fault'` | *V* is not `KIND` or `KIND:PASS` with a known kind | Use `skip-swap`, `off-by-one`, or `search-from-next`, optionally with `:` and a pass number |
| `extra operand 'F'` | More than one file was named | Run `dp-assert-sort` once per file |

## EXAMPLES

Sort numbers from a file with Windows line endings, signs, and leading zeros:

```text
$ dp-assert-sort mixed.txt
-15
-7
0
0
3
3
12
42
```

Watch a fault that goes unnoticed for two passes:

```text
$ dp-assert-sort -t --fault=search-from-next textbook.txt
pass 0: min_ind = 4 in bounds; a = 1 4 3 2 5; sorted(a, 0, 5) holds
pass 1: min_ind = 3 in bounds; a = 1 2 3 4 5; sorted(a, 1, 5) holds
dp-assert-sort: assertion failed in pass 2: sorted(a, 2, 5) (a[3] = 3 < a[2] = 4)
```

Break only pass 1:

```text
$ dp-assert-sort --fault=off-by-one:1 textbook.txt
dp-assert-sort: assertion failed in pass 1: sorted(a, 1, 5) (a[2] = 3 < a[1] = 5)
```

Use the exit status in a script:

```sh
if dp-assert-sort numbers.txt > sorted.txt; then
    echo "sorted, every check held"
fi
```

## HELP OUTPUT

`dp-assert-sort --help` prints exactly the following text (every line ends in LF). The help
text is part of the specification (CONV-23):

```text
Usage: dp-assert-sort [OPTION]... [FILE]
Sort integers by selection sort, checking assertions after every pass.

With no FILE, or when FILE is -, read standard input.  The input is a list of
whole numbers separated by whitespace.  After each pass i the tool asserts
that the index of the minimum is within the array and that a[0..i] is sorted
with every later element at least a[i].  The sorted numbers are written one
per line.  A failed assertion is reported and the exit status is 1.

FAULT is KIND or KIND:PASS, where KIND is skip-swap (omit the swap),
off-by-one (use the index after the minimum), or search-from-next (start the
search for the minimum at i+1).  The fault is injected in pass PASS (counted
from 0), or in every pass when PASS is omitted.

Options:
  -t, --trace        write one line to standard error for every invariant check
                       that holds
  -f, --fault=FAULT  inject the fault FAULT into the sort
      --help         display this help and exit
      --version      output version information and exit
```

## VERSION OUTPUT

```text
dp-assert-sort (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-assert-sort` ignores all environment variables, including locale settings (`LANG`,
`LC_ALL`). Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **All platforms:** a failed assertion is an ordinary error report with exit status 1. It
  never aborts the program, opens a crash dialog, or writes a core dump, and the checks cannot
  be switched off by building the tool in a "release" configuration.
- **Windows:** data files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z
  bytes at the very end of a file are ignored, but a Ctrl-Z byte in the middle of a file is an
  error, not an end-of-file mark. Output uses LF line endings, not CRLF. End keyboard input
  with Ctrl-Z followed by Enter.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-divide` (project 50), which recovers from an arithmetic fault instead of stopping at it;
`dp-chk-sort` (project 17), which checks whether a list is already sorted;
`dp-sort-host` (project 34) and `dp-sort-bench` (project 35), other sorting tools;
`sort(1)`.

# dp-stats — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-stats` 1.0.0 |
| Project | `15-stats` — Single-Pass Streaming Statistical Summary |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-15), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-stats** — summarize a stream of real numbers in a single pass

## SYNOPSIS

```text
dp-stats [FILE]
dp-stats --help
dp-stats --version
```

## DESCRIPTION

`dp-stats` reads real numbers from *FILE*, or from standard input when there is no *FILE* or
*FILE* is `-`, until the end of the input. It then prints how many numbers it read, their
maximum, minimum, sum, and mean, and their population variance and standard deviation:

```text
3 data items read
maximum value read = 30.000000
minimum value read = 10.000000
sum of all values read = 60.000000
mean = 20.000000
variance = 66.666667
standard deviation = 8.164966
```

If the input contains no numbers, the whole report is the single line `0 data items read`.
The first line says `data items` whatever the count, so a single number gives
`1 data items read`.

### One pass, constant memory

`dp-stats` looks at each number once and keeps only five running values: the count, the
largest and smallest number so far, the sum, and the sum of the squares. It never stores the
numbers themselves, so its memory use is the same for ten numbers and for a hundred million.

### The statistics

With *N* numbers, sum *S*, and sum of squares *Q*:

- the mean is *S* / *N*;
- the **population** variance is *Q* / *N* − mean² (dividing by *N*, not *N* − 1);
- the standard deviation is the square root of the variance.

Because the variance subtracts two nearly equal numbers, rounding can make it come out a tiny
bit below zero when all numbers are equal (three copies of 0.1 do this). `dp-stats` then uses
zero, so the standard deviation is `0.000000`, never an error.

### Reproducible results

The calculation is defined exactly: the numbers are added in input order in IEEE 754 double
precision, each square is rounded before it is added, and every printed value is rounded
correctly to six decimal places (an exact half rounds to the even digit: `0.0234375` prints
as `0.023438`, `0.0078125` as `0.007812`). Every conforming implementation therefore prints
the same digits on every computer. Large values are printed in full, without an exponent, and
a value that rounds to zero is printed as `0.000000`, never `-0.000000`.

### Numbers

Numbers are written in decimal with an optional sign, an optional decimal point, and an
optional exponent: `42`, `-5.0`, `.5`, `3.`, `+2.5e1`, and `1.25E+1` are all valid. The
decimal separator is always a point, whatever your locale. Numbers are separated by any mix
of spaces, tabs, and line breaks, so several numbers may share a line, and files with Windows
(CRLF) line endings read the same as any other. One or more Ctrl-Z bytes at the very end of
the input (the end-of-file mark of old MS-DOS data files) are ignored.

Everything else is an error: a decimal comma (`4,5`), digit grouping, `inf`, `nan`,
hexadecimal numbers, or a number too large for double precision (`1e309`). Numbers whose
squares or sum of squares would be too large (beyond about 1.34 × 10¹⁵⁴) are an error too.
`dp-stats` reports the first such entry with its line number and prints no summary at all,
because a summary of part of the data would be misleading.

At the keyboard, type the numbers and end the input with **Ctrl-D** on Linux and macOS, or
**Ctrl-Z** followed by **Enter** in a Windows console; the report appears then.

## OPTIONS

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-stats` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--he` is not accepted.
- `--` ends option processing, so `dp-stats -- -x` reads a file named `-x`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the report was printed (an input without numbers is fine), or help or version was printed |
| 1 | The input could not be read, it contained an invalid number, or the sums overflowed |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. No report
is printed, and the exit status is 1:

```text
$ dp-stats bad.txt
dp-stats: bad.txt:3: invalid number '4,5'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid number 'K'` | Entry *K* on line *L* is not a number, or is too large for double precision | Write the number with digits, a point, and an optional exponent |
| `S:L: arithmetic overflow at 'K'` | The square of *K*, or the sum of squares including it, is too large | Rescale the data (for example, change the unit) |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The report could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-stats data.txt three.txt
dp-stats: extra operand 'three.txt'
Try 'dp-stats --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | `dp-stats` has no short options |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--help' doesn't allow an argument` | A value was given with `=` to `--help` or `--version` | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-stats` once per file, or concatenate the files first |

## EXAMPLES

Summarize three numbers:

```text
$ printf '10.0 20.0 30.0\n' | dp-stats
3 data items read
maximum value read = 30.000000
minimum value read = 10.000000
sum of all values read = 60.000000
mean = 20.000000
variance = 66.666667
standard deviation = 8.164966
```

Read a file with negative numbers, exponents, and Windows line endings:

```text
$ dp-stats data.txt
7 data items read
maximum value read = 25.000000
minimum value read = -20.000000
sum of all values read = 15.250000
mean = 2.178571
variance = 168.977041
standard deviation = 12.999117
```

Identical values have no spread, even when rounding is involved:

```text
$ printf '0.1\n0.1\n0.1\n' | dp-stats
3 data items read
maximum value read = 0.100000
minimum value read = 0.100000
sum of all values read = 0.300000
mean = 0.100000
variance = 0.000000
standard deviation = 0.000000
```

Summarize several files together:

```sh
cat january.txt february.txt march.txt | dp-stats > quarter.txt
```

## HELP OUTPUT

`dp-stats --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-stats [OPTION]... [FILE]
Print summary statistics of the real numbers in FILE.

With no FILE, or when FILE is -, read standard input.  Numbers are separated
by whitespace and read in a single pass until the end of the input.  The
report gives the count, maximum, minimum, sum, mean, population variance
(sum of squares / N - mean * mean), and standard deviation, each real number
with six digits after the decimal point.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-stats (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-stats` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a number).
- **All platforms:** results do not depend on the processor (x86-64 or ARM), the compiler, or
  the locale; a report produced on one system can be compared byte for byte with one produced
  on another.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-average` and `dp-chk-sort` (project 17), other single-pass filters over numbers;
`dp-wc` (project 04); `awk(1)`, `datamash(1)`, `sort(1)`.

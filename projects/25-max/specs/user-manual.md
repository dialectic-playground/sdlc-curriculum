# dp-max — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-max` 1.0.0 |
| Project | `25-max` — Variadic Functions & Dynamic Arity Processing |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-25), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-max** — print the largest of one to four integers

## SYNOPSIS

```text
dp-max [-p | --prompt] [FILE]
dp-max --help
dp-max --version
```

## DESCRIPTION

`dp-max` reads one to four integers from *FILE*, or from standard input when there is no *FILE*
or *FILE* is `-`, until the end of the input, and prints the largest of them:

```text
Maximum integer = 42
```

### Integers

The integers are whole numbers from −9223372036854775808 to 9223372036854775807, written in
decimal digits with an optional `+` or `-` sign; leading zeros are allowed. They are separated
by any mix of spaces, tabs, and line breaks, so they may share a line or be spread over
several, and files with Windows (CRLF) line endings read the same as any other. The result is
printed as a plain number: `+07` is printed as `7`. One or more Ctrl-Z bytes at the very end of
the input (the end-of-file mark of old MS-DOS data files) are ignored.

`dp-max` reads the whole input before it prints anything. It prints no result, and exits with
status 1, if the input holds no integer, more than four entries, or an entry that is not an
integer (a decimal point, a letter, digit grouping, or a number outside the range above). The
first problem is reported with its line number.

The integers cannot be given on the command line; `dp-max -5` is an invalid option. Use
`echo -5 3 | dp-max` instead.

### Working interactively

Type the integers, then end the input with **Ctrl-D** on Linux and macOS, or **Ctrl-Z**
followed by **Enter** in a Windows console. With `--prompt`, `dp-max` first says what to do:

```text
$ dp-max --prompt
Enter one to four integers
generate EOF when done
15 42 8
^D
Maximum integer = 42
```

The prompt is written to standard error, so `dp-max --prompt > max.txt` saves only the result.

## OPTIONS

**`-p`, `--prompt`**
: Before reading, write the two lines `Enter one to four integers` and
  `generate EOF when done` to standard error.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-max` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-max values.txt -p` works.
- `--` ends option processing, so `dp-max -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the result was printed, or help or version was printed |
| 1 | The input could not be read, or it did not hold one to four valid integers |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Nothing is
written to standard output, and the exit status is 1:

```text
$ dp-max five.txt
dp-max: five.txt:2: too many values '5'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | Entry *K* on line *L* is not a whole number in the 64-bit range | Write the integer in digits only, without separators or decimals |
| `S:L: too many values 'K'` | *K*, on line *L*, is a fifth entry | Give at most four integers |
| `S:L: unexpected end of input` | The input holds no integer; *L* is the last line | Give at least one integer |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The result could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-max readme.txt one.txt
dp-max: extra operand 'one.txt'
Try 'dp-max --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x`, or a negative number given as an argument | Use `-p`; give the integers on standard input or in a file |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Put the integers in one file |

## EXAMPLES

The largest of three integers:

```text
$ echo 15 42 8 | dp-max
Maximum integer = 42
```

All negative, on two lines:

```text
$ printf -- '-10 -2\n-50 -4\n' | dp-max
Maximum integer = -2
```

The extremes of the range are exact:

```text
$ echo -9223372036854775808 9223372036854775807 | dp-max
Maximum integer = 9223372036854775807
```

Use the exit status in a script:

```sh
if largest=$(dp-max values.txt); then
    echo "$largest"
fi
```

## HELP OUTPUT

`dp-max --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-max [OPTION]... [FILE]
Print the largest of one to four integers.

Read the integers from FILE, or from standard input when FILE is absent or -,
until the end of the input.  They are whole numbers from -9223372036854775808
to 9223372036854775807, separated by whitespace.

Options:
  -p, --prompt    write a prompt to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-max (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-max` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF. Results are the same 64-bit values as on Linux and
  macOS.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing an integer).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-stats` (project 15), which summarizes any number of values; `dp-average` and `dp-chk-sort`
(project 17), other filters over integer streams; `sort(1)`, `awk(1)`.

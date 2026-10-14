# dp-convert — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-convert` 1.0.0 |
| Project | `12-convert` — Interactive Length Unit Conversion |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-12), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-convert** — convert lengths in yards to feet and inches

## SYNOPSIS

```text
dp-convert [-p | --prompt] [FILE]
dp-convert --help
dp-convert --version
```

## DESCRIPTION

`dp-convert` reads lengths in whole yards from *FILE*, or from standard input when there is no
*FILE* or *FILE* is `-`. For each length it prints three lines: the length in yards, in feet,
and in inches.

```text
5 yd =
15 ft
180 in
```

A **negative number** ends the input. `dp-convert` then prints

```text
*** END OF PROGRAM ***
```

and exits with status 0. The negative number is not converted, and nothing after it is read,
so a file may carry notes after its end marker.

### Lengths

Lengths are whole numbers from 0 to 256204778801521550 yards, written in decimal digits with an
optional `+` or `-` sign; leading zeros are allowed. (256204778801521550 is the largest length
whose number of inches, 36 times the yards, fits in a 64-bit integer.) Lengths are separated by
any mix of spaces, tabs, and line breaks, so several lengths may share a line, and files with
Windows (CRLF) line endings read the same as any other. The length is printed as a plain
number: `+3` is printed as `3`, `007` as `7`, and `-0` (which is zero, not negative) as `0`.

Everything else is an error: a decimal point (`2.5`), a unit (`yd`), digit grouping (`1,760`),
or a length larger than 256204778801521550. `dp-convert` reports the first such entry with its
line number and stops; the lines already printed for earlier lengths remain valid.

If the input ends before a negative number has been read, `dp-convert` reports
`unexpected end of input` and exits with status 1, without printing the closing banner. This
catches files that were cut short.

One or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data
files) are ignored.

### Working interactively

`dp-convert` prints each conversion as soon as you finish typing a length (press Enter or
Space), and it exits as soon as you type a negative number and press Enter. With `--prompt`, it
asks for each length:

```text
$ dp-convert --prompt
Enter next length 5
5 yd =
15 ft
180 in
Enter next length 0
0 yd =
0 ft
0 in
Enter next length -1
*** END OF PROGRAM ***
```

The prompts are written to standard error, so `dp-convert --prompt > lengths.out` saves only
the results.

## OPTIONS

**`-p`, `--prompt`**
: Before each length is read, write `Enter next length ` to standard error. A prompt is also
  written before the negative number that ends the input.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-convert` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-convert lengths.txt -p` works.
- `--` ends option processing, so `dp-convert -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: a negative number ended the input, or help or version was printed |
| 1 | The input could not be read, contained an invalid length, or ended before a negative number |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Results
printed before the problem are kept, and the exit status is 1:

```text
$ dp-convert bad.txt
10 yd =
30 ft
360 in
dp-convert: bad.txt:2: invalid integer '2.5'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | Entry *K* on line *L* is not a whole number, or lies outside −9223372036854775808 … 9223372036854775807 | Write the length in digits only, without units, separators, or decimals |
| `S:L: value out of range 'K'` | Entry *K* on line *L* is larger than 256204778801521550 | Enter a smaller length |
| `S:L: unexpected end of input` | The input ended (on line *L*) before a negative number | End the input with a negative number such as `-1` |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-convert lengths.txt mixed.txt
dp-convert: extra operand 'mixed.txt'
Try 'dp-convert --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-convert` once per file |

## EXAMPLES

Convert two lengths:

```text
$ printf '5\n0\n-1\n' | dp-convert
5 yd =
15 ft
180 in
0 yd =
0 ft
0 in
*** END OF PROGRAM ***
```

Lengths may share lines, carry signs or leading zeros, and anything after the end marker is
ignored:

```text
$ printf '+3 007 1760\n-0\n100 -5 notes follow\n' | dp-convert
3 yd =
9 ft
108 in
7 yd =
21 ft
252 in
1760 yd =
5280 ft
63360 in
0 yd =
0 ft
0 in
100 yd =
300 ft
3600 in
*** END OF PROGRAM ***
```

A file without an end marker is reported:

```text
$ printf '12\n36\n' > nosentinel.txt
$ dp-convert nosentinel.txt
12 yd =
36 ft
432 in
36 yd =
108 ft
1296 in
dp-convert: nosentinel.txt:3: unexpected end of input
```

Use the exit status in a script:

```sh
if dp-convert lengths.txt > lengths.out; then
    echo "all lengths converted"
fi
```

## HELP OUTPUT

`dp-convert --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-convert [OPTION]... [FILE]
Convert lengths in yards to feet and inches.

With no FILE, or when FILE is -, read standard input.  Lengths are whole
numbers of yards from 0 to 256204778801521550, separated by whitespace.  A
negative number ends the input: it prints '*** END OF PROGRAM ***', and
nothing after it is read.

Options:
  -p, --prompt    write the prompt 'Enter next length ' to standard error
                    before each length is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-convert (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-convert` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** at the keyboard, end a session normally with a negative number. If you end the
  input instead (Ctrl-Z followed by Enter), `dp-convert` reports `unexpected end of input`.
  Data files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the
  very end of a file are ignored, but a Ctrl-Z byte in the middle of a file is an error, not an
  end-of-file mark. Output uses LF line endings, not CRLF.
- **macOS / Linux:** Ctrl-D at the start of a line ends the input; as on Windows, that is
  reported as `unexpected end of input` unless a negative number came first.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-taxes` (project 13), which reads values until the end of the input instead of until a
sentinel; `dp-kinder` (project 11); `units(1)`, `awk(1)`.

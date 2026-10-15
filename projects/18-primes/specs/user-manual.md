<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-primes — User Manual](#dp-primes--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The bound](#the-bound)
    - [Working interactively](#working-interactively)
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

# dp-primes — User Manual

| Field         | Value                                                    |
| :------------ | :------------------------------------------------------- |
| Product       | `dp-primes` 1.0.0                                        |
| Project       | `18-primes` — Prime Number Generation via Trial Division |
| Applies to    | Linux, macOS, Windows                                    |
| Specification | `SRS.md` (SRS-18), `shared/CLI-CONVENTIONS.md`           |

---

## NAME

**dp-primes** — list the prime numbers up to a bound

## SYNOPSIS

```text
dp-primes [-c | --count] [-p | --prompt] [FILE]
dp-primes --help
dp-primes --version
```

## DESCRIPTION

`dp-primes` reads a whole number _n_ from _FILE_, or from standard input when there is no
_FILE_ or _FILE_ is `-`, and lists every prime number less than or equal to _n_: a header line,
a blank line, and the primes in ascending order, one per line.

```text
$ echo 15 | dp-primes
	Primes <= 15:

2
3
5
7
11
13
```

The header begins with one TAB character. A prime is a whole number greater than 1 that is
divisible only by 1 and itself, so for any _n_ below 2 — including 0 and negative numbers — the
list is empty and only the header and the blank line are printed.

### The bound

_n_ is the first entry in the input. It is a whole number written in decimal digits with an
optional `+` or `-` sign; leading zeros are allowed, and the header shows the plain number
(`+015` gives `Primes <= 15:`). It may be preceded by spaces, tabs, and line breaks. Everything
after it is ignored, so `dp-primes` answers as soon as you press Enter.

The largest accepted bound is **10000000**, for which `dp-primes` lists 664579 primes in about
a second. A larger bound, a missing bound, or an entry that is not a whole number (`15.0`,
`fifteen`, `1,000`) is reported with its line number; nothing is printed to standard output.

One or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data
files) are ignored, and files with Windows (CRLF) line endings read like any other.

### Working interactively

With `--prompt`, `dp-primes` greets you and asks for _n_, as the original textbook program did:

```text
$ dp-primes --prompt
	This program lists all primes <= n

Input n: 10
	Primes <= 10:

2
3
5
7
```

The greeting and the prompt are written to standard error, so `dp-primes --prompt > primes.txt`
saves only the list.

## OPTIONS

**`-c`, `--count`**
: Print only the number of primes less than or equal to _n_, on one line, without the header.

**`-p`, `--prompt`**
: Before _n_ is read, write the banner `This program lists all primes <= n` (indented by a TAB
and followed by a blank line) and the prompt `Input n:o standard error.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-primes` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Flags can be bundled: `-cp` means `-c -p`.
- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-primes bound.txt -c` works.
- `--` ends option processing, so `dp-primes -- -c` reads a file named `-c`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                        |
| :----- | :--------------------------------------------------------------------------------------------- |
| 0      | Success: the list or count was printed (an empty list is fine), or help or version was printed |
| 1      | The input could not be read, or the bound was missing, invalid, or above 10000000              |
| 2      | Usage error: an invalid option or more than one file                                           |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number, and
nothing is written to standard output:

```text
$ dp-primes bad.txt
dp-primes: bad.txt:2: invalid integer '15.0'
```

| Message                        | Cause                                                                                                   | Fix                                          |
| :----------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------- |
| `S:L: unexpected end of input` | The input ends before any bound was given; _L_ is the last line                                         | Supply a bound                               |
| `S:L: invalid integer 'K'`     | Entry _K_ on line _L_ is not a whole number, or lies outside −9223372036854775808 … 9223372036854775807 | Write the bound in digits only               |
| `S:L: value out of range 'K'`  | Entry _K_ on line _L_ is larger than 10000000                                                           | Use a bound of at most 10000000              |
| `F: No such file or directory` | _F_ does not exist                                                                                      | Check the spelling and the current directory |
| `F: Permission denied`         | You may not read _F_                                                                                    | Check the file's permissions                 |
| `F: Is a directory`            | _F_ is a directory                                                                                      | Name a file instead                          |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                                                         | Correct the path                             |
| `F: Input/output error`        | Any other read failure                                                                                  | Check the device or file system              |
| `write error`                  | The list could not be written (for example, the disk is full)                                           | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-primes fifteen.txt hundred.txt
dp-primes: extra operand 'hundred.txt'
Try 'dp-primes --help' for more information.
```

| Message                                      | Cause                                                   | Fix                           |
| :------------------------------------------- | :------------------------------------------------------ | :---------------------------- |
| `invalid option -- 'x'`                      | Unknown short option `-x`                               | Use `-c` or `-p`              |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                      | Spell the option in full      |
| `option '--count' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`               |
| `extra operand 'F'`                          | More than one file was named                            | Run `dp-primes` once per file |

## EXAMPLES

List the primes up to 20:

```text
$ echo 20 | dp-primes
	Primes <= 20:

2
3
5
7
11
13
17
19
```

A bound below 2 gives an empty list:

```text
$ echo -7 | dp-primes
	Primes <= -7:

```

Count the primes up to the limit:

```text
$ echo 10000000 | dp-primes --count
664579
```

Print the primes without the header (two lines are skipped):

```sh
echo 1000 | dp-primes | tail -n +3
```

## HELP OUTPUT

`dp-primes --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-primes [OPTION]... [FILE]
List every prime number less than or equal to n.

With no FILE, or when FILE is -, read standard input.  n is the first whole
number in the input; anything after it is ignored.  n may be negative, but it
must not exceed 10000000.  The output is a header line (a TAB, then
'Primes <= n:'), a blank line, and the primes in ascending order, one per
line.

Options:
  -c, --count     write only the number of primes <= n
  -p, --prompt    write the program banner and the prompt 'Input n: ' to
                    standard error before n is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-primes (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-primes` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** the list ends its lines with LF, not CRLF, and the header's TAB is written as a
  TAB byte. Data files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes
  at the very end of a file are ignored, but a Ctrl-Z byte directly after the number and before
  more input makes the entry invalid. Pressing Ctrl-Z then Enter before typing a number ends
  the input and is reported as `unexpected end of input`.
- **macOS / Linux:** pressing Ctrl-D before typing a number ends the input and is reported as
  `unexpected end of input`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-calendar` (project 19), another program from the same chapter of the textbook;
`dp-wc` (project 04), to count the lines of a list; `factor(1)`, `seq(1)`,
`primes(6)` (BSD games).

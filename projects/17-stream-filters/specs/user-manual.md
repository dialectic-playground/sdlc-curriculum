<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-average, dp-chk-sort — User Manual](#dp-average-dp-chk-sort--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [dp-average](#dp-average)
    - [dp-chk-sort](#dp-chk-sort)
    - [Numbers](#numbers)
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

# dp-average, dp-chk-sort — User Manual

| Field         | Value                                                            |
| :------------ | :--------------------------------------------------------------- |
| Products      | `dp-average` 1.0.0, `dp-chk-sort` 1.0.0                          |
| Project       | `17-stream-filters` — Stream Filtering & Monotonicity Validation |
| Applies to    | Linux, macOS, Windows                                            |
| Specification | `SRS.md` (SRS-17), `shared/CLI-CONVENTIONS.md`                   |

---

## NAME

**dp-average** — print the average of the positive numbers in a stream

**dp-chk-sort** — check whether a stream of integers is in non-decreasing order

## SYNOPSIS

```text
dp-average [FILE]
dp-chk-sort [FILE]
dp-average --help | --version
dp-chk-sort --help | --version
```

## DESCRIPTION

Both tools read numbers from _FILE_, or from standard input when there is no _FILE_ or _FILE_
is `-`, and print a one-line answer.

### dp-average

`dp-average` reads real numbers until the end of the input and prints the average of those
greater than zero:

```text
$ printf -- '-5.0 0.0 10.0 20.0\n' | dp-average
average = 15.000000
```

Zero and negative numbers are checked (a typo among them is still an error) but otherwise
ignored. If there is no number greater than zero — including when the input is empty — the
answer is `no positive numbers read`. Either way the exit status is 0.

The numbers are added in input order in IEEE 754 double precision, and the average is rounded
correctly to six decimal places (an exact half rounds to the even digit: an average of
`0.0078125` prints as `0.007812`), so every conforming implementation prints the same digits
on every computer.

### dp-chk-sort

`dp-chk-sort` reads integers and checks that each is greater than or equal to the one before
it. Equal neighbors are fine, and an empty input or a single integer is sorted. The answer is
printed and is also the exit status:

| Output                           | Exit status | Meaning                                                                       |
| :------------------------------- | :---------- | :---------------------------------------------------------------------------- |
| `file is sorted`                 | 0           | No integer is less than the one before it                                     |
| `file is not sorted`             | 1           | Some integer is less than the one before it                                   |
| (a diagnostic on standard error) | 2           | Something went wrong: a bad option, an unreadable file, or an invalid integer |

`dp-chk-sort` stops as soon as it reads the first integer that is out of order: it prints
`file is not sorted` and exits at once, without reading the rest of the input. Anything after
that integer — even text that is not a number — is never looked at. At the keyboard, the
answer appears as soon as you type the out-of-order number and press Space or Enter. When the
input is a pipe, the program writing into it may then be told that its reader has gone away
(for example, `yes 5 | dp-chk-sort` never stops, but `(echo 9; yes 5) | dp-chk-sort` stops at
once).

### Numbers

`dp-average` reads real numbers written in decimal with an optional sign, an optional decimal
point, and an optional exponent: `42`, `-5.0`, `.5`, `3.`, and `2.5e1` are valid. The decimal
separator is always a point, whatever your locale. `dp-chk-sort` reads whole numbers with an
optional sign, from −9223372036854775808 to 9223372036854775807; leading zeros are allowed, so
`05`, `+5`, and `5` are equal.

Numbers are separated by any mix of spaces, tabs, and line breaks, so several numbers may share
a line, and files with Windows (CRLF) line endings read the same as any other. One or more
Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data files) are
ignored.

Everything else is an error: a decimal comma or a fraction such as `1/2`, digit grouping,
`inf`, `nan`, hexadecimal numbers, a real number too large for double precision (`1e309`), or —
for `dp-chk-sort` — a number with a decimal point or exponent, or one outside the range above.
The tool reports the first such entry with its line number and prints no answer, because an
answer about part of the data would be misleading. `dp-average` also reports a sum too large
for double precision (`arithmetic overflow`).

End keyboard input with **Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by **Enter** in
a Windows console.

## OPTIONS

Both tools accept only:

**`--help`**
: Display the tool's help text below and exit with status 0.

**`--version`**
: Display the tool's version line and exit with status 0.

### Option syntax

Both tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--he` is not accepted.
- `--` ends option processing, so `dp-chk-sort -- -x` reads a file named `-x`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

`dp-average`:

| Status | Meaning                                                                                                   |
| :----- | :-------------------------------------------------------------------------------------------------------- |
| 0      | Success: the answer was printed (`no positive numbers read` is an answer), or help or version was printed |
| 1      | The input could not be read, it contained an invalid number, or the sum overflowed                        |
| 2      | Usage error: an invalid option or more than one file                                                      |

`dp-chk-sort` (like `sort -c`):

| Status | Meaning                                                                           |
| :----- | :-------------------------------------------------------------------------------- |
| 0      | The input is sorted, or help or version was printed                               |
| 1      | The input is not sorted                                                           |
| 2      | Trouble: a usage error, an unreadable input, an invalid integer, or a write error |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. No answer
is printed:

```text
$ dp-average bad.txt
dp-average: bad.txt:4: invalid number '1/2'
$ dp-chk-sort badint.txt
dp-chk-sort: badint.txt:2: invalid integer '3.5'
```

| Message                           | Cause                                                                                      | Fix                                                             |
| :-------------------------------- | :----------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| `S:L: invalid number 'K'`         | (`dp-average`) Entry _K_ on line _L_ is not a number, or is too large for double precision | Write the number with digits, a point, and an optional exponent |
| `S:L: arithmetic overflow at 'K'` | (`dp-average`) Adding _K_ made the sum too large                                           | Rescale the data (for example, change the unit)                 |
| `S:L: invalid integer 'K'`        | (`dp-chk-sort`) Entry _K_ on line _L_ is not a whole number in the 64-bit range            | Write the integer in digits only                                |
| `F: No such file or directory`    | _F_ does not exist                                                                         | Check the spelling and the current directory                    |
| `F: Permission denied`            | You may not read _F_                                                                       | Check the file's permissions                                    |
| `F: Is a directory`               | _F_ is a directory                                                                         | Name a file instead                                             |
| `F: Not a directory`              | Part of the path _F_ is a file, not a directory                                            | Correct the path                                                |
| `F: Input/output error`           | Any other read failure                                                                     | Check the device or file system                                 |
| `write error`                     | The answer could not be written (for example, the disk is full)                            | Free space or redirect the output elsewhere                     |

These exit with status 1 from `dp-average` and 2 from `dp-chk-sort`.

Usage errors are written to standard error as two lines; nothing is read, nothing is written to
standard output, and the exit status is 2:

```text
$ dp-average numbers.txt nonpos.txt
dp-average: extra operand 'nonpos.txt'
Try 'dp-average --help' for more information.
```

| Message                                     | Cause                                                 | Fix                                                        |
| :------------------------------------------ | :---------------------------------------------------- | :--------------------------------------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                             | The tools have no short options                            |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                    | Spell the option in full                                   |
| `option '--help' doesn't allow an argument` | A value was given with `=` to `--help` or `--version` | Remove the `=…`                                            |
| `extra operand 'F'`                         | More than one file was named                          | Run the tool once per file, or concatenate the files first |

## EXAMPLES

Average the positive readings, ignoring placeholders:

```text
$ printf -- '-1.0 -10.0 0.0\n' | dp-average
no positive numbers read
$ printf '0.1\r\n0.2\r\n-7e3\r\n' | dp-average
average = 0.150000
```

Check a file and use the answer in a script:

```sh
if dp-chk-sort ids.txt; then
    echo "ids.txt is sorted"
else
    case $? in
        1) echo "ids.txt is not sorted" ;;
        *) echo "could not check ids.txt" ;;
    esac
fi
```

Nothing after the first out-of-order number is read:

```text
$ printf '1 3\n8 4 junk\n' | dp-chk-sort
file is not sorted
$ echo $?
1
```

Equal neighbors and the 64-bit extremes are in order:

```text
$ echo '-9223372036854775808 -1 +0 -0 05 +5 9223372036854775807' | dp-chk-sort
file is sorted
```

## HELP OUTPUT

`dp-average --help` and `dp-chk-sort --help` print exactly the following texts (every line
ends in LF). The help texts are part of the specification (CONV-23).

`dp-average --help`:

```text
Usage: dp-average [OPTION]... [FILE]
Print the average of the positive numbers in FILE.

With no FILE, or when FILE is -, read standard input.  Numbers are real
numbers separated by whitespace and are read until the end of the input.
Numbers less than or equal to zero are checked but otherwise ignored.  The
average is written with six digits after the decimal point.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

`dp-chk-sort --help`:

```text
Usage: dp-chk-sort [OPTION]... [FILE]
Check whether the integers in FILE are in non-decreasing order.

With no FILE, or when FILE is -, read standard input.  Integers are separated
by whitespace.  Print 'file is sorted' and exit with status 0 if no integer
is less than the one before it; otherwise print 'file is not sorted' as soon
as the first such integer is read, stop reading, and exit with status 1.
Any error exits with status 2.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-average (dialectic-playground) 1.0.0
dp-chk-sort (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

Both tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF. In PowerShell, use `$LASTEXITCODE` to read
  `dp-chk-sort`'s answer.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a number). When `dp-chk-sort` stops early, the command feeding its pipe may receive
  SIGPIPE; in a shell with `set -o pipefail`, the pipeline's status then reflects that
  command, not `dp-chk-sort`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build both tools
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-stats` (project 15), which summarizes all the numbers in a stream; `dp-grep` (project 05)
and `dp-diff` (project 07), which also answer through their exit status; `sort(1)` (`sort -c`,
`sort -n`), `awk(1)`.

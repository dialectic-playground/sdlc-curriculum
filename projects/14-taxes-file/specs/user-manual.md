<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-taxes-file — User Manual](#dp-taxes-file--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The tax rule](#the-tax-rule)
    - [Incomes](#incomes)
    - [The report file is all or nothing](#the-report-file-is-all-or-nothing)
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

# dp-taxes-file — User Manual

| Field         | Value                                                                |
| :------------ | :------------------------------------------------------------------- |
| Product       | `dp-taxes-file` 1.0.0                                                |
| Project       | `14-taxes-file` — Batch File-Based Progressive Income Tax Calculator |
| Applies to    | Linux, macOS, Windows                                                |
| Specification | `SRS.md` (SRS-14), `shared/CLI-CONVENTIONS.md`                       |

---

## NAME

**dp-taxes-file** — compute the progressive income tax for a file of incomes

## SYNOPSIS

```text
dp-taxes-file [-i FILE | --input=FILE] [-o FILE | --output=FILE]
dp-taxes-file --help
dp-taxes-file --version
```

## DESCRIPTION

`dp-taxes-file` reads incomes from the file `incomes.dat` in the current directory, computes
the tax on each, and writes the report to the file `out.dat`, replacing whatever it contained.
It prints nothing when it succeeds. Use `-i` and `-o` to choose other files; the name `-`
means standard input or standard output.

The report has two lines per income, in the order of the input:

```text
Income = 4500 greenbacks
Tax = 1350 greenbacks
```

### The tax rule

- An income **below 6000** greenbacks is taxed at **30%**.
- An income of **6000 or more** is taxed at **60%** of the whole income.

The tax is rounded down to a whole number of greenbacks: 30% of 5999 is 1799.7, so the tax is 1799. The calculation is exact for every income `dp-taxes-file` accepts, up to
9223372036854775807; it never suffers from floating-point rounding. The rule and the report
format are exactly those of `dp-taxes` (project 13).

### Incomes

Incomes are whole numbers from 0 to 9223372036854775807, written in decimal digits with an
optional `+` or `-` sign; leading zeros are allowed. They are separated by any mix of spaces,
tabs, and line breaks, so several incomes may share a line, and files with Windows (CRLF) line
endings read the same as any other. The income is printed as a plain number: `+4500` is printed
as `4500` and `007` as `7`. One or more Ctrl-Z bytes at the very end of the input (the
end-of-file mark of old MS-DOS data files) are ignored.

Everything else is an error: a decimal point (`4500.50`), digit grouping (`12,000`), a currency
sign, a negative income, or a number larger than 9223372036854775807.

### The report file is all or nothing

`dp-taxes-file` reads and checks the **whole** input before it opens the report file. If the
input file is missing or unreadable, or any income in it is invalid, the report file is not
created and not changed: a previous `out.dat` keeps its contents. Only when every income is
valid is the report file created (or emptied) and written. An input with no incomes produces an
empty report file.

Because the input has been read completely first, the input and the report may even be the
same file: `dp-taxes-file -i data.txt -o data.txt` replaces the incomes in `data.txt` with
their report.

## OPTIONS

**`-i FILE`, `--input=FILE`**
: Read the incomes from _FILE_ instead of `incomes.dat`. `-i -` reads standard input.

**`-o FILE`, `--output=FILE`**
: Write the report to _FILE_ instead of `out.dat`, creating it or replacing its contents.
`-o -` writes the report to standard output instead of a file.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-taxes-file` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-iq3.dat`, `-i q3.dat`, `--input=q3.dat`, and
  `--input q3.dat` are equivalent.
- Long options must be spelled out in full; `--in` is not accepted.
- If an option is given more than once, the last one wins.
- File names are never given as plain arguments: `dp-taxes-file q3.dat` is an error; write
  `dp-taxes-file -i q3.dat`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                         |
| :----- | :---------------------------------------------------------------------------------------------- |
| 0      | Success: the report was written, or help or version was printed                                 |
| 1      | The input could not be read, it contained an invalid income, or the report could not be written |
| 2      | Usage error: an invalid option or value, or an unexpected argument                              |

## DIAGNOSTICS

Every problem is reported on standard error as one line, and the exit status is 1. Problems
with the data name the input (`-` for standard input) and the line number:

```text
$ dp-taxes-file -i bad.dat
dp-taxes-file: bad.dat:3: invalid integer '12,000'
```

| Message                        | Cause                                                                                           | Fix                                                                |
| :----------------------------- | :---------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| `S:L: invalid integer 'K'`     | Entry _K_ on line _L_ of input _S_ is not a whole number, or is larger than 9223372036854775807 | Write the income in digits only, without separators or decimals    |
| `S:L: value out of range 'K'`  | Entry _K_ on line _L_ of input _S_ is negative                                                  | Correct the income                                                 |
| `F: No such file or directory` | The input _F_ does not exist, or a directory in the report path _F_ does not exist              | Check the spelling and the current directory; create the directory |
| `F: Permission denied`         | You may not read the input _F_, or may not create or write the report _F_                       | Check the permissions                                              |
| `F: Is a directory`            | _F_ is a directory                                                                              | Name a file instead                                                |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                                                 | Correct the path                                                   |
| `F: Input/output error`        | Any other failure to read _F_ or to write _F_ (for example, the disk is full)                   | Check the device or file system                                    |
| `write error`                  | The report could not be written to standard output                                              | Free space or redirect the output elsewhere                        |

If the report file cannot be written completely (for example, the disk fills up), its contents
are incomplete; run the tool again once the problem is fixed.

Usage errors are written to standard error as two lines; no file is read or written:

```text
$ dp-taxes-file incomes.dat
dp-taxes-file: extra operand 'incomes.dat'
Try 'dp-taxes-file --help' for more information.
```

| Message                                     | Cause                                             | Fix                        |
| :------------------------------------------ | :------------------------------------------------ | :------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                         | Use `-i` or `-o`           |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                | Spell the option in full   |
| `option requires an argument -- 'i'`        | `-i` or `-o` given without a file name            | Supply a file name         |
| `option '--input' requires an argument`     | `--input` or `--output` given without a file name | Supply a file name         |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…`                       | Remove the `=…`            |
| `invalid argument '' for '-i'`              | An empty file name                                | Give a non-empty file name |
| `extra operand 'F'`                         | A file name given without `-i` or `-o`            | Use `-i F` or `-o F`       |

## EXAMPLES

The default batch run (`incomes.dat` holds `4500`, `6000`, and `12000`):

```text
$ dp-taxes-file
$ cat out.dat
Income = 4500 greenbacks
Tax = 1350 greenbacks
Income = 6000 greenbacks
Tax = 3600 greenbacks
Income = 12000 greenbacks
Tax = 7200 greenbacks
```

Show the report instead of writing a file:

```text
$ dp-taxes-file -o -
Income = 4500 greenbacks
Tax = 1350 greenbacks
Income = 6000 greenbacks
Tax = 3600 greenbacks
Income = 12000 greenbacks
Tax = 7200 greenbacks
```

Use explicit files, or a pipeline:

```sh
dp-taxes-file --input=2026-q3.dat --output=2026-q3.rpt
printf '5000\n6000\n' | dp-taxes-file -i - -o - | less
```

A bad input leaves the previous report alone:

```text
$ dp-taxes-file -i bad.dat
dp-taxes-file: bad.dat:3: invalid integer '12,000'
$ echo $?
1
```

Use the exit status in a script:

```sh
if dp-taxes-file -i today.dat -o today.rpt; then
    mail -s "tax report" office < today.rpt
fi
```

## HELP OUTPUT

`dp-taxes-file --help` prints exactly the following text (every line ends in LF). The help
text is part of the specification (CONV-23):

```text
Usage: dp-taxes-file [OPTION]...
Compute the progressive income tax for every income in an input file and
write the report to an output file.

Incomes are whole numbers from 0 to 9223372036854775807, separated by
whitespace.  An income below 6000 greenbacks is taxed at 30%, any other
income at 60%; the tax is rounded down to a whole number.  The whole input is
checked before the output file is opened: if the input cannot be read or
contains an invalid income, the output file is not created or changed.

Options:
  -i, --input=FILE    read the incomes from FILE (default incomes.dat);
                        - means standard input
  -o, --output=FILE   write the report to FILE, replacing its contents
                        (default out.dat); - means standard output
      --help          display this help and exit
      --version       output version information and exit
```

## VERSION OUTPUT

```text
dp-taxes-file (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-taxes-file` ignores all environment variables, including locale settings (`LANG`,
`LC_ALL`). Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** the report file has LF line endings, not CRLF, so it is byte-identical to one
  written on Linux or macOS; current editors, including Notepad, display it correctly. Input
  files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end
  of a file are ignored, but a Ctrl-Z byte in the middle of a file is an error. Both `/` and
  `\` work as directory separators in file names.
- **macOS / Linux:** the report file is created with the default permissions given by your
  `umask`. An existing report file keeps its permissions when it is replaced.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-taxes` (project 13), the interactive version that reads a stream and prints each result
immediately; `dp-kv` (project 09), which also writes a file; `awk(1)`.

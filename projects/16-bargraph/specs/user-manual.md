<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-bargraph — User Manual](#dp-bargraph--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Input format](#input-format)
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

# dp-bargraph — User Manual

| Field         | Value                                                |
| :------------ | :--------------------------------------------------- |
| Product       | `dp-bargraph` 1.0.0                                  |
| Project       | `16-bargraph` — ASCII Comic Book Bar Graph Generator |
| Applies to    | Linux, macOS, Windows                                |
| Specification | `SRS.md` (SRS-16), `shared/CLI-CONVENTIONS.md`       |

---

## NAME

**dp-bargraph** — draw a bar graph of titled values

## SYNOPSIS

```text
dp-bargraph [FILE]
dp-bargraph --help
dp-bargraph --version
```

## DESCRIPTION

`dp-bargraph` reads _records_ from _FILE_, or from standard input when _FILE_ is absent or `-`.
Each record is two lines: a **title**, then a **value**. For every record it prints the title
on one line and, on the next line, a bar of asterisks: one `*` for every 2 units of the value,
rounded down. A value of 0 or 1 gives an empty bar line.

```text
$ dp-bargraph bargraph.in
Detective Comics
**********************************************
Action Comics
*********************************************
Marvel Comics
*************************************
Superman
***********************************
Whiz Comics
*********************
```

### Input format

- **Lines** end with a line feed (LF) or with CR LF; the two are treated the same. The last
  line does not need a line ending.
- A **title** is the whole line, printed exactly as written: spaces at the start, in the
  middle, and at the end are kept, and so are accented letters in any encoding. A title may be
  empty.
- A **value** is a whole number from 0 to 10000 on a line of its own. Spaces and tabs around the
  number are allowed, as are a leading `+` and leading zeros (`+9`, `007`). Anything else on the
  line — a second word, a decimal point, a negative number — is an error.
- **Blank lines at the end** of the input are ignored. A blank line anywhere else counts as a
  line: in a title position it is an empty title, and in a value position it is an error.
- A run of **Ctrl-Z** bytes (`0x1A`) at the very end of the input, as written by old MS-DOS
  editors, is ignored.

An empty input, or one holding only blank lines, produces no output.

## OPTIONS

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-bargraph` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full.
- `--` ends option processing, so `dp-bargraph -- -data.txt` reads a file named `-data.txt`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                         |
| :----- | :-------------------------------------------------------------- |
| 0      | Success: every record was drawn, or help or version was printed |
| 1      | The file could not be read, or the data contains an error       |
| 2      | Usage error: an invalid option or more than one _FILE_          |

## DIAGNOSTICS

Errors in the data name the input and the line, and are written to standard error after the
bars of the records before the error:

```text
$ dp-bargraph badvalue.txt
Superman
***********************************
dp-bargraph: badvalue.txt:4: invalid integer 'forty-two'
```

Standard input is named `-`. Nothing of the faulty record, and nothing after it, is printed.

| Message                                | Cause                                                                                                              | Fix                                     |
| :------------------------------------- | :----------------------------------------------------------------------------------------------------------------- | :-------------------------------------- |
| `FILE:LINE: invalid integer 'TEXT'`    | The value line is not a single whole number (_TEXT_ is the line without surrounding spaces; `''` for a blank line) | Put just the number on the line         |
| `FILE:LINE: value out of range 'TEXT'` | The value is negative or larger than 10000                                                                         | Use a value from 0 to 10000             |
| `FILE:LINE: unexpected end of input`   | The input ends after a title, without its value                                                                    | Add the value line, or remove the title |
| `FILE: No such file or directory`      | _FILE_ does not exist                                                                                              | Check the name                          |
| `FILE: Is a directory`                 | _FILE_ is a directory                                                                                              | Name a file                             |
| `FILE: Permission denied`              | _FILE_ cannot be read                                                                                              | Check its permissions                   |

Usage errors are written to standard error as two lines; nothing is read and nothing is written
to standard output:

```text
$ dp-bargraph prices.txt more.txt
dp-bargraph: extra operand 'more.txt'
Try 'dp-bargraph --help' for more information.
```

| Message                                     | Cause                              | Fix                      |
| :------------------------------------------ | :--------------------------------- | :----------------------- |
| `invalid option -- 'x'`                     | Unknown short option               | Remove it                |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option | Spell the option in full |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…`        | Remove the `=…`          |
| `extra operand 'more.txt'`                  | More than one _FILE_               | Graph one file at a time |

## EXAMPLES

Graph the textbook's data from standard input:

```sh
dp-bargraph < bargraph.in
```

Titles keep their spaces; values 0 and 1 give empty bars:

```text
$ printf '  Spaced  Title  \n75\nZero\n0\n' | dp-bargraph
  Spaced  Title
*************************************
Zero

```

Use the exit status in a script:

```sh
if dp-bargraph prices.txt > graph.txt; then
    echo "graph written"
fi
```

## HELP OUTPUT

`dp-bargraph --help` prints exactly the following text (every line ends in LF). The help text
is part of the specification (CONV-23):

```text
Usage: dp-bargraph [OPTION]... [FILE]
Draw a bar graph: for each record, print its title, then a bar of one '*' for
every 2 units of its value.

With no FILE, or when FILE is -, read standard input.  Lines alternate between
a title and a value; a value is a whole number from 0 to 10000 on a line of
its own.  Blank lines after the last record are ignored.

Options:
      --help       display this help and exit
      --version    output version information and exit
```

## VERSION OUTPUT

```text
dp-bargraph (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-bargraph` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).

## PLATFORM NOTES

- **Windows:** input is read as bytes, so CRLF files and files ending in Ctrl-Z give the same
  graph as on Linux and macOS, and the output uses LF line endings, not CRLF. In Windows
  PowerShell 5.1, text piped into a native program is re-encoded first; pass the file name
  (`dp-bargraph prices.txt`) to graph the bytes stored on disk.
- **All platforms:** titles are copied byte for byte. To see accented titles correctly, use a
  terminal whose encoding matches the file.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-bargraph2` (project 20), which draws the same graph; `dp-stats` (project 15);
`dp-cat` (project 02); `awk(1)`.

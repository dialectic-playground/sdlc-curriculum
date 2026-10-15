<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-page — User Manual](#dp-page--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [What counts as a line](#what-counts-as-a-line)
    - [The text is never changed](#the-text-is-never-changed)
    - [No empty pages](#no-empty-pages)
    - [Several files](#several-files)
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

# dp-page — User Manual

| Field         | Value                                          |
| :------------ | :--------------------------------------------- |
| Product       | `dp-page` 1.0.0                                |
| Project       | `36-page` — Stream Text Pagination Utility     |
| Applies to    | Linux, macOS, Windows                          |
| Specification | `SRS.md` (SRS-36), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-page** — break text into numbered pages for printing

## SYNOPSIS

```text
dp-page [-l N | --lines=N] [FILE]...
dp-page --help
dp-page --version
```

## DESCRIPTION

`dp-page` copies the text of the *FILE*s, or of standard input when there is no _FILE_ or a
_FILE_ is `-`, to standard output in pages. Each page consists of:

1. the header line `Page     N` — the word `Page`, five spaces, and the page number;
2. an empty line;
3. the next 52 lines of the text, exactly as they were read;
4. a form feed character (byte `0x0C`), which makes a printer eject the sheet.

The next page's header follows the form feed directly, and the output ends with the form feed
of the last page. The last page holds whatever lines remain, from 1 to 52.

### What counts as a line

A line ends with a newline (LF). Nothing else ends a line: carriage returns (CR) of Windows
line endings, tabs, form feeds, NUL bytes, and Ctrl-Z bytes are simply copied as part of the
line. An empty line counts like any other. If the text does not end with a newline, its last
line is copied without one, and the form feed follows it directly.

### The text is never changed

`dp-page` only _adds_ the headers and form feeds. Deleting them from the output gives back the
input exactly, byte for byte.

### No empty pages

`dp-page` starts a page only when there is at least one more line to put on it. An empty
input produces no output at all, and a text whose length is an exact multiple of 52 lines ends
with a full page, not with an empty one.

### Several files

All the *FILE*s are paginated as one continuous text, as if they had been joined with `dp-cat`
first: the page numbers continue from file to file, and pages are not restarted at the start
of a file. If a file does not end with a newline, its last line runs on into the first line of
the next file, exactly as `dp-cat` would join them.

## OPTIONS

**`-l N`, `--lines=N`**
: Put _N_ lines of text on each page instead of 52. _N_ is a whole number from 1 to
9223372036854775807, written in digits only. The header and the empty line after it are not
counted. If the option is given more than once, the last one counts.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-page` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--line` is not accepted.
- The value may be attached or separate: `-l3`, `-l 3`, `--lines=3`, and `--lines 3` are the
  same.
- Options and file names can be given in any order: `dp-page notes.txt -l 40` works.
- `--` ends option processing, so `dp-page -- -l` reads a file named `-l`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                     |
| :----- | :------------------------------------------------------------------------------------------ |
| 0      | Success: every input was paginated (an empty input is fine), or help or version was printed |
| 1      | At least one file could not be read; the others were still paginated                        |
| 2      | Usage error: an invalid option or page length                                               |

## DIAGNOSTICS

A file that cannot be read is reported, and `dp-page` goes on with the next file:

```text
$ dp-page missing.txt notes.txt > notes.prn
dp-page: missing.txt: No such file or directory
```

| Message                        | Cause                                                          | Fix                                          |
| :----------------------------- | :------------------------------------------------------------- | :------------------------------------------- |
| `F: No such file or directory` | _F_ does not exist                                             | Check the spelling and the current directory |
| `F: Permission denied`         | You may not read _F_                                           | Check the file's permissions                 |
| `F: Is a directory`            | _F_ is a directory                                             | Name a file instead                          |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                | Correct the path                             |
| `F: Input/output error`        | Any other read failure                                         | Check the device or file system              |
| `write error`                  | The pages could not be written (for example, the disk is full) | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-page -l 0 notes.txt
dp-page: invalid argument '0' for '-l'
Try 'dp-page --help' for more information.
```

| Message                                     | Cause                                                   | Fix                                       |
| :------------------------------------------ | :------------------------------------------------------ | :---------------------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                               | Use `-l`                                  |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                      | Spell the option in full                  |
| `option requires an argument -- 'l'`        | `-l` was given without a number                         | Add the number of lines                   |
| `option '--lines' requires an argument`     | `--lines` was given without a number                    | Add the number of lines                   |
| `invalid argument 'V' for '-l'`             | _V_ is not a whole number from 1 to 9223372036854775807 | Give a positive number of lines in digits |
| `option '--help' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                           |

## EXAMPLES

Paginate a report for the printer:

```sh
dp-page report.txt > report.prn
```

The page layout, shown with `od -c` (`\f` is the form feed) for three lines on pages of two:

```text
$ printf 'alpha\nbeta\ngamma\n' | dp-page -l 2 | od -c
0000000   P   a   g   e                       1  \n  \n   a   l   p   h
0000020   a  \n   b   e   t   a  \n  \f   P   a   g   e
0000040       2  \n  \n   g   a   m   m   a  \n  \f
0000053
```

Paginate two files as one document of 40-line pages:

```sh
dp-page --lines=40 chapter1.txt chapter2.txt > book.prn
```

Count the pages of a file (each page ends with exactly one inserted form feed, provided the
file itself contains none):

```sh
dp-page notes.txt | tr -cd '\f' | dp-wc -c
```

## HELP OUTPUT

`dp-page --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-page [OPTION]... [FILE]...
Break the concatenation of the FILEs into numbered pages for printing.

With no FILE, or when FILE is -, read standard input.  Each page starts with
the header line 'Page     N' (five spaces before the page number) and a blank
line, holds the next 52 input lines exactly as read, and ends with a form
feed character.  A last line without a newline is copied without one.  No
page is written for an empty input.

Options:
  -l, --lines=N   put N input lines on each page instead of 52
                    (1 to 9223372036854775807)
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-page (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-page` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
It never decodes the text, so files in any encoding are paginated the same way.

## PLATFORM NOTES

- **Windows:** files are read as raw bytes, so CRLF line endings are copied unchanged and a
  Ctrl-Z byte is copied like any other byte instead of ending the file. Output is written in
  binary mode: headers end in LF, not CRLF. Redirect the output to a file (`> out.prn`) rather
  than viewing it in a console, which may show the form feed as a symbol. In Windows
  PowerShell 5.1, piping text into or out of a native program re-encodes it; use `cmd.exe`
  redirection or PowerShell 7 to keep the bytes exact.
- **macOS / Linux:** a terminal usually shows the form feed as a line break or ignores it;
  use `od -c` or `less` to see it.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-cat` (project 02), which joins files the same way; `dp-head`, `dp-tail` (project 03);
`dp-wc` (project 04); `dp-wrap` (project 27), which wraps long lines before
pagination; `pr(1)`, `lp(1)`, `lpr(1)`.

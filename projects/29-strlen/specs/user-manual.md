<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-strlen — User Manual](#dp-strlen--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Characters and bytes](#characters-and-bytes)
    - [How the length is found](#how-the-length-is-found)
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

# dp-strlen — User Manual

| Field         | Value                                             |
| :------------ | :------------------------------------------------ |
| Product       | `dp-strlen` 1.0.0                                 |
| Project       | `29-strlen` — String Length from First Principles |
| Applies to    | Linux, macOS, Windows                             |
| Specification | `SRS.md` (SRS-29), `shared/CLI-CONVENTIONS.md`    |

---

## NAME

**dp-strlen** — print the length of strings or of input lines

## SYNOPSIS

```text
dp-strlen [-b | --bytes] STRING...
dp-strlen [-b | --bytes] [-f FILE | --file=FILE]
dp-strlen --help
dp-strlen --version
```

## DESCRIPTION

`dp-strlen` prints the length of each _STRING_ given on the command line, one number per line,
in order:

```text
$ dp-strlen '' a 'hello world' 'ANSI C'
0
1
11
6
```

With no _STRING_, `dp-strlen` reads standard input — or the file _FILE_ named with `-f` — and
prints the length of each line instead. A line is the text before a line feed; the text after
the last line feed, if there is any, is a line too. The line feed is not part of the line, and
neither is one carriage return (CR) just before it, so a file with Windows (CRLF) line endings
gives the same lengths as one with LF endings. An empty line has length 0, and an empty input
prints nothing.

### Characters and bytes

Lengths are counted in **characters**, by the same rule as `dp-wc -m`: each UTF-8 character
counts 1, and so does each byte that is not part of a valid UTF-8 sequence. Nothing depends on
how a terminal would display the text: a wide Chinese character, a combining accent, a tab,
and a NUL byte each count 1.

With `-b`, lengths are counted in **bytes**:

```text
$ dp-strlen Zoë 日本語 🙂
3
3
1
$ dp-strlen -b Zoë 日本語 🙂
4
9
4
```

Every byte sequence has a length, so `dp-strlen` never rejects its input: a damaged or binary
file is measured by the same rules.

### How the length is found

`dp-strlen` finds every length the way the classic C `strlen` function does: it starts at the
first byte and steps through the string, one character (or one byte) at a time, counting the
steps until it reaches the end. Unlike C's `strlen`, the end of a line is its line feed or the
end of the input, not a NUL byte, so lines that contain NUL bytes are measured in full. Lines
are measured as they are read and are never held in memory, so lines and files of any size can
be measured, and at the keyboard each length appears as soon as you press Enter.

One Ctrl-Z byte or more at the very end of the input (the end-of-file mark of old MS-DOS text
files) is ignored.

## OPTIONS

**`-f FILE`, `--file=FILE`**
: Read lines from _FILE_ instead of standard input. The _FILE_ `-` means standard input. No
_STRING_ may be given together with `-f`.

**`-b`, `--bytes`**
: Count bytes instead of characters.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-strlen` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be bundled: `-bf notes.txt` means `-b -f notes.txt`.
- Long options must be spelled out in full; `--byte` is not accepted.
- Options and strings can be given in any order: `dp-strlen Zoë -b` counts bytes.
- If `-f` is given more than once, the last one counts.
- `--` ends option processing, so `dp-strlen -- -b` prints `2`, the length of the string `-b`.
- A _STRING_ `-` is just a one-character string; to read standard input explicitly, use
  `-f -`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                             |
| :----- | :-------------------------------------------------------------------------------------------------- |
| 0      | Success: every string or line was measured (an empty input is fine), or help or version was printed |
| 1      | The input file could not be read                                                                    |
| 2      | Usage error: an invalid option, or strings given together with `-f`                                 |

## DIAGNOSTICS

| Message                        | Cause                                                           | Fix                                          |
| :----------------------------- | :-------------------------------------------------------------- | :------------------------------------------- |
| `F: No such file or directory` | _F_ does not exist                                              | Check the spelling and the current directory |
| `F: Permission denied`         | You may not read _F_                                            | Check the file's permissions                 |
| `F: Is a directory`            | _F_ is a directory                                              | Name a file instead                          |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                 | Correct the path                             |
| `F: Input/output error`        | Any other read failure                                          | Check the device or file system              |
| `write error`                  | The output could not be written (for example, the disk is full) | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-strlen -f lines.txt extra
dp-strlen: extra operand 'extra'
Try 'dp-strlen --help' for more information.
```

| Message                                      | Cause                                                   | Fix                                                             |
| :------------------------------------------- | :------------------------------------------------------ | :-------------------------------------------------------------- |
| `invalid option -- 'x'`                      | Unknown short option `-x`                               | Use `-f` or `-b`; put `--` before a string that starts with `-` |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                      | Spell the option in full                                        |
| `option requires an argument -- 'f'`         | `-f` was the last argument                              | Name the file                                                   |
| `option '--file' requires an argument`       | `--file` was the last argument                          | Name the file                                                   |
| `invalid argument '' for '-f'`               | The file name is empty                                  | Name the file                                                   |
| `option '--bytes' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                                                 |
| `extra operand 'X'`                          | Strings were given together with `-f`                   | Measure strings and files in separate runs                      |

## EXAMPLES

Line lengths of a file:

```text
$ dp-strlen -f lines.txt
5
0
11
6
19
```

Find the lines of a file that are longer than 72 characters, with their line numbers:

```sh
dp-strlen -f notes.txt | awk '$1 > 72 { print NR ": " $1 }'
```

Check a field limit in bytes in a script:

```sh
if [ "$(dp-strlen -b "$name")" -gt 32 ]; then
    echo "name too long for the 32-byte field"
fi
```

## HELP OUTPUT

`dp-strlen --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-strlen [OPTION]... [STRING]...
Print the length of each STRING, or of each line of the input.

With no STRING, print the length of each line of standard input, or of FILE
with -f (the FILE - is standard input).  The LF that ends a line is not
counted, and neither is one CR before it.  Lengths count UTF-8 characters;
each byte of an invalid sequence counts as one character.  With -b, lengths
count bytes.

Options:
  -f, --file=FILE   read lines from FILE instead of standard input
  -b, --bytes       count bytes instead of characters
      --help        display this help and exit
      --version     output version information and exit
```

## VERSION OUTPUT

```text
dp-strlen (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-strlen` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Characters are always counted with the same UTF-8 rule, whatever the locale or console code
page.

## PLATFORM NOTES

- **Windows:** command-line strings are taken as Unicode and measured in their UTF-8 form, so
  `dp-strlen 🙂` prints `1` (not 2, as a UTF-16 length would). Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is an ordinary character. Output uses LF line endings,
  not CRLF. End keyboard input with Ctrl-Z followed by Enter. In Windows PowerShell 5.1, text
  piped into a native program is re-encoded before `dp-strlen` sees it, which can change
  non-ASCII byte lengths; use a file with `-f` to measure exact bytes.
- **macOS / Linux:** command-line strings are measured as the bytes the shell passes. End
  keyboard input with Ctrl-D at the start of a line.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-wc` (project 04), whose `-m` counts characters by the same rule and whose `-L` gives the
longest line; `dp-wrap` (project 27) and `dp-reverse` (project 33), which measure strings by the
same rule; `wc(1)`, `expr(1)`, `awk(1)`.

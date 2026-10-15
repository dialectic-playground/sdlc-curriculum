<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-wrap — User Manual](#dp-wrap--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The line length](#the-line-length)
    - [How lines are filled](#how-lines-are-filled)
    - [How words are measured](#how-words-are-measured)
    - [Words that do not fit](#words-that-do-not-fit)
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

# dp-wrap — User Manual

| Field         | Value                                                |
| :------------ | :--------------------------------------------------- |
| Product       | `dp-wrap` 1.0.0                                      |
| Project       | `27-line-wrap` — Greedy Word-Wrapping Text Formatter |
| Applies to    | Linux, macOS, Windows                                |
| Specification | `SRS.md` (SRS-27), `shared/CLI-CONVENTIONS.md`       |

---

## NAME

**dp-wrap** — fill words into lines no longer than a given length

## SYNOPSIS

```text
dp-wrap [-w WIDTH | --width=WIDTH] [-b | --bytes] [FILE]
dp-wrap --help
dp-wrap --version
```

## DESCRIPTION

`dp-wrap` reads words from _FILE_, or from standard input when there is no _FILE_ or _FILE_ is
`-`, and writes them to standard output in lines no longer than the _line length_. A word is
any run of characters without spaces, tabs, or line breaks. The words keep their order; the
way they were laid out in the input does not matter, so runs of spaces, tabs, and blank lines
all disappear.

### The line length

Without `-w`, the first word of the input is the line length, as in the original program:

```text
$ cat fox.txt
20
The quick brown fox jumps over the lazy dog
$ dp-wrap fox.txt
The quick brown fox
jumps over the lazy
dog
```

The line length must be a whole number from 1 to 9223372036854775807. With `-w WIDTH` (or
`--width=WIDTH`) the line length is given on the command line instead, and the first word of
the input is ordinary text.

### How lines are filled

Words are placed one at a time. The first word starts the first line. Each later word goes on
the current line, after one space, if the line, the space, and the word together are no longer
than the line length; otherwise the word starts a new line. A line that reaches the line length
exactly is full: the next word always starts a new line. Every line ends with a line feed, and
no line has spaces at its start or end. An input without words produces no output.

### How words are measured

Lengths are counted in **characters**, by the same rule as `dp-wc -m`: each UTF-8 character
counts 1, and so does each byte that is not part of a valid UTF-8 sequence. So `café` is 4 long
and `🙂` is 1 long. Nothing depends on how a terminal would display the text: a wide Chinese
character, a combining accent, and a tab each count 1.

With `-b`, lengths are counted in **bytes** instead, so `café` is 5 long and `🙂` is 4 long.
Use this when the result must fit a field limited in bytes.

### Words that do not fit

A word longer than the line length cannot fit on any line. `dp-wrap` reports it on standard
error, still writes it on a line of its own, and carries on with the rest of the text; the exit
status is then 1:

```text
$ dp-wrap long.txt
Short
words,
then
supercalifragilistic,
and short
words
again.
dp-wrap: long.txt:2: word length exceeds line length 'supercalifragilistic,'
```

One Ctrl-Z byte or more at the very end of the input (the end-of-file mark of old MS-DOS text
files) is ignored. Files with Windows (CRLF) line endings read the same as any other.

## OPTIONS

**`-w WIDTH`, `--width=WIDTH`**
: Use _WIDTH_ as the line length. _WIDTH_ is written in digits only and is at least 1. The first
word of the input is then text, not a line length.

**`-b`, `--bytes`**
: Measure words in bytes instead of characters.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-wrap` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be bundled: `-bw3` means `-b -w 3`. The value of `-w` may follow directly
  (`-w12`) or as the next argument (`-w 12`); the value of `--width` may follow `=` or come as
  the next argument.
- Long options must be spelled out in full; `--wid` is not accepted.
- Options and the file name can be given in any order: `dp-wrap notes.txt -w 72` works.
- If `-w` is given more than once, the last one counts.
- `--` ends option processing, so `dp-wrap -- -w` reads a file named `-w`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                     |
| :----- | :-------------------------------------------------------------------------------------------------------------------------- |
| 0      | Success: every word was placed and none was too long (an input without words is fine), or help or version was printed       |
| 1      | A word was longer than the line length, the line length in the input was missing or invalid, or the input could not be read |
| 2      | Usage error: an invalid option or _WIDTH_, or more than one file                                                            |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. A word
that is too long is reported, written anyway, and wrapping continues. A problem with the line
length at the start of the input stops `dp-wrap` before anything is written.

| Message                                    | Cause                                                                            | Fix                                                  |
| :----------------------------------------- | :------------------------------------------------------------------------------- | :--------------------------------------------------- |
| `S:L: word length exceeds line length 'K'` | Word _K_ on line _L_ is longer than the line length                              | Choose a larger line length, or accept the long line |
| `S:L: invalid integer 'K'`                 | The first word _K_ is not a whole number (or is larger than 9223372036854775807) | Put the line length first, or use `-w`               |
| `S:L: value out of range 'K'`              | The line length _K_ is 0 or negative                                             | Use a line length of at least 1                      |
| `S:L: unexpected end of input`             | The input is empty, so there is no line length                                   | Put the line length first, or use `-w`               |
| `F: No such file or directory`             | _F_ does not exist                                                               | Check the spelling and the current directory         |
| `F: Permission denied`                     | You may not read _F_                                                             | Check the file's permissions                         |
| `F: Is a directory`                        | _F_ is a directory                                                               | Name a file instead                                  |
| `F: Not a directory`                       | Part of the path _F_ is a file, not a directory                                  | Correct the path                                     |
| `F: Input/output error`                    | Any other read failure                                                           | Check the device or file system                      |
| `write error`                              | The output could not be written (for example, the disk is full)                  | Free space or redirect the output elsewhere          |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-wrap -w 0 fox.txt
dp-wrap: invalid argument '0' for '-w'
Try 'dp-wrap --help' for more information.
```

| Message                                      | Cause                                                     | Fix                         |
| :------------------------------------------- | :-------------------------------------------------------- | :-------------------------- |
| `invalid option -- 'x'`                      | Unknown short option `-x`                                 | Use `-w` or `-b`            |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                        | Spell the option in full    |
| `option requires an argument -- 'w'`         | `-w` was the last argument                                | Give the line length        |
| `option '--width' requires an argument`      | `--width` was the last argument                           | Give the line length        |
| `invalid argument 'V' for '-w'`              | _V_ is not a whole number of at least 1 written in digits | Use, for example, `-w 72`   |
| `option '--bytes' doesn't allow an argument` | A value was given with `=` to an option that takes none   | Remove the `=…`             |
| `extra operand 'F'`                          | More than one file was named                              | Run `dp-wrap` once per file |

## EXAMPLES

Wrap any text at 10 characters, without a line length in the data:

```text
$ dp-wrap -w 10 words.txt
A greedy
formatter
puts as
many words
on each
line as
will fit,
then
starts a
new line.
```

Characters versus bytes:

```text
$ echo 'crème brûlée in a café' | dp-wrap -w 12
crème brûlée
in a café
$ echo 'crème brûlée in a café' | dp-wrap -w 12 -b
crème
brûlée in
a café
```

Reflow a file to 72 columns in a script, and notice long words:

```sh
if ! dp-wrap -w 72 notes.txt > wrapped.txt; then
    echo "some words did not fit (see the messages above)"
fi
```

## HELP OUTPUT

`dp-wrap --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-wrap [OPTION]... [FILE]
Fill the words of FILE into lines no longer than a given line length.

With no FILE, or when FILE is -, read standard input.  Words are separated by
whitespace and are written greedily, separated by single spaces, so that no
line is longer than the line length.  Without -w, the first word of the input
is the line length.  Lengths count UTF-8 characters unless -b is given.  A
word longer than the line length is reported and written on a line of its own.

Options:
  -w, --width=WIDTH   use WIDTH (1 or more) as the line length; the first word
                        of the input is then text
  -b, --bytes         measure words in bytes instead of characters
      --help          display this help and exit
      --version       output version information and exit
```

## VERSION OUTPUT

```text
dp-wrap (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-wrap` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Characters are always counted with the same UTF-8 rule, whatever the locale or console code
page.

## PLATFORM NOTES

- **Windows:** files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes at
  the very end of a file are ignored, but a Ctrl-Z byte in the middle of a file is an ordinary
  character. Output uses LF line endings, not CRLF. To see non-ASCII output correctly in a
  console, use a UTF-8 code page (`chcp 65001`); the bytes written are the same either way. End
  keyboard input with Ctrl-Z followed by Enter.
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

`dp-wc` (project 04), whose `-m` counts characters by the same rule; `dp-strlen` (project 29)
and `dp-reverse` (project 33), which measure strings by the same rule; `dp-page` (project 36);
`fmt(1)`, `fold(1)`.

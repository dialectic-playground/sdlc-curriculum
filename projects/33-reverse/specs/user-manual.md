<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-reverse — User Manual](#dp-reverse--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [What a string is](#what-a-string-is)
    - [Characters and bytes](#characters-and-bytes)
    - [How the reversal works](#how-the-reversal-works)
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

# dp-reverse — User Manual

| Field         | Value                                                 |
| :------------ | :---------------------------------------------------- |
| Product       | `dp-reverse` 1.0.0                                    |
| Project       | `33-reverse` — Two-Pointer In-Place Sequence Reversal |
| Applies to    | Linux, macOS, Windows                                 |
| Specification | `SRS.md` (SRS-33), `shared/CLI-CONVENTIONS.md`        |

---

## NAME

**dp-reverse** — reverse short strings in place

## SYNOPSIS

```text
dp-reverse [-l | --lines] [-b | --bytes] [-p | --prompt] [FILE]
dp-reverse --help
dp-reverse --version
```

## DESCRIPTION

`dp-reverse` reads strings from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`, until the end of the input. For each string it prints one line: the label
`Reversed string:`, a tab, and the string written backwards.

```text
$ echo Antigravity | dp-reverse
Reversed string:	ytivargitnA
```

### What a string is

By default a string is a **word**: a run of characters without spaces, tabs, or line breaks.
Words may share a line or be spread over several lines; each one is reversed separately.

With `-l`, a string is a **whole line**, spaces included, and an empty line is an empty string.
The line feed that ends a line is not part of it, and neither is one carriage return (CR) just
before it, so files with Windows (CRLF) line endings give the same results as any other.

A string may be at most **100 characters** long. A longer string is reported, and `dp-reverse`
stops there; the results already printed remain valid.

### Characters and bytes

`dp-reverse` reverses **characters**, counted by the same rule as `dp-wc -m`: each UTF-8
character is kept whole, so `Zoë` becomes `ëoZ` and `日本語` becomes `語本日`. A byte that is
not part of a valid UTF-8 sequence counts as one character on its own, and is moved as a whole.

With `-b`, `dp-reverse` reverses the **bytes** of each string instead, as the original C
program did, and the limit is 100 bytes. Every accented or non-Latin character then comes out
as invalid bytes — a demonstration of why byte reversal is not text reversal.

### How the reversal works

Each string is reversed **in place**: two positions start at its two ends, exchange what they
point at, and move toward each other until they meet. No second copy of the string is made.
Each result appears as soon as its string has been read, so `dp-reverse` can be used at the
keyboard. End the input with **Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by
**Enter** in a Windows console. With `--prompt`, `dp-reverse` asks for each string with the
original program's prompt, `Enter a string:` followed by a tab:

```text
$ dp-reverse --prompt
Enter a string:	Antigravity
Reversed string:	ytivargitnA
Enter a string:	racecar
Reversed string:	racecar
Enter a string:	^D
```

The prompts are written to standard error, so `dp-reverse --prompt > out.txt` saves only the
results.

One Ctrl-Z byte or more at the very end of the input (the end-of-file mark of old MS-DOS text
files) is ignored.

## OPTIONS

**`-l`, `--lines`**
: Treat each line as one string, instead of each word.

**`-b`, `--bytes`**
: Reverse and count bytes instead of characters.

**`-p`, `--prompt`**
: Before each string is read, write `Enter a string:` and a tab to standard error. A last
prompt appears before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-reverse` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be bundled: `-lp` means `-l -p`.
- Long options must be spelled out in full; `--line` is not accepted.
- Options and the file name can be given in any order: `dp-reverse words.txt -p` works.
- `--` ends option processing, so `dp-reverse -- -l` reads a file named `-l`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                       |
| :----- | :-------------------------------------------------------------------------------------------- |
| 0      | Success: every string was reversed (an empty input is fine), or help or version was printed   |
| 1      | A string was longer than 100 characters (or bytes, with `-b`), or the input could not be read |
| 2      | Usage error: an invalid option or more than one file                                          |

## DIAGNOSTICS

A string that is too long is reported with the input's name (`-` for standard input) and the
line it starts on. Results printed before it are kept, and the exit status is 1:

```text
$ dp-reverse toolong.txt
Reversed string:	trohs
dp-reverse: toolong.txt:2: string exceeds 100 characters
```

| Message                              | Cause                                                            | Fix                                                 |
| :----------------------------------- | :--------------------------------------------------------------- | :-------------------------------------------------- |
| `S:L: string exceeds 100 characters` | The string on line _L_ is longer than 100 characters             | Shorten it, or split it into several strings        |
| `S:L: string exceeds 100 bytes`      | With `-b`, the string on line _L_ is longer than 100 bytes       | Shorten it, or reverse characters instead (no `-b`) |
| `F: No such file or directory`       | _F_ does not exist                                               | Check the spelling and the current directory        |
| `F: Permission denied`               | You may not read _F_                                             | Check the file's permissions                        |
| `F: Is a directory`                  | _F_ is a directory                                               | Name a file instead                                 |
| `F: Not a directory`                 | Part of the path _F_ is a file, not a directory                  | Correct the path                                    |
| `F: Input/output error`              | Any other read failure                                           | Check the device or file system                     |
| `write error`                        | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere         |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-reverse words.txt lines.txt
dp-reverse: extra operand 'lines.txt'
Try 'dp-reverse --help' for more information.
```

| Message                                       | Cause                                                   | Fix                            |
| :-------------------------------------------- | :------------------------------------------------------ | :----------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-l`, `-b`, or `-p`        |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full       |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                |
| `extra operand 'F'`                           | More than one file was named                            | Run `dp-reverse` once per file |

## EXAMPLES

Reverse every word of a file:

```text
$ dp-reverse words.txt
Reversed string:	ytivargitnA
Reversed string:	olleH
Reversed string:	654321
Reversed string:	A
Reversed string:	DCBA
Reversed string:	EDCBA
Reversed string:	racecar
```

Reverse whole lines:

```text
$ dp-reverse -l lines.txt
Reversed string:	!dlroW ,olleH
Reversed string:
Reversed string:	stressed  desserts
```

Characters stay whole:

```text
$ echo 'Zoë 日本語' | dp-reverse
Reversed string:	ëoZ
Reversed string:	語本日
```

Print only the reversed strings, without the label:

```sh
dp-reverse words.txt | cut -f 2
```

## HELP OUTPUT

`dp-reverse --help` prints exactly the following text (every line ends in LF). The help text
is part of the specification (CONV-23):

```text
Usage: dp-reverse [OPTION]... [FILE]
Reverse each string read from FILE and print it.

With no FILE, or when FILE is -, read standard input.  A string is a word (a
run of bytes other than whitespace), or a whole line with -l.  A string may
be at most 100 characters long.  Characters are UTF-8 code points, and each
byte of an invalid sequence is one character; with -b, the string's bytes are
reversed and counted instead.

Options:
  -l, --lines    read each line as one string
  -b, --bytes    reverse and count bytes instead of characters
  -p, --prompt   write the prompt 'Enter a string:' and a tab to standard error
                   before each string is read
      --help     display this help and exit
      --version  output version information and exit
```

## VERSION OUTPUT

```text
dp-reverse (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-reverse` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Characters are always determined with the same UTF-8 rule, whatever the locale or console code
page.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is an ordinary character. Output uses LF line endings, not
  CRLF. To see non-ASCII results correctly in a console, use a UTF-8 code page (`chcp 65001`);
  the bytes written are the same either way. In Windows PowerShell 5.1, text piped into a
  native program is re-encoded before `dp-reverse` sees it; read non-ASCII text from a file to
  avoid this.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a string).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-strlen` (project 29) and `dp-wrap` (project 27), which measure strings by the same
character rule; `dp-wc` (project 04); `rev(1)`, `tac(1)`.

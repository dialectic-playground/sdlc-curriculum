# dp-cat — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-cat` 1.0.0 |
| Project | `02-cat` — Concatenate & Number Files |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-02), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-cat** — concatenate files and print them on standard output

## SYNOPSIS

```text
dp-cat [-AbEnsTv] [FILE]...
dp-cat --help
dp-cat --version
```

## DESCRIPTION

`dp-cat` reads each *FILE* in turn and writes its contents to standard output. With no *FILE*,
or where *FILE* is `-`, it reads standard input. `-` may appear more than once and between
file names: `dp-cat header.txt - footer.txt` wraps whatever arrives on standard input.

Without options the output is an exact copy of the input, byte for byte. Binary files, NUL
bytes, Windows (CRLF) line endings, and a missing final newline are all passed through
unchanged. `dp-cat` never converts line endings or character sets.

The options number lines, squeeze runs of blank lines, and make invisible bytes visible. For
these options, a *line* ends at a line feed (LF). A carriage return (CR) is ordinary data, so a
line containing only a CR is not blank. All the files are treated as one continuous stream:
line numbers continue from one file to the next. If a file does not end with a newline, its
last line runs straight into the first line of the next file, just as it would if you had
joined the files first.

If a file cannot be read (it does not exist, is a directory, or access is denied), `dp-cat`
reports it on standard error, carries on with the remaining files, and exits with status 1 at
the end.

`dp-cat` reads and writes in large blocks and never holds a whole file or line in memory, so it
handles files of any size and endless pipes. Data arriving on a pipe is passed on immediately.

## OPTIONS

**`-A`, `--show-all`**
: Equivalent to `-vET`: show non-printing bytes, tabs, and line ends.

**`-b`, `--number-nonblank`**
: Number the non-empty output lines. Empty lines are left unnumbered and do not use up a number.
  Overrides `-n`.

**`-E`, `--show-ends`**
: Display `$` at the end of each line, just before the line feed. A carriage return directly
  before the line feed is displayed as `^M`, so CRLF line endings appear as `^M$`. A final line
  without a line feed gets no `$`.

**`-n`, `--number`**
: Number all output lines, starting at 1. Each number is right-aligned in a six-character field
  and followed by a TAB: `     1<TAB>first line`.

**`-s`, `--squeeze-blank`**
: Replace each run of consecutive empty lines with a single empty line. Lines that contain only
  a carriage return (blank lines in a CRLF file) are not empty and are never squeezed.

**`-T`, `--show-tabs`**
: Display TAB characters as `^I`.

**`-v`, `--show-nonprinting`**
: Display control characters and other non-printing bytes in a visible notation, described
  below. TAB and line feed are left as they are, unless `-T` or `-E` is also given.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Notation used by `-v`

| Byte | Shown as | Examples |
| :-- | :-- | :-- |
| Control characters `0x00`–`0x1F` except TAB and LF | `^` and a letter or symbol | NUL `^@`, Ctrl-A `^A`, CR `^M`, Ctrl-Z `^Z`, ESC `^[` |
| Printable ASCII `0x20`–`0x7E` | Unchanged | `A`, `~`, space |
| DEL `0x7F` | `^?` | |
| `0x80`–`0xFF` | `M-` and the notation for the byte minus 128 | `0x89` `M-^I`, `0xA0` `M-` + space, `0xE9` `M-i`, `0xFF` `M-^?` |

Bytes are shown one at a time, so a UTF-8 character such as `é` (bytes `0xC3 0xA9`) appears as
`M-CM-)`.

### Option syntax

`dp-cat` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Options can be combined: `-nE` is `-n -E`, and `-sb` is `-s -b`.
- Options can appear anywhere, even after file names: `dp-cat notes.txt -n` numbers the lines.
  An option affects every file, whatever its position.
- Long options must be spelled out in full; `--num` is not accepted.
- `--` ends option processing, so `dp-cat -- -n` prints a file named `-n`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: every file was read and written, or help or version was printed |
| 1 | At least one file could not be read, or the output could not be written |
| 2 | Usage error: invalid option; nothing was read or written |

## DIAGNOSTICS

A file that cannot be read is reported on standard error as a single line. The other files are
still printed:

```text
$ dp-cat alpha.txt missing.txt beta.txt
alpha one
alpha two
dp-cat: missing.txt: No such file or directory
beta one
beta two
$ echo $?
1
```

Usage errors are written as two lines. In that case nothing is read and nothing is written to
standard output:

```text
$ dp-cat --numbr notes.txt
dp-cat: unrecognized option '--numbr'
Try 'dp-cat --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `FILE: No such file or directory` | *FILE* does not exist | Check the name and the current directory |
| `FILE: Permission denied` | You may not read *FILE* | Check the file's permissions |
| `FILE: Is a directory` | *FILE* is a directory | Name the files inside it instead |
| `FILE: Not a directory` | A part of the path that should be a directory is a file | Correct the path |
| `FILE: Input/output error` | Any other error while opening or reading *FILE* (`-` means standard input) | Check the device or the file system |
| `write error` | The output could not be written (for example, the disk is full) | Free space or choose another destination |
| `invalid option -- 'x'` | Unknown short option, such as `-e`, `-t`, or `-u` | Use `-A`, `-b`, `-E`, `-n`, `-s`, `-T`, or `-v` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--number' doesn't allow an argument` | A long option given `=value` | Remove the `=value` |

If the program reading `dp-cat`'s output exits early (for example `dp-cat big.log | head`),
`dp-cat` stops quietly.

## EXAMPLES

Join two files into a third:

```sh
dp-cat part1.txt part2.txt > whole.txt
```

Wrap standard input between a header and a footer:

```sh
generate-report | dp-cat header.txt - footer.txt > report.txt
```

Number the lines of several files; the numbering continues across files:

```text
$ dp-cat -n alpha.txt beta.txt
     1	alpha one
     2	alpha two
     3	beta one
     4	beta two
```

Number only the non-blank lines, and squeeze the runs of blank lines:

```text
$ dp-cat -sb blanks.txt

     1	first

     2	second

     3	third

```

Find out whether a file has Windows line endings:

```text
$ dp-cat -A crlf.txt
first^M$
second^M$
^M$
third^M$
```

The same file without options is printed unchanged, carriage returns included.

Inspect a binary file safely on a terminal:

```text
$ dp-cat -v controls.bin
tab	here
^@^A^Z^[^?
M-^@M-^IM-^JM-^[M- M-CM-)M-^?
bell^G^Mend
```

See where a file lacks its final newline:

```text
$ dp-cat -E no-eol.txt alpha.txt
last line without newlinealpha one$
alpha two$
```

## HELP OUTPUT

`dp-cat --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-cat [OPTION]... [FILE]...
Concatenate FILE(s) to standard output.

With no FILE, or when FILE is -, read standard input.

Options:
  -A, --show-all           equivalent to -vET
  -b, --number-nonblank    number nonempty output lines, overrides -n
  -E, --show-ends          display $ at end of each line, and a CR before it as ^M
  -n, --number             number all output lines
  -s, --squeeze-blank      suppress repeated empty output lines
  -T, --show-tabs          display TAB characters as ^I
  -v, --show-nonprinting   use ^ and M- notation, except for LF and TAB
      --help               display this help and exit
      --version            output version information and exit
```

## VERSION OUTPUT

```text
dp-cat (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-cat` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`). The
`-v` notation is the same in every locale. Bytes `0x80`–`0xFF` are always shown as `M-`
sequences, even when they form valid UTF-8.

## PLATFORM NOTES

- **Windows:** `dp-cat` reads and writes in binary mode. CRLF line endings are preserved, not
  converted. A Ctrl-Z byte (`0x1A`) in a file or on redirected standard input is ordinary data,
  not an end-of-file mark. Generated lines (help, version, diagnostics) end in LF only. When
  you type at the console, end standard input with Ctrl-Z followed by Enter. In PowerShell 5.1,
  `cmd | dp-cat` and `>` redirection re-encode text through PowerShell's pipeline. Use
  `cmd.exe` or PowerShell 7.4 or later when the exact bytes matter.
- **Windows paths:** both `dir\file.txt` and `dir/file.txt` work. Diagnostics repeat the path
  exactly as you typed it. Where Linux and macOS report `Not a directory` (for example
  `file.txt/x`), Windows reports `No such file or directory`.
- **Directories:** a directory operand is reported as `Is a directory` on every system, and
  `dp-cat` continues with the next operand.
- **macOS / Linux:** end typed standard input with Ctrl-D. The system `cat` on macOS (BSD)
  accepts a different set of options; for example, it has no long options. `dp-cat` behaves
  identically on every system.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`cat(1)`, `tac(1)`, `nl(1)`, `od(1)`; `dp-echo` (project 01), `dp-head` and `dp-tail`
(project 03), `dp-wc` (project 04).

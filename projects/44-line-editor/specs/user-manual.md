# dp-line-ed — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-line-ed` 1.0.0 |
| Project | `44-line-editor` — Modal Line-Oriented Text Editor |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-44), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-line-ed** — edit a text file with a line editor driven by standard input

## SYNOPSIS

```text
dp-line-ed [-p | --prompt] FILE
dp-line-ed --help
dp-line-ed --version
```

## DESCRIPTION

`dp-line-ed` loads *FILE* into a buffer of lines and then reads commands from standard input,
one per line. If *FILE* does not exist, the buffer starts empty, and *FILE* is created when you
quit with `q`. Nothing is written to *FILE* until then.

### The current line and `[BOF]`

The buffer begins with a special position, `[BOF]` ("beginning of file"), before the first
line. It is never written to the file. Most commands work from the *current line*, which is
either `[BOF]` or one of the lines. When the editor starts, the current line is `[BOF]`, so text
inserted straight away goes at the top of the file. Typing `[BOF]` itself shows the text
`[BOF]`.

No command can move the current line past the last line: a count that is too large simply
stops there.

### Commands

| Command | Effect |
| :-- | :-- |
| `i` | Insert mode: every following line is inserted after the current line, which moves to it, until a line consisting of a single `.` |
| `d` | Delete the line after the current line |
| `d N` | Delete the *N* lines after the current line (as many as there are) |
| `t .` | Type the current line |
| `t b` | Go to `[BOF]` and type the first line |
| `t e` | Go to the last line and type it |
| `t N` | Type the *N* lines after the current line, without moving |
| `m N` | Move forward *N* lines (stopping at the last line) and type the new current line |
| `f 'PAT'` | Find the next line after the current line that contains *PAT*, go to it, and type it |
| `s 'OLD' 'NEW'` | Replace the first *OLD* in the current line by *NEW*, and type the line |
| `q` | Write the buffer to *FILE* and quit |

Details:

- Commands are lowercase letters separated from their arguments by spaces or tabs. Blanks at the
  start and end of a command line are ignored, and empty lines are skipped.
- *N* is a whole number of at least 1, written in digits (a leading `+` and leading zeros are
  allowed).
- `t N` and `d N` work on the same lines, so `t 3` shows exactly what `d 3` would delete.
  Because `t b` leaves the current line at `[BOF]`, `t b` followed by `t 1000000` types the
  whole file.
- `d` never deletes the current line itself, and neither `d` nor `t N` is an error when fewer
  lines follow than you asked for.
- `f` does not look at the current line and does not wrap around to the top; use `t b` first to
  search the whole file. Matching is exact and case-sensitive; there are no wildcards.
- `s` needs a current line: after `t b` the current line is `[BOF]`, so move to a line first.

### Patterns and delimiters

*PAT*, *OLD*, and *NEW* are written between a pair of identical punctuation characters, the
*delimiter*: `'cat'`, `"cat"`, `/cat/`, and `|cat|` are all the same pattern. Choose a delimiter
that does not occur in the text: `s "it's" 'it is'`. Each string has its own pair of
delimiters, so the `ed` form `s/old/new/` is not accepted; write `s /old/ /new/`. *PAT* and
*OLD* must not be empty; *NEW* may be (`s 'very ' ''` deletes a word). Letters and digits cannot
be delimiters.

### Insert mode

After `i`, every line you type is added to the buffer exactly as typed, including leading
spaces, until you type a line consisting of a single `.`. A line such as ` .` or `..` is
inserted as text; a line that is exactly `.` cannot be inserted. No prompt is shown in insert
mode.

### Saving and quitting

`q` writes every line to *FILE*, each followed by a line feed, and quits. If the input ends
without `q` — the end of a script, or Ctrl-D — the editor reports
`unexpected end of input`, leaves *FILE* exactly as it was, and exits with status 1.

### Mistakes

A command that is malformed or cannot be carried out is reported on standard error with its
line number, changes nothing, and the editor waits for the next command. If any command failed,
the exit status is 1 even though `q` wrote the file, so a script can tell that its edits were
not all applied.

### File contents

Lines are kept as raw bytes. Lines you do not edit are written back exactly as they were —
including the CR of a Windows (CRLF) line ending, tabs, and bytes that are not valid UTF-8 —
except that the last line always ends with a line feed and Ctrl-Z bytes at the very end of the
file (the end-of-file mark of old MS-DOS files) are dropped. Lines you type are taken without a
final CR, so a command script with Windows line endings works like any other.

### Working interactively

With `--prompt`, the editor writes `*` before each command:

```text
$ dp-line-ed --prompt poem.txt
*f 'rat'
It saw a rat.
*s 'rat' 'bat'
It saw a bat.
*q
```

The prompt goes to standard error, so typed lines are the only content of standard output.

## OPTIONS

**`-p`, `--prompt`**
: Write the prompt `*` to standard error before each command is read (not in insert mode). A
  last prompt appears before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-line-ed` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-line-ed notes.txt -p` works.
- `--` ends option processing, so `dp-line-ed -- -p` edits a file named `-p`.
- Because standard input carries the commands, `-` is an ordinary file name here, not standard
  input.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | `q` wrote the file and every command succeeded, or help or version was printed |
| 1 | A command failed (the file is still written by a later `q`), the input ended without `q` (the file is not written), or the file could not be read or written |
| 2 | Usage error: an invalid option, or no file or more than one file named |

## DIAGNOSTICS

Problems with a command name standard input (`-`) and the command's line number, and the session
continues:

```text
$ printf 'x\nt 0\nf /zebra/\nq\n' | dp-line-ed poem.txt
dp-line-ed: -:1: unknown command 'x'
dp-line-ed: -:2: value out of range '0'
dp-line-ed: -:3: pattern not found
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `-:L: unknown command 'W'` | *W* is not one of `i d t m f s q` (commands are lowercase and separated from their arguments by a blank) | Check the command letter |
| `-:L: missing argument` | `t`, `m`, `f`, or `s` without its argument(s) | Supply the argument |
| `-:L: extra argument 'X'` | Something follows the last argument | Remove it; one command per line |
| `-:L: invalid integer 'K'` | *K* is not a whole number, or is far too large | Write the count in digits |
| `-:L: value out of range 'K'` | *K* is zero or negative | Use a count of at least 1 |
| `-:L: missing delimiter` | A pattern does not start with a punctuation character | Enclose it: `f 'cat'` |
| `-:L: unterminated string` | The closing delimiter is missing | Add it |
| `-:L: empty pattern` | `f ''` or `s '' '…'` | Give a non-empty pattern |
| `-:L: no current line` | `s` while the current line is `[BOF]` | Move to a line first (`m 1`, `f`) |
| `-:L: pattern not found` | `f` found no later line with the pattern; `s` found no *OLD* in the current line | Check the text; use `t b` to search from the top |

Problems that end the session (exit status 1):

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `-:L: unexpected end of input` | The input ended without `q`; the file was not written | End the commands with `q` |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Permission denied` | You may not read or write *F* | Check the file's permissions |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: No such file or directory` | At `q`: a directory on the path *F* does not exist | Create the directory or correct the path |
| `F: Input/output error` | Any other read or write failure | Check the device or file system |
| `-: Input/output error` | Standard input could not be read | Check the pipe or terminal |
| `write error` | Typed lines could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read, the file is not
touched, and nothing is written to standard output:

```text
$ dp-line-ed
dp-line-ed: missing operand
Try 'dp-line-ed --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `missing operand` | No file was named | Name the file to edit |
| `extra operand 'F'` | More than one file was named | Edit one file at a time |

## EXAMPLES

Look at a file without changing it (`t b` types the first line, `t 1000000` everything after
`[BOF]`):

```text
$ printf 't 1000000\nq\n' | dp-line-ed poem.txt
The cat sat on the mat.
It saw a rat.
The rat ran.
The cat ran after the rat.
The end.
```

Create a new file:

```text
$ printf 'i\nfirst line\nsecond line\n.\nq\n' | dp-line-ed new.txt
$ cat new.txt
first line
second line
```

Add a title above the first line and a signature below the last:

```text
$ printf 't b\ni\nA Poem\n.\nt e\ni\n-- Anonymous\n.\nq\n' | dp-line-ed poem.txt
The cat sat on the mat.
The end.
```

Delete the two lines after the line that contains `saw`:

```text
$ printf "f 'saw'\nd 2\nq\n" | dp-line-ed poem.txt
It saw a rat.
```

Apply a prepared edit script and check that every command succeeded:

```sh
if dp-line-ed CHANGES.txt < bump.ed > /dev/null; then
    echo "edited"
fi
```

## HELP OUTPUT

`dp-line-ed --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-line-ed [OPTION]... FILE
Edit FILE with a line editor that reads its commands from standard input.

A missing FILE starts an empty buffer, and the current line starts at [BOF],
the position before the first line.  Commands, one per line:
  i              insert the lines that follow after the current line, up to
                   a line consisting of a single .
  d [N]          delete N lines (default 1) after the current line
  t .            type the current line
  t b            go to [BOF] and type the first line
  t e            go to the last line and type it
  t N            type the N lines after the current line
  m N            move forward N lines and type the new current line
  f 'PAT'        find the next line containing PAT and type it
  s 'OLD' 'NEW'  replace the first OLD in the current line by NEW; type it
  q              write the buffer to FILE and quit
Any punctuation character can be used in place of ' around PAT, OLD, NEW.
At the end of the input without q, the editor quits without writing FILE.

Options:
  -p, --prompt    write the prompt * to standard error before each command
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-line-ed (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-line-ed` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`)
and `EDITOR`.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter — but remember that ending the
  input without `q` discards your changes. Files are read and written as raw bytes, so CRLF
  files keep their CRLF line endings and new lines you insert end with LF only. In Windows
  PowerShell 5.1, text piped into a native program is re-encoded before `dp-line-ed` sees it;
  for plain ASCII commands this does not change the result.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line. In shell scripts,
  `printf` with single-quoted commands needs double quotes around the format string when the
  commands themselves contain `'`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-elephnt1`, `dp-elephnt2` (project 43), the linked lists this editor's buffer is built from;
`dp-cat` (project 02) and `dp-diff` (project 07), to view and compare the files you edit;
`ed(1)`, `ex(1)`, `sed(1)`.

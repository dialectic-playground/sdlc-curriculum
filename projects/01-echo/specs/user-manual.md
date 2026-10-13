# dp-echo — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-echo` 1.0.0 |
| Project | `01-echo` — Stream Echo & Formatting |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-01), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-echo** — write arguments to standard output

## SYNOPSIS

```text
dp-echo [-n] [-e | -E] [STRING]...
dp-echo --help
dp-echo --version
```

## DESCRIPTION

`dp-echo` writes each *STRING* to standard output, separated by single spaces, and ends the
output with a line feed (LF). With `-n` it leaves out the line feed; with `-e` it interprets
backslash escape sequences such as `\t` (tab) and `\r` (carriage return).

Output is identical on every operating system. The line feed `dp-echo` adds is always the single
byte LF (`0x0A`), even on Windows, where many programs would write CRLF. `dp-echo` never adds or
removes a carriage return: a CR appears in the output only if you put one there yourself (see
*Line endings* below). Strings are printed exactly as given, including non-ASCII characters such
as `Zoë` or `日本語`, and are encoded in UTF-8.

`dp-echo` reads no input, never touches files or environment variables, and never complains
about its arguments: whatever you give it, it prints.

### Which arguments are options

`dp-echo` is used to print arbitrary text, so it treats options more cautiously than other
curriculum tools (this is a deliberate exception to `shared/CLI-CONVENTIONS.md`, as in the
traditional `echo`):

- Only arguments at the **start** of the command line can be options, and only if they consist
  of `-` followed by one or more of the letters `n`, `e`, `E`. Letters may be combined: `-ne` is
  the same as `-n -e`.
- The first argument that is not such an option, and **every argument after it**, is printed as
  text. That includes `-` on its own, `--`, unknown options such as `-x`, mixtures such as `-nx`,
  the empty string, and option-like arguments that appear after a string:
  `dp-echo hello -n` prints `hello -n`.
- `--` has no special meaning. It is printed like any other string.
- `--help` and `--version` work only when they are the **only** argument. `dp-echo --help me`
  prints `--help me`.

Because every argument is acceptable, `dp-echo` has no usage errors.

### Escape sequences

When `-e` is in effect, a backslash in a *STRING* begins an escape sequence:

| Sequence | Produces |
| :-- | :-- |
| `\\` | a single backslash |
| `\a` | alert (BEL, `0x07`) |
| `\b` | backspace (`0x08`) |
| `\c` | nothing; **all further output stops**, including the remaining strings and the final line feed |
| `\e` | escape (`0x1B`) |
| `\f` | form feed (`0x0C`) |
| `\n` | line feed (LF, `0x0A`) |
| `\r` | carriage return (CR, `0x0D`) |
| `\t` | horizontal tab (`0x09`) |
| `\v` | vertical tab (`0x0B`) |
| `\0NNN` | the byte whose octal value is *NNN*: zero to three octal digits (`0`–`7`) after `\0`; values above 255 wrap around (modulo 256) |
| `\xHH` | the byte whose hexadecimal value is *HH*: one or two hex digits, upper or lower case |

Details:

- Each string is processed separately; an escape never continues into the next string.
- Digits are taken greedily up to the limit: `\01234` is `\0123` (`S`) followed by `4`, and
  `\x414` is `A` followed by `4`.
- A backslash followed by anything else is printed unchanged together with the character after
  it: `\q` prints `\q`, `\x` with no hex digit prints `\x`, and `\1` prints `\1` (only `\0` starts
  an octal escape).
- A backslash at the very end of a string is printed unchanged.
- Escapes can produce any byte, including NUL (`\0`) and bytes that are not valid UTF-8
  (`\xff`). They are written exactly as requested.

Without `-e` (or after a later `-E`), backslashes are ordinary characters, so text such as
`C:\temp\new` is printed exactly as typed.

### Line endings

Unix systems end text lines with LF; Windows traditionally uses CRLF (`0x0D 0x0A`). `dp-echo`
always ends its output with LF alone, on every platform, so a file written by `dp-echo` on
Windows is byte-for-byte identical to one written on Linux or macOS. When a file format or
network protocol requires CRLF, ask for it explicitly:

```text
$ dp-echo -ne 'HELO example.org\r\n'
```

This writes the text, a CR, and an LF, and nothing else (`-n` stops `dp-echo` from adding a
second, bare LF). Carriage returns that are part of a string you pass are printed unchanged too.

## OPTIONS

**`-n`**
: Do not write the trailing line feed.

**`-e`**
: Interpret backslash escape sequences in the strings (see *Escape sequences*).

**`-E`**
: Do not interpret backslash escape sequences. This is the default. If both `-e` and `-E` are
  given, the one that comes last wins: `-e -E` and `-eE` turn escapes off, `-E -e` turns them on.

**`--help`**
: Display the help text below and exit with status 0. Recognized only as the sole argument.

**`--version`**
: Display the version line and exit with status 0. Recognized only as the sole argument.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the strings, help, or version were written |
| 1 | Standard output could not be written (for example, the disk is full) |

`dp-echo` never exits with status 2, because it has no usage errors. If the program reading the
output exits early (a broken pipe), `dp-echo` stops quietly.

## DIAGNOSTICS

`dp-echo` prints exactly one diagnostic, on standard error:

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `dp-echo: write error` | Standard output could not be written, for example because the disk is full | Free space or redirect the output elsewhere |

Unknown options and malformed escape sequences are not errors; they are printed as text.

## EXAMPLES

Print a message (the shell removes the extra spaces between words):

```text
$ dp-echo Build   finished
Build finished
```

Preserve spacing by quoting:

```text
$ dp-echo 'Build   finished'
Build   finished
```

Build one line from two commands:

```text
$ dp-echo -n 'Progress: '; dp-echo done
Progress: done
```

Write a tab-separated header:

```text
$ dp-echo -e 'name\tsize'
name	size
```

Backslashes are printed literally unless `-e` is given:

```text
$ dp-echo 'C:\temp\new'
C:\temp\new
```

Print a prompt that leaves the cursor on the same line:

```text
$ dp-echo -e 'Continue? [y/N] \c'
Continue? [y/N] $
```

Produce bytes by code:

```text
$ dp-echo -e '\x48\0151!'
Hi!
```

Print text that looks like an option:

```text
$ dp-echo -- -n
-- -n
$ dp-echo -x
-x
```

Write a file with CRLF line endings, identical on every platform:

```sh
dp-echo -ne 'line one\r\nline two\r\n' > crlf.txt
```

Show the version:

```text
$ dp-echo --version
dp-echo (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-echo --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-echo [SHORT-OPTION]... [STRING]...
  or:  dp-echo --help
  or:  dp-echo --version
Write the STRINGs to standard output, separated by single spaces and followed
by a line feed (LF) on every platform.

Only leading arguments made of '-' and the letters n, e, E are options. The
first other argument and every argument after it is printed as given; '--' is
not special. --help and --version are recognized only as the sole argument.

Options:
  -n             do not output the trailing line feed
  -e             enable interpretation of backslash escapes
  -E             disable interpretation of backslash escapes (default)
      --help     display this help and exit
      --version  output version information and exit

When -e is in effect, the following sequences are recognized:
  \\      backslash
  \a      alert (BEL, 0x07)
  \b      backspace (0x08)
  \c      produce no further output, not even the line feed
  \e      escape (0x1B)
  \f      form feed (0x0C)
  \n      line feed (LF, 0x0A)
  \r      carriage return (CR, 0x0D)
  \t      horizontal tab (0x09)
  \v      vertical tab (0x0B)
  \0NNN   byte with octal value NNN (0 to 3 octal digits)
  \xHH    byte with hexadecimal value HH (1 to 2 hex digits)
Any other backslash is printed as is. To print a CRLF line ending, use
-ne 'text\r\n'.
```

## VERSION OUTPUT

```text
dp-echo (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-echo` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`) and
`POSIXLY_CORRECT`.

## PLATFORM NOTES

- **Shell built-ins:** most shells have their own built-in `echo`, which behaves differently from
  shell to shell (bash does not interpret escapes by default, dash and zsh do; PowerShell's
  `echo` is an alias for `Write-Output` and ends lines with CRLF when redirected on Windows).
  Type `dp-echo`, not `echo`, to get the behavior described here.
- **Windows:** output uses LF line endings, not CRLF, and is never translated. Use
  `dp-echo -ne '...\r\n'` when you need CRLF. Use Windows Terminal or another UTF-8-capable
  console to see non-ASCII text correctly; redirected output is always UTF-8. In `cmd.exe`,
  single quotes are not quoting characters; use double quotes there: `dp-echo -e "a\tb"`.
  PowerShell accepts both kinds of quotes.
- **macOS / Linux:** in shells such as bash or zsh, put strings containing backslashes, `!`, `$`,
  or spaces in single quotes so the shell passes them unchanged: `dp-echo -e 'a\tb'`. Inside
  double quotes, the shell itself may consume some backslashes.
- **Differences from GNU `echo`:** `dp-echo` recognizes octal escapes only in the form `\0NNN`
  (`\101` is printed literally), and it ignores `POSIXLY_CORRECT`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`echo(1)`, `printf(1)`; `dp-hello` (project 00), `dp-cat` (project 02).

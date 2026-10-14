# dp-size — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-size` 1.0.0 |
| Project | `39-size` — Binary File Byte Size Inspector |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-39), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-size** — print the size in bytes of files named without their extension

## SYNOPSIS

```text
dp-size [-e EXT | --extension=EXT] [-p | --prompt] [NAME]...
dp-size --help
dp-size --version
```

## DESCRIPTION

`dp-size` takes the name of a file *without its extension*, appends `.c`, and reports how many
bytes the file holds. It finds out by opening the file in binary mode and reading it to the
end, counting every byte, so the answer is exactly what `wc -c` or a directory listing shows.

Names are given as arguments, or, with no arguments, read from standard input one per line;
the argument `-` reads names from standard input at that point. Each name is answered as soon
as it has been read. For each file, two lines are written, each starting with a TAB:

```text
	File name:	size.c
	Byte size:	562
```

The first line gives the file name as `dp-size` built it (the name followed by the extension);
the second gives the size. Between the label and the value is one TAB.

### Every byte counts

The file is read in *binary* mode, never in text mode. Every byte counts as one, including:

- NUL bytes (`0x00`), which some programs treat as the end of a string;
- CR bytes: a line ending in CRLF (Windows) counts two bytes, not one;
- Ctrl-Z bytes (`0x1A`), which old MS-DOS programs, and the text mode of Windows C libraries,
  treat as the end of a file — even when they are the last bytes of the file.

So a file has the same size with `dp-size` on Linux, macOS, and Windows.

### Names

A name is used exactly as given: spaces and other characters are part of it, and nothing is
added except the extension. A name may include directories (`src/main` measures
`src/main.c`). Names read from standard input are the lines of the input: one CR before the
line feed is removed, so names typed or saved on Windows work; one or more Ctrl-Z bytes at the
very end of the input are ignored. An empty name, or one that contains a NUL byte, is an error.

### Choosing the extension

`-e .h` appends `.h` instead of `.c`. The extension must begin with a dot, or be empty:
`-e ''` (or `--extension=`) appends nothing, so the name is the whole file name.

## OPTIONS

**`-e EXT`, `--extension=EXT`**
: Append *EXT* to each name instead of `.c`. *EXT* must be empty or begin with `.`.

**`-p`, `--prompt`**
: Before each name is read from standard input, write the prompt
  `File name (NO extension):`, with a TAB before and after it, to standard error. No prompt is
  written for names given as arguments. The prompt never appears on standard output.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-size` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-e.h`, `-e .h`, `--extension=.h`, and
  `--extension .h` are equivalent.
- Long options must be spelled out in full; `--ext` is not accepted.
- If `-e` is given more than once, the last one wins.
- A name that begins with `-` must follow `--`: `dp-size -- -draft` measures `-draft.c`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Every name was measured (or there were none), or help or version was printed |
| 1 | At least one name was empty or malformed, or its file could not be read |
| 2 | Usage error: an invalid option or extension |

## DIAGNOSTICS

Every problem is reported on standard error as one line; `dp-size` then goes on with the next
name, and exits with status 1 at the end. File problems name the file as `dp-size` built it:

```text
$ dp-size missing size
dp-size: missing.c: No such file or directory
	File name:	size.c
	Byte size:	562
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `P: No such file or directory` | The file *P* does not exist (or its name is not valid on this system) | Check the spelling, the extension, and the current directory |
| `P: Permission denied` | You may not read *P* | Check the permissions |
| `P: Is a directory` | *P* is a directory | Name a file instead |
| `P: Not a directory` | Part of the path *P* is a file, not a directory | Correct the path |
| `P: Input/output error` | Any other failure to read *P* | Check the device or file system |
| `empty file name` | An empty argument (`''`) | Give a name |
| `-:L: empty file name` | Line *L* of standard input is empty | Remove the blank line |
| `-:L: file name contains a NUL byte` | Line *L* of standard input contains a NUL byte | Correct the input |
| `-: Input/output error` | Standard input could not be read | Check what feeds standard input |
| `write error` | The results could not be written to standard output | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; no file is read:

```text
$ dp-size -e txt notes
dp-size: invalid argument 'txt' for '-e'
Try 'dp-size --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-e` or `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'e'` | `-e` given without an extension | Supply an extension (or `''`) |
| `option '--extension' requires an argument` | `--extension` given without an extension | Supply an extension |
| `option '--prompt' doesn't allow an argument` | `--prompt=…`, `--help=…`, or `--version=…` | Remove the `=…` |
| `invalid argument 'txt' for '-e'` | The extension is not empty and does not begin with `.` | Write `-e .txt` |

## EXAMPLES

The textbook dialog (what you type is shown after the prompt; the prompt is on standard
error):

```text
$ dp-size --prompt
	File name (NO extension):	size
	File name:	size.c
	Byte size:	562
	File name (NO extension):	^D
```

Measure several files, including one with Windows line endings:

```text
$ dp-size binary crlf empty
	File name:	binary.c
	Byte size:	300
	File name:	crlf.c
	Byte size:	38
	File name:	empty.c
	Byte size:	0
```

Measure files with another extension, or with none:

```sh
dp-size -e .txt notes chapter1 chapter2
dp-size -e '' Makefile README
```

Feed names from another program:

```sh
ls *.c | sed 's/\.c$//' | dp-size
```

Extract just the numbers:

```sh
dp-size main util | awk -F'\t' '$2 == "Byte size:" { print $3 }'
```

## HELP OUTPUT

`dp-size --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-size [OPTION]... [NAME]...
Print the size in bytes of the file NAME.c for each NAME.

Each NAME is a file name without its extension; the extension (.c unless -e
is given) is appended to it, and the file is read to its end in binary mode,
counting every byte.  With no NAME, or when NAME is -, read the names from
standard input, one per line.  For each file, two lines are written:
a TAB, 'File name:', a TAB, and the file name; then a TAB, 'Byte size:', a
TAB, and the number of bytes.

Options:
  -e, --extension=EXT   append EXT instead of .c; EXT is empty or begins
                          with '.'
  -p, --prompt          write the prompt 'File name (NO extension):' to
                          standard error before each name is read
      --help            display this help and exit
      --version         output version information and exit
```

## VERSION OUTPUT

```text
dp-size (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-size` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** sizes are counted in binary mode, so a file with CRLF line endings or Ctrl-Z
  bytes has the same size as on Linux and macOS (and as Explorer shows). Output uses LF line
  endings, not CRLF. End keyboard input with Ctrl-Z followed by Enter. File names cannot contain
  control characters on Windows; such a name is reported as `No such file or directory`. Both `/` and `\` work as directory separators in names.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line. Names are used as
  bytes, so names that are not valid UTF-8 work.
- **All platforms:** names are case-sensitive as far as the file system is: on a
  case-insensitive file system (the default on Windows and macOS), `dp-size SIZE` measures
  `size.c` but reports it as `SIZE.c`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-wc` (project 04), whose `-c` count `dp-size` reproduces; `dp-cat` (project 02), which also
reads binary data unchanged; `dp-strlen` (project 29), which counts the bytes of a string;
`dp-relfile` (project 40), which reads and writes a binary file at fixed offsets; `wc(1)`,
`stat(1)`, `ls(1)`.

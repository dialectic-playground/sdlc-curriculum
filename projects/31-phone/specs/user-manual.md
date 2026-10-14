# dp-phone — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-phone` 1.0.0 |
| Project | `31-phone` — Student Directory Lookup via Selection Sort & Binary Search |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-31), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-phone** — look up students' telephone numbers by last name

## SYNOPSIS

```text
dp-phone [-f FILE | --file=FILE] [-p | --prompt] [FILE]
dp-phone --help
dp-phone --version
```

## DESCRIPTION

`dp-phone` loads the student records in `students.dat` in the current directory, sorts them,
and then reads last names, one per line, from *FILE*, or from standard input when there is no
*FILE* or *FILE* is `-`. For each name it prints one line: the student's record, or a message
that the name is not in the directory.

```text
Record: Turing                   Alan                     508-416-0633
Knuth is not in our directory.
```

The tool runs until the end of the names, and exits with status 0 whether or not any name was
found.

### The student file

Each line of the student file is one record of exactly 62 bytes, in three fixed columns:

| Columns | Contents |
| :-- | :-- |
| 1–25 | Last name, padded with spaces |
| 26–50 | First name, padded with spaces |
| 51–62 | Telephone number, for example `508-416-0633` |

The records may be in any order. Lines may end with LF or with CRLF, and one or more Ctrl-Z
bytes at the very end of the file (the end-of-file mark of old MS-DOS data files) are ignored.
Every line must be exactly 62 bytes long, not counting its line ending: a short or long line,
or a blank line, is reported with its line number before any name is looked up, for example

```text
dp-phone: students.dat:4: invalid record length 61, expected 62
```

Columns are counted in bytes, so a last name with non-ASCII letters, such as `Zoë` in UTF-8,
uses more columns than it has letters.

### How names are matched

Each line you type is one last name, including any spaces in it, so `Von Neumann` is looked up
as one name. The match is exact and case-sensitive: `turing` does not find `Turing`, and a
space in front of the name (` Turing`) prevents a match, while spaces after it do not. A name
longer than 25 bytes cannot fit in the last-name column and is never found. Blank lines are
ignored and produce no output.

If several students share a last name, `dp-phone` shows exactly one of them: the one its binary
search reaches first (see the SRS, FR-06). It always shows the same one for the same file.

### Working interactively

`dp-phone` answers each name as soon as you press Enter. End the session with **Ctrl-D** on
Linux and macOS, or **Ctrl-Z** followed by **Enter** in a Windows console. With `--prompt`,
`dp-phone` asks for each name, as the original program did:

```text
$ dp-phone --prompt
Enter a student's name, or signal EOF to halt: Turing
Record: Turing                   Alan                     508-416-0633
Enter a student's name, or signal EOF to halt: Knuth
Knuth is not in our directory.
Enter a student's name, or signal EOF to halt: ^D
```

The prompts are written to standard error, so `dp-phone --prompt > answers.txt` saves only the
answers.

## OPTIONS

**`-f FILE`, `--file=FILE`**
: Read the student records from *FILE* instead of `students.dat`. `-f -` reads them from
  standard input; the names must then come from a *FILE* operand other than `-`.

**`-p`, `--prompt`**
: Write the prompt `Enter a student's name, or signal EOF to halt: ` to standard error before
  each name is read, and once more before the end of the input is detected.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-phone` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-fstaff.dat`, `-f staff.dat`,
  `--file=staff.dat`, and `--file staff.dat` are equivalent.
- Short options can be combined: `-pf staff.dat` works.
- Long options must be spelled out in full; `--fi` is not accepted.
- If `--file` is given more than once, the last one wins.
- `--` ends option processing: `dp-phone -- -names.txt` reads the names from the file
  `-names.txt`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: every name was answered, or help or version was printed |
| 1 | A file could not be read, or the student file contains a malformed record |
| 2 | Usage error: an invalid option or value, or an unexpected argument |

## DIAGNOSTICS

Every problem is reported on standard error as one line, and the exit status is 1. Problems
with the student file are found before any name is read, so nothing is written to standard
output.

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid record length N, expected 62` | Line *L* of the student file *S* is *N* bytes long (without its line ending) | Pad or trim the record to exactly 62 columns; remove blank lines |
| `F: No such file or directory` | The student file or name file *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other failure to read *F* | Check the device or file system |
| `write error` | The answers could not be written to standard output | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; no file is read:

```text
$ dp-phone names.txt more.txt
dp-phone: extra operand 'more.txt'
Try 'dp-phone --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-f` or `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'f'` | `-f` given without a file name | Supply a file name |
| `option '--file' requires an argument` | `--file` given without a file name | Supply a file name |
| `option '--prompt' doesn't allow an argument` | `--prompt=…`, `--help=…`, or `--version=…` | Remove the `=…` |
| `invalid argument '' for '-f'` | An empty file name | Give a non-empty file name |
| `invalid argument '-' for '-f'` | `-f -` while the names also come from standard input | Name a file of names as the operand |
| `extra operand 'F'` | More than one file of names | Look up the names of one file at a time |

## EXAMPLES

Look up names from a list (`names.txt` holds `Turing`, `Knuth`, `Lovelace`, and `Gosling`):

```text
$ dp-phone names.txt
Record: Turing                   Alan                     508-416-0633
Knuth is not in our directory.
Record: Lovelace                 Ada                      212-789-0979
Gosling is not in our directory.
```

Look up a name that contains a space:

```text
$ echo 'Von Neumann' | dp-phone
Record: Von Neumann              Johnny                   602-490-2066
```

Use another student file, or read the records from a pipe:

```sh
dp-phone -f staff.dat callers.txt
export-students | dp-phone -f - callers.txt
```

Keep only the telephone numbers of the students found:

```sh
dp-phone callers.txt | grep '^Record: ' | cut -c 59-70
```

## HELP OUTPUT

`dp-phone --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-phone [OPTION]... [FILE]
Look up students' telephone numbers by last name.

Load the fixed-width student records (last name in columns 1-25, first name in
columns 26-50, telephone number in columns 51-62), sort them, and then answer
each line of FILE as a last name to look up.  With no FILE, or when FILE is -,
read the names from standard input.  Names are matched exactly, including
case and spaces; a name is reported as 'Record: ' and the student's record, or
as not in the directory.

Options:
  -f, --file=FILE   read the student records from FILE (default students.dat);
                      - means standard input
  -p, --prompt      write a prompt to standard error before each name is read
      --help        display this help and exit
      --version     output version information and exit
```

## VERSION OUTPUT

```text
dp-phone (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-phone` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Names are compared byte for byte, so the result never depends on the language settings.

## PLATFORM NOTES

- **Windows:** end interactive input with Ctrl-Z followed by Enter. Student files and name
  lists with CRLF line endings are read correctly, and the answers always end in LF only. Both
  `/` and `\` work as directory separators in file names.
- **macOS / Linux:** end interactive input with Ctrl-D at the start of a line. A student file
  copied from Windows needs no conversion.
- **All systems:** a record is 62 *bytes*. An editor that saves non-ASCII letters in UTF-8 uses
  two or more bytes for each of them, so pad such names with fewer spaces.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-grep` (project 05), which finds lines by pattern instead of by exact key;
`dp-kv` (project 09), a key-value store; `look(1)`, `sort(1)`, `join(1)`.

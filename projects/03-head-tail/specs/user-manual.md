<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-head, dp-tail — User Manual](#dp-head-dp-tail--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
  - [OPTIONS](#options)
    - [Common options](#common-options)
    - [dp-tail only](#dp-tail-only)
    - [Numbers](#numbers)
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

# dp-head, dp-tail — User Manual

| Field         | Value                                          |
| :------------ | :--------------------------------------------- |
| Products      | `dp-head` 1.0.0, `dp-tail` 1.0.0               |
| Project       | `03-head-tail` — Stream Slicing Utility        |
| Applies to    | Linux, macOS, Windows                          |
| Specification | `SRS.md` (SRS-03), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-head** — output the first part of files

**dp-tail** — output the last part of files, optionally following them as they grow

## SYNOPSIS

```text
dp-head [-n [-]NUM | -c [-]NUM] [-q | -v] [FILE]...
dp-tail [-n [+]NUM | -c [+]NUM] [-q | -v] [-f [-s SECONDS] [--max-polls=N]] [FILE]...
dp-head --help | --version
dp-tail --help | --version
```

## DESCRIPTION

`dp-head` prints the first 10 lines of each _FILE_; `dp-tail` prints the last 10. With `-n`
you choose a different number of lines, and with `-c` you count bytes instead of lines.

- `dp-head -n -NUM` prints everything **except** the last _NUM_ lines (`-c -NUM`: bytes).
- `dp-tail -n +NUM` prints everything **from** line _NUM_ onward, counting from 1
  (`-c +NUM`: from byte _NUM_).

With no _FILE_, or when _FILE_ is `-`, the tools read standard input. When you give more than
one _FILE_, each file's output is preceded by a header such as `==> notes.txt <==`, and a blank
line separates consecutive files. Standard input is labelled `standard input`.

A **line** is everything up to and including a line feed (LF). If a file does not end with a
line feed, its last partial line still counts as a line. The data is copied exactly as it is
stored: Windows CRLF line endings keep their CR bytes, and no line feed is ever added.

`dp-tail -f` keeps running after printing the last lines and prints whatever is appended to the
files, which makes it suitable for watching log files. `--max-polls` makes it stop after a fixed
number of checks.

Both tools handle files of any size, including files much larger than memory. On an ordinary
file, `dp-tail` reads backwards from the end, so `dp-tail` of a 40 GB log is as quick as
`dp-tail` of a small one.

## OPTIONS

### Common options

**`-n NUM`, `--lines=NUM`**
: Count lines. `dp-head` prints the first _NUM_ lines (`-NUM`: all but the last _NUM_).
`dp-tail` prints the last _NUM_ lines (`+NUM`: starting with line _NUM_). The default is
`-n 10`.

**`-c NUM`, `--bytes=NUM`**
: Count bytes instead of lines, with the same sign rules as `-n`.

**`-q`, `--quiet`**
: Never print headers.

**`-v`, `--verbose`**
: Always print headers, even for a single input.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### dp-tail only

**`-f`, `--follow`**
: After the initial output, keep checking each file for appended data and print it. Only
ordinary files are followed: standard input, pipes, directories, and files that could not be
opened are not. If no file can be followed, `dp-tail` exits right away. If a followed file
becomes shorter (for example, it was truncated), `dp-tail` reports `file truncated` and
continues from its new beginning.

**`-s SECONDS`, `--sleep-interval=SECONDS`**
: With `-f`, wait _SECONDS_ between checks. _SECONDS_ is a whole number or a decimal such as
`0.5` (digits on both sides of the point), from 0 to 86400. The default is 1.

**`--max-polls=N`**
: With `-f`, check the files _N_ times and then exit, instead of running until interrupted. _N_
is a whole number; 0 means exit right after the initial output.

### Numbers

_NUM_ is written with the digits `0`–`9`, optionally preceded by the sign described above and
optionally followed by one multiplier suffix: `K` (1024), `M` (1024×1024), or `G`
(1024×1024×1024). For example, `-c 64K` means 65536 bytes. Suffixes are uppercase only. The
largest allowed value is 9223372036854775807. Requesting more lines or bytes than a file has is
fine: you get the whole file (or, for `-NUM` and `+NUM`, possibly nothing).

### Option syntax

Both tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-n5`, `-n 5`, `--lines=5`, and `--lines 5`
  are equivalent. A separate value may start with `-`: `dp-head -n -2` works.
- Flags can be combined: `dp-tail -qf` means `dp-tail -q -f`.
- Long options must be spelled out in full.
- `-n` and `-c` are alternatives; whichever comes **last** decides. Likewise for `-q` and `-v`.
- `--` ends option processing, so `dp-tail -- -notes.txt` reads a file named `-notes.txt`.
- The traditional shorthand `dp-head -5` is not supported; write `dp-head -n 5`. An argument
  such as `+5` is treated as a file name; write `dp-tail -n +5`.

## EXIT STATUS

| Status | Meaning                                                                            |
| :----- | :--------------------------------------------------------------------------------- |
| 0      | Success: every file was printed, or help or version was shown                      |
| 1      | At least one file could not be opened or read (the other files were still printed) |
| 2      | Usage error: invalid option or value; nothing was printed                          |

`dp-tail -f` without `--max-polls` keeps running until you interrupt it (for example with
Ctrl+C).

## DIAGNOSTICS

Usage errors are written to standard error as two lines, and nothing is written to standard
output. For example:

```text
$ dp-head -n ten notes.txt
dp-head: invalid argument 'ten' for '-n'
Try 'dp-head --help' for more information.
```

File errors are one line, and processing continues with the next file:

```text
$ dp-head -n 1 missing.txt short.txt
==> short.txt <==
alpha
dp-head: missing.txt: No such file or directory
```

| Message                                      | Cause                                                     | Fix                                               |
| :------------------------------------------- | :-------------------------------------------------------- | :------------------------------------------------ |
| `invalid option -- 'x'`                      | Unknown short option, including the shorthand `-5`        | Use `-n 5`                                        |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                        | Spell the option in full                          |
| `option requires an argument -- 'n'`         | `-n`, `-c`, or `-s` without a value                       | Supply a value                                    |
| `option '--lines' requires an argument`      | A long option without its value                           | Supply a value                                    |
| `option '--quiet' doesn't allow an argument` | `=…` after a flag                                         | Remove the `=…`                                   |
| `invalid argument '+3' for '--lines'`        | A malformed or too-large _NUM_, or `+` given to `dp-head` | Use digits, an allowed sign, and `K`/`M`/`G` only |
| `invalid argument '1.5.2' for '-s'`          | Malformed or too-large _SECONDS_                          | Use a number such as `2` or `0.5`, at most 86400  |
| `invalid argument '-1' for '--max-polls'`    | _N_ is not a whole number                                 | Use digits only                                   |
| `missing.txt: No such file or directory`     | The file does not exist                                   | Check the name                                    |
| `logs: Is a directory`                       | A directory was named                                     | Name a file inside it                             |
| `notes.txt: Permission denied`               | The file cannot be read                                   | Check its permissions                             |
| `app.log: file truncated`                    | A followed file became shorter (`dp-tail -f`)             | Informational only                                |

## EXAMPLES

Show the start and the end of a file:

```text
$ dp-head -n 3 lines.txt
line 1
line 2
line 3
$ dp-tail -n 2 lines.txt
line 14
line 15
```

Skip a header line, or drop a trailer:

```sh
dp-tail -n +2 table.csv > rows.csv      # everything from line 2
dp-head -n -1 report.txt                # everything except the last line
```

Extract bytes:

```sh
dp-head -c 512 disk.img > boot.bin      # first 512 bytes
dp-tail -c 1M big.log                   # last mebibyte
```

Several files with headers:

```text
$ dp-head -n 2 lines.txt short.txt
==> lines.txt <==
line 1
line 2

==> short.txt <==
alpha
beta
```

Keep only the end of a long build log in a pipeline:

```sh
make 2>&1 | dp-tail -n 50
```

Watch a log file until interrupted, checking twice a second:

```sh
dp-tail -f -s 0.5 server.log
```

Print the end of a log, check once more for new lines, and exit:

```sh
dp-tail -f --max-polls 1 -s 0 server.log
```

## HELP OUTPUT

`dp-head --help` and `dp-tail --help` print exactly the following texts (every line ends in LF).
The help texts are part of the specification (CONV-23).

`dp-head --help`:

```text
Usage: dp-head [OPTION]... [FILE]...
Print the first 10 lines of each FILE to standard output.

With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

NUM is a decimal integer with an optional multiplier suffix:
K (1024), M (1024*1024), or G (1024*1024*1024).

Options:
  -c, --bytes=[-]NUM    print the first NUM bytes of each file;
                          with a leading '-', print all but the last NUM bytes
  -n, --lines=[-]NUM    print the first NUM lines instead of the first 10;
                          with a leading '-', print all but the last NUM lines
  -q, --quiet           never print headers giving file names
  -v, --verbose         always print headers giving file names
      --help            display this help and exit
      --version         output version information and exit
```

`dp-tail --help`:

```text
Usage: dp-tail [OPTION]... [FILE]...
Print the last 10 lines of each FILE to standard output.

With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

NUM is a decimal integer with an optional multiplier suffix:
K (1024), M (1024*1024), or G (1024*1024*1024).

Options:
  -c, --bytes=[+]NUM    output the last NUM bytes;
                          or use -c +NUM to output starting with byte NUM
  -n, --lines=[+]NUM    output the last NUM lines, instead of the last 10;
                          or use -n +NUM to output starting with line NUM
  -f, --follow          output appended data as regular files grow
  -s, --sleep-interval=SECONDS
                        with -f, wait SECONDS between polls
                          (default 1, at most 86400)
      --max-polls=N     with -f, stop after N polls instead of running forever
  -q, --quiet           never print headers giving file names
  -v, --verbose         always print headers giving file names
      --help            display this help and exit
      --version         output version information and exit
```

## VERSION OUTPUT

```text
dp-head (dialectic-playground) 1.0.0
dp-tail (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

Both tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).

## PLATFORM NOTES

- **Windows:** output is written in binary mode, so CRLF files come out byte-for-byte unchanged
  and headers end in LF, not CRLF. In PowerShell, `Get-Content file | dp-tail` re-encodes the
  text before it reaches `dp-tail`; pass the file name instead (`dp-tail file`) to get the exact
  bytes. Paths are echoed as typed, so `logs\app.log` appears as `==> logs\app.log <==`.
- **All platforms:** follow mode checks for appended data by polling. A file that is renamed
  or replaced (log rotation) is not re-opened; `dp-tail -f` keeps reading the original file.
- **Large files:** `dp-tail`, and `dp-head` with `-NUM`, find their slice from the end of an
  ordinary file without reading the whole file. On pipes, they keep only the last _NUM_ lines or
  bytes in memory.
- **macOS / Linux:** quote file names that contain spaces or shell metacharacters.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build dp-head and dp-tail
make install      # install both into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`head(1)`, `tail(1)`; `dp-cat` (project 02), `dp-wc` (project 04).

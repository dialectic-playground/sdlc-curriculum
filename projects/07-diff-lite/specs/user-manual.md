<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-diff — User Manual](#dp-diff--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [One answer, every time](#one-answer-every-time)
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

# dp-diff — User Manual

| Field         | Value                                          |
| :------------ | :--------------------------------------------- |
| Product       | `dp-diff` 1.0.0                                |
| Project       | `07-diff-lite` — Line-by-Line File Comparison  |
| Applies to    | Linux, macOS, Windows                          |
| Specification | `SRS.md` (SRS-07), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-diff** — compare two files line by line

## SYNOPSIS

```text
dp-diff [-q | --brief] [-u | -U NUM | --unified[=NUM]] [--strip-trailing-cr] FILE1 FILE2
dp-diff --help
dp-diff --version
```

## DESCRIPTION

`dp-diff` reads _FILE1_ and _FILE2_, splits them into lines, and reports the shortest way to
turn the first into the second: which lines to delete and which to insert. If either operand is
`-`, that side is read from standard input.

By default the differences are written in **normal format**, the classic diff output:

```text
2c2
< banana
---
> blueberry
```

Each block starts with a command: `NdM` (lines _N_ of _FILE1_ were deleted; _M_ is the line of
_FILE2_ they would have followed), `NaM` (lines _M_ of _FILE2_ were added after line _N_ of
_FILE1_), or `NcM` (lines _N_ were changed into lines _M_). Ranges are written `first,last`, or
as a single number for one line. Deleted lines are shown after `<inserted lines after `>`and a change separates the two groups with`---`.

With `-u` or `-U NUM`, the output uses **unified format**, the format of code review tools and
patches. It starts with a `---` line naming _FILE1_ and a `+++` line naming _FILE2_, followed by
_hunks_. Each hunk header `@@ -start,count +start,count @@` gives the range of lines it covers
in each file (`,count` is omitted when the count is 1; a count of 0 means the hunk inserts or
deletes at that position). Inside a hunk, unchanged context lines start with a space, deleted
lines with `-`, and inserted lines with `+`. Changes that are close together (at most 2·_NUM_
unchanged lines apart) share one hunk.

Lines are compared as exact byte sequences, including their final line feed. A last line that
has no line feed is therefore different from the same text with one, and `dp-diff` marks such a
line with `\ No newline at end of file`.

When the files are the same, `dp-diff` prints nothing and exits with status 0.

### One answer, every time

Two files can often be reconciled by several equally short sets of edits. For example, to turn
`ping ping pong` into `ping pong pong`, you can change the middle line, or delete one `ping` and
add one `pong`. Traditional diff tools pick one depending on their algorithm. `dp-diff` always
picks the same one: it keeps matching lines as early as possible and, when it has a choice,
deletes before it inserts. The exact rule is defined in SRS-07 (FR-05). Because the rule is
fixed, every correct implementation of `dp-diff` on every operating system prints exactly the
same output, so `dp-diff` output can be stored, compared, and tested byte for byte. Its output
can therefore differ from GNU `diff`, while still describing a valid shortest set of edits.

## OPTIONS

**`-q`, `--brief`**
: Do not list the differences. Print `Files FILE1 and FILE2 differ` if the files differ, and
nothing if they are the same. Takes precedence over `-u` and `-U`.

**`-u`**
: Use unified format with 3 lines of context. Exactly the same as `-U 3`.

**`-U NUM`, `--unified[=NUM]`**
: Use unified format with _NUM_ lines of context around each change. _NUM_ is a whole number
from 0 to 2147483647, written with the digits `0`–`9` only. `--unified` without `=NUM` means
3 lines. The value of `--unified` must be attached with `=`: `--unified 5` means "3 lines of
context" followed by an operand `5`.

**`--strip-trailing-cr`**
: Remove the carriage return (CR) that ends each line of a file with Windows (CRLF) line
endings before comparing. Files that differ only in CRLF versus LF line endings then compare
as the same. Output lines are shown without the removed CR.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-diff` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- `-U` takes its value attached or separate: `-U1` and `-U 1` are equivalent, and short options
  can be combined: `-qU1`.
- Long options must be spelled out in full; `--unif` is not accepted.
- `-u`, `-U`, and `--unified` set the same thing; if several are given, the last one wins.
- Options and operands can be mixed: `dp-diff a.txt -u b.txt` works.
- `--` ends option processing, so `dp-diff -- -q b.txt` compares a file named `-q`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                            |
| :----- | :----------------------------------------------------------------- |
| 0      | The files are the same (or `--help` / `--version` was handled)     |
| 1      | The files differ                                                   |
| 2      | Trouble: a file could not be read, or the command line was invalid |

Note that, as with traditional `diff`, a missing file gives status 2, not 1: status 1 always
means "the files differ".

## DIAGNOSTICS

Errors are written to standard error, and nothing is written to standard output. Command-line
mistakes add a second line pointing to `--help`:

```text
$ dp-diff old.txt
dp-diff: missing operand
Try 'dp-diff --help' for more information.
```

File problems are reported for every operand that fails, _FILE1_ first:

```text
$ dp-diff fruits.txt nosuch.txt
dp-diff: nosuch.txt: No such file or directory
```

| Message                                      | Cause                                                           | Fix                                 |
| :------------------------------------------- | :-------------------------------------------------------------- | :---------------------------------- |
| `missing operand`                            | Fewer than two files named                                      | Name exactly two files              |
| `extra operand 'c.txt'`                      | More than two files named                                       | Name exactly two files              |
| `'-' may be given as only one operand`       | Both operands are `-`                                           | Standard input can only be one side |
| `invalid option -- 'x'`                      | Unknown short option                                            | Use `-q`, `-u`, or `-U`             |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option                              | Spell the option in full            |
| `option requires an argument -- 'U'`         | `-U` given without a number                                     | Supply a number: `-U 2`             |
| `option '--brief' doesn't allow an argument` | `--brief=…` (also `--strip-trailing-cr`, `--help`, `--version`) | Remove the `=…`                     |
| `invalid argument 'x' for '--unified'`       | Context size is not a whole number from 0 to 2147483647         | Use digits only, e.g. `--unified=5` |
| `FILE: No such file or directory`            | The file does not exist                                         | Check the path                      |
| `FILE: Permission denied`                    | The file cannot be read                                         | Check its permissions               |
| `FILE: Is a directory`                       | A directory was named                                           | `dp-diff` compares files only       |
| `FILE: Not a directory`                      | A path component is a file, not a directory                     | Check the path                      |
| `FILE: Input/output error`                   | Any other read failure                                          | Check the device or file            |

## EXAMPLES

Check whether two files are the same:

```sh
if dp-diff -q expected.txt actual.txt > /dev/null; then
    echo "same"
fi
```

Show a single changed line in normal format:

```text
$ dp-diff fruits.txt fruits-changed.txt
2c2
< banana
---
> blueberry
```

Insertions and deletions:

```text
$ dp-diff list-old.txt list-new.txt
1a2,3
> flour
> sugar
3d4
< bread
6d6
< jam
```

The same comparison in unified format:

```text
$ dp-diff -u list-old.txt list-new.txt
--- list-old.txt
+++ list-new.txt
@@ -1,6 +1,6 @@
 milk
+flour
+sugar
 eggs
-bread
 butter
 cheese
-jam
```

Less context splits distant changes into separate hunks:

```text
$ dp-diff -U 1 long-old.txt long-new.txt
--- long-old.txt
+++ long-new.txt
@@ -1,3 +1,3 @@
 line 01
-line 02
+line 02 changed
 line 03
@@ -8,3 +8,3 @@
 line 08
-line 09
+line 09 changed
 line 10
```

A file whose last line has no line feed:

```text
$ dp-diff -u poem.txt poem-no-eol.txt
--- poem.txt
+++ poem-no-eol.txt
@@ -1,3 +1,3 @@
 roses are red
 violets are blue
-sugar is sweet
+sugar is sweet
\ No newline at end of file
```

Repeated lines, where the canonical rule decides (GNU `diff` prints `2c2` here):

```text
$ dp-diff pings.txt pongs.txt
2d1
< ping
3a3
> pong
```

Ignore Windows line endings:

```text
$ dp-diff --strip-trailing-cr crlf.txt lf.txt
$ echo $?
0
```

Compare a program's output with a stored copy:

```sh
generate-report | dp-diff -u - golden.txt
```

## HELP OUTPUT

`dp-diff --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-diff [OPTION]... FILE1 FILE2
Compare two files line by line.

With no options, the differences are written in normal format. If FILE1 or
FILE2 is -, standard input is read; at most one operand may be -.

Options:
  -q, --brief               report only whether the files differ
  -u                        output unified format with 3 lines of context
  -U NUM, --unified[=NUM]   output unified format with NUM lines of context
                              (default 3)
      --strip-trailing-cr   remove a carriage return that precedes a line feed
                              in the input
      --help                display this help and exit
      --version             output version information and exit

Exit status is 0 if the files are the same, 1 if they differ, 2 if trouble.
```

## VERSION OUTPUT

```text
dp-diff (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-diff` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`) and
the time zone (`TZ`). Its output never contains timestamps.

## PLATFORM NOTES

- **Line endings:** `dp-diff` never translates line endings. A file with CRLF line endings
  differs from the same text with LF endings unless `--strip-trailing-cr` is given, and the CR
  bytes are copied into the output unchanged. Every line `dp-diff` generates itself (commands,
  headers, `---`, the no-newline marker) ends in LF only, on every platform.
- **Windows:** output is written in binary mode, so redirecting it to a file never adds CR
  bytes. Paths are echoed exactly as typed, so `dp-diff -u a\x.txt b.txt` prints
  `--- a\x.txt`. In PowerShell, piping text into `dp-diff -` may re-encode it; redirect from a
  file (`cmd /c "dp-diff - b.txt < a.txt"`) when the exact bytes matter.
- **macOS / Linux:** quote file names that contain spaces or shell metacharacters.
- **Comparing with GNU diff:** `dp-diff` output is valid input for `patch`, but it is not always
  byte-identical to GNU `diff`: unified headers have no timestamps, and when several equally
  short edit sets exist, `dp-diff` may choose a different one.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`diff(1)`, `cmp(1)`, `patch(1)`; `dp-cat` (project 02), `dp-grep` (project 05).

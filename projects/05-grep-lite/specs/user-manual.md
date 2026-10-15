<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-grep — User Manual](#dp-grep--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
  - [OPTIONS](#options)
    - [Pattern selection](#pattern-selection)
    - [Output control](#output-control)
    - [File selection](#file-selection)
    - [Option syntax](#option-syntax)
  - [PATTERN SYNTAX](#pattern-syntax)
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

# dp-grep — User Manual

| Field         | Value                                           |
| :------------ | :---------------------------------------------- |
| Product       | `dp-grep` 1.0.0                                 |
| Project       | `05-grep-lite` — Pattern Matching Search Engine |
| Applies to    | Linux, macOS, Windows                           |
| Specification | `SRS.md` (SRS-05), `shared/CLI-CONVENTIONS.md`  |

---

## NAME

**dp-grep** — print lines that match a portable regular expression

## SYNOPSIS

```text
dp-grep [OPTION]... PATTERN [FILE]...
dp-grep [OPTION]... -e PATTERN [-e PATTERN]... [FILE]...
dp-grep --help
dp-grep --version
```

## DESCRIPTION

`dp-grep` searches each _FILE_ for lines that match _PATTERN_ and writes those lines to standard
output. With no _FILE_ it reads standard input; with `-r` and no _FILE_ it searches the current
directory and everything below it. A _FILE_ of `-` means standard input.

_PATTERN_ is a regular expression in the **portable ERE subset** described below. Every
implementation of `dp-grep`, on every operating system, accepts exactly the same patterns and
selects exactly the same lines. Constructs that other tools support but that do not behave the
same everywhere, such as `\d`, backreferences, and lazy quantifiers, are rejected with a message
that names the problem, instead of being silently interpreted one way or another.

`dp-grep` works on bytes. A line is everything between two line feeds (LF). A carriage return
(CR) at the end of a line from a Windows-style file is part of the line and is printed back
unchanged. Files need not be text: NUL bytes and invalid UTF-8 are searched like any other bytes.
Each printed line ends with a single LF, even if the last line of the file had none.

When more than one _FILE_ is given, or with `-r`, each output line starts with the file name and
a colon. Files found by `-r` are named by joining directory and entry names with `/` on every
operating system, and are visited in a fixed (byte-wise sorted) order, so the output is the same
everywhere.

`dp-grep` never modifies files.

## OPTIONS

### Pattern selection

**`-e PATTERN`, `--regexp=PATTERN`**
: Use _PATTERN_. Give the option several times to search for several patterns: a line matches
if any of them matches. When `-e` is used, every operand is a _FILE_. Use `-e` for a pattern
that begins with `-`: `dp-grep -e -x notes.txt`.

**`-F`, `--fixed-strings`**
: Treat every pattern as a literal string. No character is special, so `dp-grep -F 'a.b*'`
finds the text `a.b*` exactly.

**`-i`, `--ignore-case`**
: Ignore the case of the ASCII letters `A`–`Z` and `a`–`z`. Other characters, such as `é` and
`É`, are always compared exactly.

**`-v`, `--invert-match`**
: Select the lines that do _not_ match.

**`-x`, `--line-regexp`**
: A pattern must match the whole line, from its first byte to its last. `-x` overrides `-w`.

**`-w`, `--word-regexp`**
: A pattern must match a whole word: the matched text must not be directly preceded or followed
by a word character (`A`–`Z`, `a`–`z`, `0`–`9`, or `_`). For example, `-w cat` matches
`the cat sat` and `CAT!` (with `-i`), but not `concatenate`, `cat_food`, or `bobcat`.

### Output control

**`-n`, `--line-number`**
: Put the line number (counting from 1 in each file) and a colon before each output line.

**`-c`, `--count`**
: Instead of the lines, print the number of selected lines in each file, including `0`.

**`-l`, `--files-with-matches`**
: Instead of the lines, print the name of each file that has at least one selected line.
`dp-grep` stops reading a file as soon as it knows the answer.

**`-q`, `--quiet`**
: Print nothing. Exit with status 0 as soon as any line is selected, without reading further.
Useful in scripts: `if dp-grep -q ERROR log.txt; then ...`.

**`-s`, `--no-messages`**
: Do not report missing or unreadable files and directories. The exit status still reports the
error.

**`-H`, `--with-filename`**
: Start each output line (and each count) with the file name, even for a single file.

**`-h`, `--no-filename`**
: Never start output lines with the file name. If both `-H` and `-h` are given, the last one
wins. Note that `-h` does **not** mean help; use `--help`.

If several of `-q`, `-l`, and `-c` are given, `-q` wins over `-l`, which wins over `-c`.

### File selection

**`-r`, `--recursive`**
: Search each directory operand, and all of its subdirectories, in a fixed order: entries are
sorted by the bytes of their names (so `B.txt` comes before `a.txt`, and the directory `a`
comes before `a-b.txt` and `a.txt`), and the contents of a subdirectory are searched at the
point where its name appears. Names that start with `.` are searched too. Symbolic links
found inside a directory are skipped; a symbolic link given as an operand is followed. With
no _FILE_, the current directory is searched and names are printed without a leading `./`.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-grep` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be combined: `-rn` is `-r -n`, and `-efox` is `-e fox`.
- Long options must be spelled out in full; `--count` works, `--cou` does not.
- Options and operands can be mixed: `dp-grep fox -n poem.txt` works.
- `--` ends option processing: `dp-grep -- -x notes.txt` searches for `-x`.

## PATTERN SYNTAX

A pattern is made of the following pieces. Everything else is rejected (see DIAGNOSTICS).

| Syntax                    | Meaning                                                                                                                                                                 |
| :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `c`                       | Any ordinary character matches itself. `]` and `}` are ordinary characters. Non-ASCII characters such as `ë` are allowed and match themselves                           |
| `\c`                      | One of the fourteen special characters `^ . [ ] $ ( ) \| * + ? { } \`, matched literally. A backslash before any other character is an error                            |
| `.`                       | Any single byte                                                                                                                                                         |
| `[abc]`, `[a-z]`          | Any one byte from the list; `a-z` is a range of ASCII characters                                                                                                        |
| `[^abc]`                  | Any one byte **not** in the list (including non-ASCII bytes)                                                                                                            |
| `[[:digit:]]`             | A character class inside a bracket expression: `alpha`, `digit`, `alnum`, `upper`, `lower`, `space`, `blank`, `punct`, `print`, `graph`, `cntrl`, `xdigit` (ASCII only) |
| `^`, `$`                  | The start and the end of the line                                                                                                                                       |
| `x*`, `x+`, `x?`          | Zero or more, one or more, zero or one `x`                                                                                                                              |
| `x{m}`, `x{m,}`, `x{m,n}` | Exactly m, at least m, from m to n `x` (m and n at most 255)                                                                                                            |
| `x\|y`                    | Either `x` or `y`                                                                                                                                                       |
| `(x)`                     | Grouping, so that a quantifier applies to all of `x`                                                                                                                    |

Inside brackets, every ASCII character is literal, including `\`, `.`, and `*`. To include `]`,
put it first (`[]a]`); to include `-`, put it first or last (`[a-]`). Brackets may contain only
ASCII characters.

Some consequences of the byte-based design:

- `.` matches one byte, so `^.{3}$` does not match `Zoë`, whose `ë` takes two bytes.
- `ë+` repeats the whole character `ë`.
- `$` matches only at the very end of the line. In a file with CRLF line endings, use `x.$` or
  `x[[:cntrl:]]?$` rather than `x$` to find lines ending in `x`.
- Group nesting is limited to 100 levels, and nested repetition counts multiplied together
  (for example `(a{30}){33}` = 990) must not exceed 1000.

## EXIT STATUS

| Status | Meaning                                                                                |
| :----- | :------------------------------------------------------------------------------------- |
| 0      | At least one line was selected (with `-q`: even if an error occurred)                  |
| 1      | No line was selected, and no error occurred                                            |
| 2      | An error occurred: a usage error, an invalid pattern, or a file that could not be read |

With `-v`, "selected" means "did not match", so `dp-grep -v x` exits 0 if some line lacks `x`.

## DIAGNOSTICS

Errors are written to standard error. Usage errors are followed by a hint line:

```text
$ dp-grep --cuont fox poem.txt
dp-grep: unrecognized option '--cuont'
Try 'dp-grep --help' for more information.
```

| Message                                      | Cause                                     | Fix                         |
| :------------------------------------------- | :---------------------------------------- | :-------------------------- |
| `invalid option -- 'Z'`                      | Unknown short option                      | Check the option letter     |
| `unrecognized option '--xyz'`                | Unknown or abbreviated long option        | Spell the option in full    |
| `option requires an argument -- 'e'`         | `-e` at the end of the command            | Give the pattern after `-e` |
| `option '--regexp' requires an argument`     | `--regexp` at the end of the command      | Give the pattern            |
| `option '--count' doesn't allow an argument` | `--count=…` or another flag given a value | Remove the `=…`             |
| `missing operand`                            | No pattern was given                      | Give a pattern, or use `-e` |

An invalid pattern is reported as `dp-grep: invalid pattern '<PATTERN>': <reason>` (no hint
line) and nothing is searched:

| Reason                                      | Example                              | Cause                                                                                 |
| :------------------------------------------ | :----------------------------------- | :------------------------------------------------------------------------------------ |
| `unsupported escape \1`                     | `(a)\1`                              | Backreferences are not supported                                                      |
| `unsupported escape \d`                     | `\d+`, `\w`, `\s`, `\b`, `\-`, `\n`  | Only the fourteen special characters may follow `\`; use `[0-9]` for digits           |
| `trailing backslash`                        | `abc\`                               | A pattern cannot end with `\`                                                         |
| `nothing to repeat`                         | `*a`, `(?=x)`, `(?i)x`, `^*`         | A quantifier needs something before it; lookaround and inline flags are not supported |
| `multiple repeat`                           | `a+?`, `a**`                         | Only one quantifier per item; lazy and possessive forms are not supported             |
| `invalid interval`                          | `a{2,1}`, `a{256}`, `a{,3}`, `f{oo}` | Use `{m}`, `{m,}`, or `{m,n}` with m ≤ n ≤ 255; write a literal brace as `\{`         |
| `repetition too large`                      | `(a{30}){40}`                        | Nested repetition counts multiply to more than 1000                                   |
| `nesting too deep`                          | 101 nested `(`                       | More than 100 nested groups                                                           |
| `unmatched (`                               | `(lazy\|dog`                         | A group is not closed                                                                 |
| `unmatched )`                               | `a)`                                 | `)` without a matching `(`; write `\)` for a literal                                  |
| `unmatched [`                               | `[abc`, `[[:alpha]`                  | A bracket expression is not closed                                                    |
| `invalid character class`                   | `[[:word:]]`                         | Use one of the twelve class names                                                     |
| `invalid range`                             | `[z-a]`, `[[:digit:]-z]`             | Range ends must be single characters in ascending order                               |
| `unsupported bracket construct`             | `[[.a.]]`, `[[=a=]]`                 | Collating elements and equivalence classes are not supported                          |
| `non-ASCII character in bracket expression` | `[éè]`                               | Use alternation instead: `(é\|è)`                                                     |

File problems are reported as `dp-grep: <file>: <reason>`, where the reason is one of
`No such file or directory`, `Permission denied`, `Is a directory` (a directory given without
`-r`), `Not a directory`, or `Input/output error`. The search continues with the next file, and
the exit status becomes 2. Use `-s` to hide these messages.

## EXAMPLES

Find the lines that mention a fox:

```text
$ dp-grep fox poem.txt
The quick brown fox
a fox, a box, a sock
the fox knows (a) secret
```

Several alternatives, with line numbers:

```text
$ dp-grep -n 'the|fox' poem.txt
1:The quick brown fox
2:jumps over the lazy dog.
4:a fox, a box, a sock
7:the fox knows (a) secret
```

Whole lines in a fixed format:

```text
$ dp-grep -n '^[0-9]{3}-[0-9]{4}$' phones.txt
1:555-0100
5:555-0123
```

Count whole-word matches:

```text
$ dp-grep -w -c cat words.txt
2
```

Search a directory tree:

```text
$ dp-grep -r fox tree
tree/.hidden.txt:a hidden fox
tree/a/deep.txt:a deep fox
tree/a-b.txt:the fox is here
tree/a.txt:fox in a
tree/a.txt:second fox
tree/b/c/notes.txt:fox again
```

A pattern from another tool's dialect:

```text
$ dp-grep '\d+' phones.txt
dp-grep: invalid pattern '\d+': unsupported escape \d
$ dp-grep -c '[0-9]+' phones.txt
6
```

Use the exit status in a script:

```sh
if dp-grep -q -F 'FAILED' report.txt; then
    echo "the report contains failures"
fi
```

Show the version:

```text
$ dp-grep --version
dp-grep (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-grep --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-grep [OPTION]... PATTERN [FILE]...
  or:  dp-grep [OPTION]... -e PATTERN... [FILE]...
Search each FILE for lines that match a pattern.

PATTERN is a portable extended regular expression (see the user manual).
With no FILE, read standard input, or the working directory with -r.
A FILE of - means standard input.

Options:
  -e, --regexp=PATTERN      use PATTERN; may be given more than once
  -F, --fixed-strings       treat every PATTERN as a literal string
  -i, --ignore-case         ignore ASCII letter case
  -v, --invert-match        select lines that do not match
  -x, --line-regexp         a pattern must match the whole line
  -w, --word-regexp         a pattern must match a whole word
  -n, --line-number         prefix each selected line with its line number
  -c, --count               print only a count of selected lines per file
  -l, --files-with-matches  print only the names of files with selected lines
  -q, --quiet               print nothing; exit 0 at the first selected line
  -s, --no-messages         suppress diagnostics about unreadable files
  -r, --recursive           search directories recursively
  -H, --with-filename       prefix each output line with the file name
  -h, --no-filename         never prefix output lines with the file name
      --help                display this help and exit
      --version             output version information and exit

Exit status is 0 if a line is selected, 1 if no line is selected, and 2 if an
error occurred; with -q, a selected line gives 0 even after an error.
```

## VERSION OUTPUT

```text
dp-grep (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-grep` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Case-insensitive matching and character classes always use the ASCII definitions.

## PLATFORM NOTES

- **Paths:** paths you type are printed exactly as typed, so on Windows `dp-grep -r x src\lib`
  prints `src\lib/util.c:...`: your `\` is kept, and the separator `dp-grep` adds is `/`. A
  trailing separator is not doubled: `tree/` gives `tree/a.txt`, and on Windows `tree\` gives
  `tree\a.txt`.
- **Line endings:** output always uses LF. Lines from CRLF files keep their CR, so they print
  back unchanged, and a pattern ending in `$` must allow for the CR.
- **Order:** the order of `-r` results never depends on the file system; it is the byte-wise
  order of the names, which puts upper-case names before lower-case ones.
- **Quoting:** in bash and zsh, put patterns in single quotes (`'a|b'`, `'x$'`). In PowerShell
  use single quotes as well; in `cmd.exe` use double quotes, and note that `^` is `cmd.exe`'s
  escape character (`"^abc"` inside double quotes is passed unchanged).
- **Differences from other grep programs:** there is no binary-file detection, no `-o`, no
  color, no context options, and no `-L`. A newline inside a pattern is an ordinary character
  (which no line can contain), not a separator between several patterns; use `-e` once per
  pattern instead.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`grep(1)`, `regex(7)`; `dp-cat` (project 02), `dp-find` (project 06).

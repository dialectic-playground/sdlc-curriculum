# dp-find — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-find` 1.0.0 |
| Project | `06-find-lite` — Recursive File Discovery Suite |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-06), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-find** — search directory trees for entries that match an expression

## SYNOPSIS

```text
dp-find [PATH]... [EXPRESSION]
dp-find --help
dp-find --version
```

## DESCRIPTION

`dp-find` walks the directory tree below each *PATH* and evaluates *EXPRESSION* for every
entry it reaches: the *PATH* itself, then everything beneath it. With no *PATH*, it searches the
current directory `.`. The expression combines *tests* (such as `-name '*.c'`), *global
options* (`-maxdepth`, `-mindepth`), *actions* (`-print`, `-exec`), and *operators* (`!`,
`-a`, `-o`, parentheses). If the expression contains no action, `dp-find` prints the path of
every entry for which the expression is true; with no expression at all, it prints every entry.

The order of the results is the same on every operating system:

- Each *PATH* is searched completely, in the order given.
- A directory is listed before its contents (*pre-order*).
- The entries of each directory are visited in ascending **byte-wise** order of their UTF-8
  names. This order is case-sensitive and ignores the locale: `B.txt` comes before `a.txt`,
  and `a-b` comes before `a.b`, `a1`, and `a_b`.

Paths are printed as reached: the *PATH* exactly as you typed it, then `/` and each name below
it, even on Windows. Searching `.` therefore prints `.`, `./src`, `./src/main.c`, and so on.
No extra `/` is added after a *PATH* that already ends in one: `dp-find src/` prints
`src/main.c`.

Symbolic links (and Windows directory junctions) are never followed. They are reported like other
entries, but they are neither files (`-type f`) nor directories (`-type d`).

`dp-find` never changes the file system itself and never reads standard input.

## OPTIONS

Start paths come first, then the expression. A start path cannot begin with `-` and cannot be
`(`, `)`, or `!`; write `./-odd-name` to search a directory called `-odd-name`.

In most shells, `(`, `)`, `!`, and `;` must be quoted or escaped: write `'('`, `')'`,
`'!'` (in interactive bash or zsh), and `';'` or `\;`. Quote glob patterns as well, so the shell
does not expand them: `-name '*.txt'`.

### Operators

Listed from highest to lowest precedence:

**`( EXPR )`**
: True if *EXPR* is true. Use parentheses to override precedence.

**`! EXPR`**, **`-not EXPR`**
: True if *EXPR* is false.

**`EXPR1 EXPR2`**, **`EXPR1 -a EXPR2`**
: AND: true if both are true. *EXPR2* is not evaluated when *EXPR1* is false. Writing two
  expressions next to each other means AND.

**`EXPR1 -o EXPR2`**
: OR: true if either is true. *EXPR2* is not evaluated when *EXPR1* is true.

Because AND binds more tightly than OR, `-type f -name '*.c' -o -name '*.h'` means
`( -type f -name '*.c' ) -o -name '*.h'`. To select regular files with either extension, write
`-type f '(' -name '*.c' -o -name '*.h' ')'`.

### Global options

These are always true. They affect the whole search wherever they appear in the expression; if
one is given more than once, the last one counts. *N* is a whole number from 0 to 2147483647.

**`-maxdepth N`**
: Descend at most *N* levels below each start path. `-maxdepth 0` examines only the start paths
  themselves.

**`-mindepth N`**
: Do not evaluate entries fewer than *N* levels below their start path (their contents are still
  searched). `-mindepth 1` skips the start paths themselves.

### Tests

**`-name GLOB`**
: True if the entry's base name (the last component of its path) matches the glob pattern
  *GLOB* as a whole. Matching is case-sensitive on every system. The pattern language:

  | Pattern | Matches |
  | :-- | :-- |
  | `*` | any sequence of characters, including none and including a leading `.` |
  | `?` | exactly one character |
  | `[abc]`, `[a-z]` | one character from the set or range |
  | `[!abc]`, `[!a-z]` | one character *not* in the set or range |
  | `\c` | the character *c* literally, for example `\*` or `\[` |

  Inside brackets, a `]` right after `[` or `[!` is an ordinary member, and a `-` at the start
  or end is literal. A `[` without a closing `]` is an ordinary character. `^` and
  `[:alpha:]`-style classes have no special meaning. For a start path, the base name ignores
  trailing slashes: the base name of `src/` is `src`, and that of `.` is `.`.

**`-iname GLOB`**
: Like `-name`, but the ASCII letters A–Z and a–z match regardless of case. Other letters, such
  as `É` and `é`, are still compared exactly.

**`-type f`**, **`-type d`**
: True for a regular file (`f`) or a directory (`d`). No other letters are accepted.

**`-size [+|-]N[UNIT]`**
: Compares the entry's size, **rounded up** to whole units, with *N*. *UNIT* is `c` (bytes),
  `k` (KiB, 1024 bytes), `M` (MiB), `G` (GiB), or omitted for 512-byte blocks. `+N` means more
  than *N* units, `-N` fewer than *N*, and `N` exactly *N*. Because of the rounding,
  `-size -1k` matches only empty files, `-size 1k` matches sizes of 1 to 1024 bytes, and
  `-size -2k` matches files of at most 1024 bytes. Use `c` for exact byte comparisons:
  `-size +1024c` means larger than 1024 bytes. Directory sizes differ between operating
  systems, so combine `-size` with `-type f`.

**`-mtime [+|-]N`**
: Compares the entry's age with *N* days. The age is the time since the entry was last modified,
  in **whole** days rounded down, measured from the moment the search started. A file changed an
  hour ago has age 0, so `-mtime 0` and `-mtime -1` match it; `-mtime +7` matches entries last
  modified 8 or more days ago.

**`-empty`**
: True for an empty regular file and for a directory with no entries.

### Actions

**`-print`**
: Print the entry's path followed by a newline. Always true.

**`-exec COMMAND ;`**
: Run *COMMAND* once for the entry and wait for it to finish. *COMMAND* is every argument up to
  the next `;` argument. Each `{}` in any of these arguments, even inside a longer argument
  like `backup-{}`, is replaced by the entry's path. The command is started directly, not by a
  shell, so no quoting, wildcards, or redirections are interpreted. It runs in the current
  directory, with the same environment, standard input, standard output, and standard error as
  `dp-find`. `-exec` is true if the command exits with status 0, so it can also act as a test.
  If the command cannot be started, `dp-find` reports it, treats `-exec` as false, and exits
  with status 1 at the end.

### Standard options

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

`--help` and `--version` work anywhere in the expression, except as another primary's
argument (`-name --help` searches for entries called `--help`). They take effect as soon as
they are reached while reading the arguments from left to right, unless an earlier argument was
invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: every path was searched without error, or help or version was printed |
| 1 | At least one path could not be examined or read, or an `-exec` command could not be started; everything else was still searched |
| 2 | Usage error in the expression; nothing was searched |

A command run by `-exec` that exits with a non-zero status is not an error. It only makes that
`-exec` false.

## DIAGNOSTICS

Usage errors are written to standard error as two lines, and nothing is searched:

```text
$ dp-find . -nme '*.c'
dp-find: unknown primary '-nme'
Try 'dp-find --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `unknown primary '-nme'` | A word starting with `-` that is not a test, action, or operator | Check the spelling; see `--help` |
| `missing argument to '-name'` | The primary is the last argument | Supply its argument |
| `missing argument to '-exec'` | No `;` after the command, or no command before `;` | End the command with `';'` |
| `invalid argument '5K' for '-size'` | Malformed number, sign, unit, or type letter | Use the forms shown in OPTIONS |
| `paths must precede expression: 'src'` | A path appears after the expression has started | Move all paths to the front |
| `expected an expression after '-o'` | An operator with nothing after it | Complete or remove the operator |
| `expected an expression before '-o'` | `-o` or `-a` with nothing before it | Complete or remove the operator |
| `empty parentheses` | `( )` | Put an expression inside |
| `missing ')'` | A `(` is never closed | Add the `)` |
| `unexpected ')'` | A `)` without a matching `(` | Remove it or add the `(` |

Runtime errors are one line each. The search continues, and the exit status becomes 1:

| Message | Cause |
| :-- | :-- |
| `dp-find: srcc: No such file or directory` | A path that does not exist |
| `dp-find: a.txt/x: Not a directory` | A path through something that is not a directory |
| `dp-find: ./private: Permission denied` | A directory you may not read; it is still printed, but its contents are skipped |
| `dp-find: lint: No such file or directory` | An `-exec` program that cannot be found |
| `dp-find: <path>: Input/output error` | Any other failure reported by the operating system |

## EXAMPLES

The examples use this tree:

```text
$ dp-find tree
tree
tree/a-b.txt
tree/a.txt
tree/a_b.txt
tree/ab.txt
tree/data.bin
tree/docs
tree/docs/guide.md
tree/docs/huge.md
tree/docs/img
tree/docs/img/.keep
tree/empty.log
tree/notes.md
tree/src
tree/src/.hidden.txt
tree/src/lib
tree/src/lib/core.c
tree/src/lib/core.h
tree/src/main.c
tree/src/util.c
```

Find files by name (`*` also matches names that start with a dot):

```text
$ dp-find tree -name '*.txt'
tree/a-b.txt
tree/a.txt
tree/a_b.txt
tree/ab.txt
tree/src/.hidden.txt
```

List only directories, or only the top level:

```text
$ dp-find tree -type d
tree
tree/docs
tree/docs/img
tree/src
tree/src/lib
$ dp-find tree -mindepth 1 -maxdepth 1 -type d
tree/docs
tree/src
```

Combine conditions with parentheses:

```text
$ dp-find tree -type f '(' -name '*.md' -o -name '*.log' ')'
tree/docs/guide.md
tree/docs/huge.md
tree/empty.log
tree/notes.md
```

Find files larger than 1 KiB (`guide.md` is exactly 1024 bytes, `huge.md` 1025):

```text
$ dp-find tree -type f -size +1024c
tree/data.bin
tree/docs/huge.md
```

Exclude entries with `!`, and find empty files:

```text
$ dp-find tree/src -type f ! -name '*.c'
tree/src/.hidden.txt
tree/src/lib/core.h
$ dp-find tree -empty
tree/docs/img/.keep
tree/empty.log
```

Run a command for every match. Here `wc -c` prints each file's size, and `-print` follows it:

```text
$ dp-find tree/src -name '*.c' -exec wc -c {} ';' -print
30 tree/src/lib/core.c
tree/src/lib/core.c
29 tree/src/main.c
tree/src/main.c
35 tree/src/util.c
tree/src/util.c
```

Use a command as a test: print the files that contain `return` (`grep -q` exits 0 on a match):

```sh
dp-find tree -type f -exec grep -q return {} ';' -print
```

A missing path is reported, and the other paths are still searched:

```text
$ dp-find nope tree/docs/img
dp-find: nope: No such file or directory
tree/docs/img
tree/docs/img/.keep
$ echo $?
1
```

## HELP OUTPUT

`dp-find --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-find [PATH]... [EXPRESSION]
Search directory trees, evaluating EXPRESSION for every entry found.

With no PATH, search the current directory '.'.  If EXPRESSION contains no
action, -print is applied to every entry for which EXPRESSION is true.

Operators (highest precedence first):
  ( EXPR )             group EXPR
  ! EXPR, -not EXPR    true if EXPR is false
  EXPR EXPR, EXPR -a EXPR
                       true if both are true (the right one is skipped
                       if the left one is false)
  EXPR -o EXPR         true if either is true (the right one is skipped
                       if the left one is true)

Global options (always true):
  -maxdepth N          descend at most N levels below the starting points
  -mindepth N          do not evaluate entries fewer than N levels deep

Tests:
  -name GLOB           base name matches GLOB (* ? [...] [!...] \)
  -iname GLOB          like -name, but ASCII letters match either case
  -type f|d            entry is a regular file (f) or a directory (d)
  -size [+|-]N[ckMG]   size rounded up to whole units (c bytes, k KiB,
                       M MiB, G GiB, default 512-byte blocks) is more
                       than (+), less than (-), or exactly N
  -mtime [+|-]N        last modified more than (+), less than (-), or
                       exactly N whole days ago
  -empty               entry is an empty regular file or empty directory

Actions:
  -print               print the path followed by a newline; true
  -exec COMMAND ;      run COMMAND with every {} replaced by the path;
                       true if it exits with status 0

Options:
      --help           display this help and exit
      --version        output version information and exit
```

## VERSION OUTPUT

```text
dp-find (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-find` ignores locale settings (`LANG`, `LC_ALL`) and every other environment variable,
except that `PATH` (and, on Windows, the variables the system's program search uses) determines
where `-exec` finds a command given without a directory. Commands run by `-exec` receive the
environment unchanged.

## PLATFORM NOTES

- **Windows:** output uses `/` between the directories `dp-find` adds and LF line endings,
  exactly as on Linux. A path you type is printed as typed, so `dp-find src\lib` prints
  `src\lib` and then `src\lib/core.c`. Paths longer than the traditional 260-character
  limit are searched normally. Folders you may not open, such as
  `C:\System Volume Information`, are reported as `Permission denied` and skipped. In
  PowerShell, quote the special arguments: `dp-find . '(' -name '*.md' -o -name '*.txt' ')'` and
  end `-exec` with `';'`. The command run by `-exec` is started directly, so built-in
  `cmd.exe` commands such as `dir` or `echo` need `cmd /c`: `-exec cmd /c echo {} ';'`.
- **macOS / Linux:** escape or quote `(`, `)`, `;`, and in interactive bash or zsh `!`.
  Names are matched case-sensitively even on the case-insensitive file systems that macOS uses by
  default; use `-iname` to ignore ASCII case.
- **All systems:** directory sizes, and the modification times of directories copied by other
  tools, vary between systems; prefer `-size` and `-mtime` together with `-type f`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`find(1)`, `glob(7)`, `fnmatch(3)`; `dp-grep` (project 05), `dp-env` (project 08).

# Software Requirements Specification (SRS) — dp-find

| Field | Value |
| :-- | :-- |
| Document ID | SRS-06 |
| Project | `06-find-lite` — Recursive File Discovery Suite |
| Product | `dp-find` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-06) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0), with the overrides in §1.5 |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-find`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation on a given file system tree. It is the authoritative source for
design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-find` traverses the directory trees rooted at its start paths and evaluates a boolean
*expression* for every entry it reaches. The expression is built from *tests* (name, type,
size, modification age, emptiness), *global options* (depth limits), *actions* (print the path,
run a command), and *operators* (NOT, AND, OR, parentheses). The syntax and semantics are a
subset of POSIX/GNU `find`, made deterministic across operating systems.

### 1.3 Definitions

| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Start path | An argument naming the place where a traversal begins (FR-01) |
| Entry | A file system object visited during traversal: a start path or anything beneath one |
| Depth | 0 for a start path; one more than its parent directory's depth for every other entry |
| Path of an entry | The start path exactly as given, or the path constructed per FR-07 |
| Base name | The name an entry's name tests are matched against (FR-08) |
| Metadata | The type, size, and modification time of an entry, read **without following symbolic links** |
| Primary | A test, global option, or action token, together with its arguments |
| Expression | The sequence of primaries and operators that follows the start paths |
| Separator | `/` on every platform; on Windows, `\` is also a separator **when reading** a user-supplied path |
| Byte-wise order | Ascending order of names compared as sequences of unsigned bytes of their UTF-8 encoding (CONV-21) |
| T | The reference time: the current time, read once after the command line has been accepted and before the first start path is examined |

### 1.4 References
- URD-06: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- POSIX.1-2017, `find` utility (informative: the model this tool simplifies)

### 1.5 Deliberate overrides of CLI-CONV

`dp-find` uses a `find`-style expression grammar instead of CLI-CONV option syntax. The
following CLI-CONV clauses are replaced for this tool; every other clause applies unchanged.

| CLI-CONV clause | Override in this SRS |
| :-- | :-- |
| CONV-07, CONV-08 (short/long options) | There are no short or long options except `--help` and `--version`. Words such as `-name` are *primaries* (FR-02). No bundling, no `--name=value` forms. |
| CONV-09 (`--` terminator) | `--` has no special meaning. In expression position it is an unknown primary. |
| CONV-10 (operands, interleaving, `-` = stdin) | Start paths must precede the expression and cannot begin with `-` (FR-01). `-` is not standard input; `dp-find` never reads standard input. |
| CONV-11 (repetition) | Applies to `-maxdepth` and `-mindepth` (last occurrence wins). Other primaries may repeat; each occurrence is an independent part of the expression. |
| CONV-12 (scan order) | `--help` and `--version` are recognized only in expression position, never as a primary's argument. The scan of FR-02 defines which usage errors are "earlier"; expression-structure errors (FR-04) are found only after the scan completes, so `dp-find '(' --help` prints the help. |
| CONV-13 (usage messages) | Replaced by the messages in §6.1. `invalid argument '<value>' for '<primary>'` keeps the CONV-13 format. `--help=x` is reported as an unknown primary. |
| CONV-16 (path errors) | Also used for commands that cannot be started (FR-16), with the command name in place of `<path>`. |
| CONV-26 (stdin) | `dp-find` does not read standard input; commands run by `-exec` inherit it. |

## 2. Overall description

### 2.1 Product perspective
`dp-find` is a standalone executable. Its interfaces are the command line, the file system
(read-only), child processes started by `-exec`, standard output, standard error, and the exit
status.

### 2.2 Product functions
1. Traverse one or more directory trees in a fixed, platform-independent order.
2. Evaluate name, type, size, age, and emptiness tests combined with boolean operators.
3. Limit traversal and evaluation by depth.
4. Print matching paths or run a command for each match.
5. Report missing and unreadable paths without stopping, and reject malformed expressions.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- `dp-find` itself MUST NOT create, modify, or delete any file system object.

### 2.4 Assumptions
- File names are UTF-8 on POSIX systems (other bytes are handled per FR-08) and UTF-16 on
  Windows.
- The tree is not modified while it is being traversed. If it is, `dp-find` must still not
  crash (NFR-05); entries that vanish are reported per FR-18.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-find [PATH]... [EXPRESSION]
dp-find --help
dp-find --version
```

### 3.2 Expression elements

Operators, in decreasing precedence:

| Syntax | Meaning |
| :-- | :-- |
| `( EXPR )` | Grouping. True if EXPR is true. |
| `! EXPR`, `-not EXPR` | Negation. True if EXPR is false. |
| `EXPR EXPR`, `EXPR -a EXPR` | Conjunction (AND). The right operand is evaluated only if the left one is true. |
| `EXPR -o EXPR` | Disjunction (OR). The right operand is evaluated only if the left one is false. |

Primaries:

| Primary | Kind | Argument | True when |
| :-- | :-- | :-- | :-- |
| `-name GLOB` | test | glob (FR-08) | the base name matches GLOB |
| `-iname GLOB` | test | glob (FR-09) | the base name matches GLOB, ASCII letters compared case-insensitively |
| `-type C` | test | `f` or `d` (FR-10) | the entry is a regular file (`f`) or a directory (`d`) |
| `-size [+\|-]N[U]` | test | size (FR-11) | the size, rounded up to units, is more than / less than / equal to N |
| `-mtime [+\|-]N` | test | age (FR-12) | the age in whole days is more than / less than / equal to N |
| `-empty` | test | none (FR-13) | the entry is an empty regular file or an empty directory |
| `-maxdepth N` | global option | depth (FR-14) | always (sets the traversal limit) |
| `-mindepth N` | global option | depth (FR-14) | always (sets the evaluation threshold) |
| `-print` | action | none (FR-07) | always (prints the path) |
| `-exec WORD... ;` | action | command (FR-15) | the command exits with status 0 |
| `--help` | standard | none | prints help, exits 0 (FR-19) |
| `--version` | standard | none | prints version, exits 0 (FR-20) |

In shells, `(`, `)`, `!`, and `;` usually need quoting or escaping: `'('`, `\)`, `';'`.

### 3.3 Operands
The start paths (FR-01). If none is given, the single start path `.` is used.

### 3.4 Standard input
Not read by `dp-find`. Commands run by `-exec` inherit it (FR-15).

### 3.5 Standard output
The lines written by `-print` actions (FR-07), interleaved in execution order with the output
of commands run by `-exec`. Nothing else. Nothing at all when a usage error occurs.

### 3.6 Standard error
Diagnostics only (§6), plus whatever commands run by `-exec` write to their inherited standard
error.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every start path was traversed without a runtime failure, or `--help` / `--version` was handled |
| 1 | At least one runtime failure occurred: a start path or entry whose metadata could not be read, a directory that could not be read, or a command that could not be started (FR-16, FR-17, FR-18). Traversal continued after each failure. |
| 2 | Usage error (§6.1). Nothing was traversed and no command was run. |

A command run by `-exec` that exits with a non-zero status is **not** a failure; it only makes
that `-exec` false.

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
Examples refer to the fixture tree used by the black-box tests (`tests/fixtures/tree`, see §7).

### 4.1 Command line

**FR-01: Start paths.**
The start paths are the longest leading run of arguments each of which neither begins with `-`
nor is exactly `(`, `)`, or `!`. Every remaining argument belongs to the expression. A start
path may be any other string, including the empty string. If there are no start paths, the
single start path `.` is used. A path that begins with `-` can be given by prefixing it, as in
`./-x`.
*AC:* `dp-find tree/docs` traverses `tree/docs`; `dp-find -type d` traverses `.`. *(UR-02)*

**FR-02: Scanning the expression.**
The expression arguments MUST be scanned from left to right, one token at a time, as follows:

1. `--help` or `--version`: the tool immediately performs FR-19 or FR-20 and exits with status
   0. No further argument is examined.
2. `(`, `)`, `!`, `-not`, `-a`, `-o`: an operator token.
3. `-print`, `-empty`: a primary with no argument.
4. `-name`, `-iname`, `-type`, `-size`, `-mtime`, `-maxdepth`, `-mindepth`: the **next**
   argument, whatever it is (even `;`, `)`, `-o`, or `--help`), is this primary's argument. If
   there is no next argument, the usage error `missing argument to '<primary>'` is reported. The
   argument is validated immediately (FR-08 … FR-14); an invalid one is reported as
   `invalid argument '<argument>' for '<primary>'`.
5. `-exec`: the command words are the following arguments up to, but not including, the next
   argument that is exactly `;`; that `;` is consumed and scanning resumes after it. If there is
   no such `;`, or there are no words before it, the usage error `missing argument to '-exec'`
   is reported.
6. Any other argument that begins with `-` (including `-`, `--`, and `--help=x`): the usage
   error `unknown primary '<argument>'`.
7. Any other argument: the usage error `paths must precede expression: '<argument>'`.

The first usage error found stops the scan. Only when the whole scan succeeds is the expression
structure checked (FR-04).
*AC:* `dp-find tree -bogus` reports `unknown primary '-bogus'` and exits 2;
`dp-find tree -name` reports `missing argument to '-name'`; `dp-find -type f tree` reports
`paths must precede expression: 'tree'`; `dp-find tree -name --help` searches for entries named
`--help` and prints nothing. *(UR-13, UR-15)*

**FR-03: Expression grammar and evaluation.**
The token sequence MUST be parsed with this grammar, where *primary* is any primary token
from FR-02:

```text
expression := or-expr
or-expr    := and-expr { "-o" and-expr }
and-expr   := unary { [ "-a" ] unary }
unary      := ( "!" | "-not" ) unary
            | "(" or-expr ")"
            | primary
```

An empty token sequence is valid (FR-06). In `and-expr`, a `unary` that directly follows
another `unary` without `-a` is an implicit AND. Both binary operators are left-associative.
For every entry that is evaluated (FR-05), the expression is evaluated once, from left to right,
with short-circuiting: the right operand of AND is evaluated only when the left one is true, and
the right operand of OR only when the left one is false. The overall result is discarded; only
the actions' side effects matter.
*AC:* `dp-find tree -type f -mtime +1000 -o -name a.txt` prints only `tree/a.txt` (AND binds
tighter than OR); `dp-find tree -type f '(' -name '*.md' -o -name '*.log' ')'` prints the three
`.md` files and `tree/empty.log`. *(UR-09)*

**FR-04: Expression syntax errors.**
Parsing stops at the first error. Whenever the grammar requires a `unary` (at the start of a
non-empty expression, or after `(`, `!`, `-not`, `-a`, or `-o`) and the next token is the end
of the expression, `)`, `-a`, or `-o`, the usage error is chosen by the first matching rule:

| # | Situation | Message |
| :-- | :-- | :-- |
| 1 | The preceding token is `!`, `-not`, `-a`, or `-o` | `expected an expression after '<preceding token>'` |
| 2 | The next token is `-a` or `-o` | `expected an expression before '<next token>'` |
| 3 | The preceding token is `(` and the next token is `)` | `empty parentheses` |
| 4 | The preceding token is `(` and the expression has ended | `missing ')'` |
| 5 | Otherwise (start of the expression, next token `)`) | `unexpected ')'` |

In addition, when a parenthesized `or-expr` is complete and the expression ends instead of
continuing with `)`, the error is `missing ')'`; and when the top-level `or-expr` is complete
and the next token is `)`, the error is `unexpected ')'`.
*AC:* `'(' -type f -o ')'` → `expected an expression after '-o'`; `-o -print` →
`expected an expression before '-o'`; `'(' ')'` → `empty parentheses`; `'(' -print` →
`missing ')'`; `-print ')'` → `unexpected ')'`; `!` → `expected an expression after '!'`.
Each exits 2. *(UR-13)*

**FR-05: Traversal.**
Start paths MUST be processed in command-line order, each completely before the next (a start
path given twice is traversed twice). For each start path the tool visits entries in
**pre-order**: an entry is visited, then, if it is a directory that is to be descended, each of
its entries is visited recursively in byte-wise order of their names (CONV-21). `.` and `..`
are never visited. Visiting an entry means:

1. Read its metadata without following symbolic links. If that fails, report it per FR-17 (start
   path) or FR-18 (other entries) and skip the entry entirely.
2. If its depth is at least the minimum depth (FR-14), evaluate the expression for it (FR-03).
3. If it is a directory and its depth is less than the maximum depth (FR-14), read its list of
   entries and visit each one.

Symbolic links (on Windows: every reparse point that is a symbolic link or a directory junction)
are never followed, neither as start paths nor during traversal; such an entry is visited like
any other but is neither a regular file nor a directory, and is never descended. A directory's
list of entries MUST be read at most once per visit, even if both `-empty` and step 3 need it;
consequently a read failure is reported at most once per visit.
*AC:* `dp-find tree` lists `tree`, then `tree/a-b.txt`, `tree/a.txt`, `tree/a_b.txt`,
`tree/ab.txt`, …, with `tree/docs` immediately followed by its own contents and `tree/src/lib`
before `tree/src/main.c` (public test 01). *(UR-01, UR-11)*

**FR-06: Default action.**
If the expression contains no action (`-print` or `-exec`) anywhere, including inside negations
and in branches that are never evaluated, the expression E is evaluated as `( E ) -print`. If
the expression is empty, it is evaluated as `-print`. If the expression contains at least one
action, no implicit `-print` is added.
*AC:* `dp-find tree` prints every entry; `dp-find tree/src -name '*.c' -exec … ';'` prints no
paths of its own; `dp-find tree -maxdepth 0 -print -print` prints `tree` twice. *(UR-01, UR-09)*

**FR-07: Paths and `-print`.**
The path of a start path is the argument exactly as given (CONV-19). The path of every other
entry is its parent directory's path, followed by `/` (CONV-20), followed by the entry's name —
except that no `/` is inserted when the parent's path already ends in a separator (for example
the start path `tree/` yields `tree/a.txt`, and on Windows the start path `tree\` yields
`tree\a.txt`). `-print` writes the path's UTF-8 bytes (CONV-05) followed by LF to standard
output and is always true. On POSIX, a name's bytes are written exactly as stored, even if they
are not valid UTF-8. On Windows, names are converted from UTF-16 to UTF-8, and an unpaired
surrogate is written as its 3-byte generalized UTF-8 form.
*AC:* `dp-find -maxdepth 2 -name 'd*'` prints `./tree/data.bin` and `./tree/docs`;
`dp-find tree/` prints `tree/` then `tree/a-b.txt`. *(UR-11)*

### 4.2 Tests

**FR-08: `-name GLOB`.**
True if the entry's base name matches GLOB in its entirety. The **base name** of an entry found
by traversal is its directory-entry name. The base name of a start path is obtained by removing
all trailing separators; if nothing remains, the base name is the first character of the start
path (so `/` has base name `/`); otherwise it is the text after the last remaining separator, or
all of it if there is none (`.` → `.`, `./tree` → `tree`, `tree/docs///` → `docs`).

GLOB is read from left to right as a sequence of elements:

| Pattern text | Matches |
| :-- | :-- |
| `*` | any sequence of zero or more characters |
| `?` | exactly one character |
| `\` followed by a character *c* | the character *c* literally (so `\*` matches `*`) |
| `\` as the last character of GLOB | a literal `\` |
| `[` that starts a bracket expression (below) | exactly one character, per the bracket expression |
| `[` with no terminating `]` | a literal `[`; reading resumes after it |
| any other character *c* | *c* itself |

A **bracket expression** starts at `[`. If the next character is `!`, the expression is
*negated* and the `!` is consumed. The members follow. A `]` in the first member position (right
after `[` or `[!`) is a literal member. The expression ends at the first later `]` that is not
consumed as a member by the following rules. Within it, `\` followed by a character yields that
character as a literal member (an escaped `]` never ends the expression, and an escaped `-` never
forms a range). A **range** is a member character *c1* followed by an unescaped `-` that is not
immediately followed by `]`, followed by a member character *c2* (which may itself be escaped);
it matches every character whose code point lies between those of *c1* and *c2* inclusive, and
matches nothing if *c1*'s code point is greater than *c2*'s. A `-` that is first, last, or
escaped is a literal member. `^` and `[:class:]` have no special meaning. A non-negated
expression matches one character that is a member or lies in a range; a negated expression
matches one character that does not.

Characters are Unicode code points of the name. On POSIX, each byte of a name that is not part
of a valid UTF-8 sequence counts as one character with code point U+DC00 plus the byte's value.
On Windows, an unpaired UTF-16 surrogate counts as one character. A leading `.` is not special,
and matching is always case-sensitive, even on case-insensitive file systems.
*AC:* `dp-find tree -name '*.txt'` prints `tree/a-b.txt`, `tree/a.txt`, `tree/a_b.txt`,
`tree/ab.txt`, and `tree/src/.hidden.txt` (public test 02). *(UR-03)*

**FR-09: `-iname GLOB`.**
True if the base name matches GLOB under FR-08 after the uppercase ASCII letters `A`–`Z` in both
GLOB and the base name have been replaced by the corresponding lowercase letters `a`–`z`. No
other characters are folded (`É` and `é` remain different).
*AC:* `dp-find tree -iname 'A*.TXT'` prints `tree/a-b.txt`, `tree/a.txt`, `tree/a_b.txt`, and
`tree/ab.txt`. *(UR-03)*

**FR-10: `-type C`.**
C MUST be exactly `f` or `d`; anything else is `invalid argument '<C>' for '-type'`. `-type f`
is true for regular files; `-type d` is true for directories. Symbolic links, junctions, and all
other entry kinds match neither (FR-05).
*AC:* `dp-find tree -type d` prints `tree`, `tree/docs`, `tree/docs/img`, `tree/src`, and
`tree/src/lib`; `-type l` is a usage error. *(UR-04)*

**FR-11: `-size [+|-]N[U]`.**
The argument is an optional sign (`+` or `-`), then one or more ASCII digits forming N, then an
optional unit letter U: `c` (1 byte), `k` (1024 bytes), `M` (1048576 bytes), or `G`
(1073741824 bytes). Without U, the unit is 512 bytes. N MUST NOT exceed 9223372036854775807.
Any other form (for example `10q`, `5K`, `+`, `1.5k`, or an empty string) is
`invalid argument '<argument>' for '-size'`.
Let S be the entry's size in bytes from its metadata and *units* = ⌈S ÷ unit⌉ (0 bytes is 0
units; 1 to 1024 bytes is 1 `k` unit). Then `+N` is true if *units* > N, `-N` if *units* < N,
and plain `N` if *units* = N. Consequently `-size -1k` matches only zero-byte entries, and
`-size -2k` matches entries of at most 1024 bytes. The size of an entry that is not a regular
file is whatever the operating system reports and differs between platforms; portable uses
combine `-size` with `-type f`.
*AC:* `dp-find tree -type f -size -2k` includes `tree/docs/guide.md` (1024 bytes) and excludes
`tree/docs/huge.md` (1025 bytes); `dp-find tree -type f -size +1024c` prints `tree/data.bin`
and `tree/docs/huge.md`. *(UR-05)*

**FR-12: `-mtime [+|-]N`.**
The argument is an optional sign (`+` or `-`) followed by one or more ASCII digits forming N,
with N not exceeding 9223372036854775807; any other form is
`invalid argument '<argument>' for '-mtime'`.
Let M be the entry's modification time from its metadata. Its *age* is
⌊(T − M) ÷ 86400 seconds⌋, computed at the best precision the platform provides and rounded
toward negative infinity (an entry modified up to one day in the future has age −1). Then `+N`
is true if *age* > N, `-N` if *age* < N, and plain `N` if *age* = N. T is read once per run
(§1.3), so every entry is compared with the same reference time.
*AC:* a file modified moments ago has age 0, so it matches `-mtime -1` and `-mtime 0` but not
`-mtime +1000` (hidden tests). *(UR-06)*

**FR-13: `-empty`.**
True for a regular file whose size is 0, and for a directory that contains no entries other than
`.` and `..`. False for every other entry. If the directory's entries cannot be read, `-empty`
is false and the failure is reported per FR-18 (once, FR-05).
*AC:* in the fixture tree, `dp-find tree -empty` prints `tree/docs/img/.keep` and
`tree/empty.log` (and an empty directory once one is created). *(UR-07)*

**FR-14: `-maxdepth N` and `-mindepth N`.**
N MUST consist only of ASCII digits (no sign) and not exceed 2147483647; anything else is
`invalid argument '<N>' for '-maxdepth'` (or `'-mindepth'`). These global options may appear
anywhere a primary may appear. Each occurrence evaluates to true at its position in the
expression, but its effect is global and independent of its position and of short-circuiting:
the last occurrence of each on the command line wins (CONV-11). No warning is printed about
their position.
- *Maximum depth* (default: unlimited): entries deeper than N are never visited; a directory at
  depth N is not descended and its entries are not read (unless `-empty` needs them).
- *Minimum depth* (default 0): the expression is not evaluated for entries shallower than N,
  but such directories are still descended.

If the minimum exceeds the maximum, nothing is evaluated.
*AC:* `dp-find tree -mindepth 1 -maxdepth 1` prints exactly the nine direct entries of `tree`;
`dp-find tree -maxdepth 0` prints only `tree`. *(UR-08)*

### 4.3 Actions

**FR-15: `-exec WORD... ;`.**
For each entry it is evaluated on, `-exec` builds an argument list from its command words by
replacing **every** occurrence of the two-character sequence `{}` in **every** word (including
the first, and within longer words such as `x{}y`) with the entry's path (FR-07). `+` is an
ordinary word. Words are used exactly as given; no shell is involved and no other expansion
occurs. The first resulting word names the program: if it contains a separator it is a path
(relative paths are relative to the current directory); otherwise it is located through the
`PATH` environment variable using the platform's standard program search (on Windows, the
standard process-creation search, under which `.exe` may be omitted).

The program runs synchronously in `dp-find`'s current directory (which `dp-find` never
changes), with `dp-find`'s environment unchanged, and with `dp-find`'s standard input, standard
output, and standard error. Before starting it, `dp-find` MUST flush everything it has buffered
for standard output and standard error, so that the combined output appears in execution order.
`-exec` is true if the program terminates normally with exit status 0, and false otherwise
(including termination by a signal). A false `-exec` is not a failure (§3.7).
*AC:* `dp-find tree/src -name '*.c' -exec {PYTHON} show.py {} ';' -print` prints, for each of
the three `.c` files, the helper's line `show.py: [<path>]` followed by the path (public test
08). *(UR-10)*

**FR-16: Command cannot be started.**
If the program cannot be started (for example, it does not exist or is not executable), the tool
MUST write `dp-find: <first word>: <reason>` to standard error, where `<first word>` is the first
word after `{}` replacement and `<reason>` is `No such file or directory` when the program was
not found, `Permission denied` when access was denied (including when the word names a
directory), and `Input/output error` for any other reason (CONV-16). That `-exec` is false,
traversal continues, and the final exit status is 1. The report MUST be written by `dp-find`
itself (an implementation that forks before executing must transfer the failure back to the
parent rather than letting a child process print or exit with a status).
*AC:* `dp-find tree/docs/img -exec no-such-command-dp {} ';' -o -print` prints both paths,
writes the diagnostic twice, and exits 1. *(UR-10, UR-12)*

### 4.4 Errors and standard behavior

**FR-17: Start path errors.**
If a start path's metadata cannot be read, the tool MUST write `dp-find: <start path>: <reason>`
with the CONV-16 reason (`No such file or directory` when it does not exist, `Not a directory`
when a component is not a directory, `Permission denied`, or `Input/output error`), skip it,
continue with the next start path (CONV-17), and finally exit with status 1. The empty string as
a start path does not exist.
*AC:* `dp-find nope tree/docs` reports `dp-find: nope: No such file or directory`, still lists
`tree/docs` and its contents, and exits 1 (public test 09). *(UR-12)*

**FR-18: Unreadable directories and entries (permission-denied states).**
If a directory's list of entries cannot be read (on POSIX typically EACCES for a directory
without read permission; on Windows typically `ERROR_ACCESS_DENIED` for a protected folder), the
tool MUST: (a) still evaluate the expression for the directory itself (it was already visited,
FR-05 step 2); (b) write `dp-find: <path>: <reason>` with the CONV-16 reason, once; (c) skip the
directory's contents; (d) continue with the directory's next sibling; and (e) finally exit with
status 1. If the metadata of an entry found in a listing cannot be read (for example, it was
deleted after the listing was read), the tool MUST report `dp-find: <path>: <reason>`, skip that
entry, continue, and finally exit with status 1. The reason text MUST never be the operating
system's own message, and `Is a directory` is never used by `dp-find`.
*AC (integration test, implementer-provided):* on POSIX, as a non-root user, a directory with
mode `000` inside a test tree is printed, reported once as `Permission denied`, and its siblings
are still listed; exit status 1. On Windows, the same holds for a directory whose ACL denies
the user `List folder contents`. *(UR-12)*

**FR-19: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan of FR-02.
*AC:* `dp-find --help` matches the user manual exactly; `dp-find tree '(' --help` prints the
help and exits 0; `dp-find tree -bogus --help` is a usage error. *(UR-15)*

**FR-20: Version.**
`--version` MUST write `dp-find (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-15)*

**FR-21: Usage-error atomicity.**
The entire command line MUST be scanned and parsed (FR-02 … FR-04) before any start path is
examined. When a usage error occurs, the tool MUST write nothing to standard output, examine no
path, and run no command. Every usage error is two lines on standard error: the message from
§6.1 prefixed with `dp-find: `, then `Try 'dp-find --help' for more information.` (CONV-14).
*AC:* `dp-find tree -exec {PYTHON} show.py {}` (no `;`) runs nothing, writes only the two
diagnostic lines, and exits 2. *(UR-13)*

**FR-22: Long paths (Windows MAX_PATH).**
On Windows, the tool MUST examine, list, and test entries whose full path is 260 characters or
longer, regardless of the system's long-path setting and of the application manifest — for
example by passing extended-length (`\\?\`-prefixed, absolute) paths or equivalent long-path
aware interfaces to the operating system. Any such internal form is used only when calling the
operating system: printed paths, diagnostics, and `{}` replacements MUST be the paths of FR-07.
On every platform, deep trees MUST be traversed without exhausting the call stack (NFR-05).
*AC (integration test, implementer-provided):* a tree created by the test whose deepest file path
exceeds 300 characters is listed completely and exactly as on Linux, with exit status 0.
*(UR-14)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output MUST be byte-identical on Linux, macOS, and Windows for the same tree, and every line MUST end in LF only (CONV-03). Constructed paths use `/` (CONV-20); entries are ordered byte-wise (CONV-21), never in file-system or locale order. | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform file systems | Long Windows paths MUST work (FR-22). Access-denied and vanished entries MUST be reported with fixed CONV-16 reasons and never stop the traversal (FR-18). Name tests MUST be case-sensitive (or ASCII-folded for `-iname`) independent of the file system's own case sensitivity. Symbolic links and junctions MUST NOT be followed (FR-05), so cycles cannot occur. | Integration tests; inspection |
| NFR-03 | Performance | For a tree of 10,000 entries in the operating system's file cache, `dp-find <tree>` MUST finish in under 1 s for a natively compiled build (under 3 s for an interpreted runtime) on CI hardware. Each directory MUST be listed once per visit, and each entry's metadata read once per visit. Output for an entry MUST NOT wait until the traversal has finished. | Measurement |
| NFR-04 | Memory | Memory use MUST NOT grow with the total number of entries in a tree. It MAY grow with the depth of the tree and the sizes of the directory listings along the current path. Peak memory MUST stay under 64 MiB for a tree of 100,000 entries with no directory larger than 10,000 entries. | Measurement |
| NFR-05 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or tree (CONV-24), including trees 10,000 levels deep (traversal must not use one native stack frame per level without bound) and entries that change during traversal. | Unit + integration tests |
| NFR-06 | Maintainability | Argument scanning, expression parsing, expression evaluation, glob matching, and traversal MUST be separate units (Principles 13, 18). | Design review |
| NFR-07 | Testability | Glob matching, numeric-argument parsing, size rounding, and age computation MUST be pure functions covered by unit tests. File system access MUST sit behind an interface so that permission-denied and long-path cases (FR-18, FR-22) can also be exercised with test doubles. | Code review |
| NFR-08 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-09 | Security | `dp-find` MUST NOT modify the file system, MUST NOT run a command through a shell, and MUST NOT read environment variables other than `PATH` (and, on Windows, the variables the platform's program search uses). It passes its environment to `-exec` commands unchanged. | Inspection |
| NFR-10 | Determinism | Results MUST NOT depend on locale (CONV-06), on the order in which the operating system returns directory entries, or on time beyond the single reference time T. | Inspection; CI |

## 6. Diagnostics (complete list)

### 6.1 Usage errors

Each diagnostic is followed by `Try 'dp-find --help' for more information.` and exit status 2.

| Trigger | Exact first line |
| :-- | :-- |
| Expression argument beginning with `-` that is not a primary or operator (FR-02) | `dp-find: unknown primary '<argument>'` |
| Primary `P` at the end of the arguments, or `-exec` without `;` or without a command word | `dp-find: missing argument to '<P>'` |
| Invalid argument `V` to `-type`, `-size`, `-mtime`, `-maxdepth`, `-mindepth` | `dp-find: invalid argument '<V>' for '<P>'` |
| Argument not beginning with `-` in expression position | `dp-find: paths must precede expression: '<argument>'` |
| Operand missing after an operator `OP` (FR-04 rule 1) | `dp-find: expected an expression after '<OP>'` |
| Binary operator `OP` with no left operand (FR-04 rule 2) | `dp-find: expected an expression before '<OP>'` |
| `(` immediately followed by `)` | `dp-find: empty parentheses` |
| `(` without a matching `)` | `dp-find: missing ')'` |
| `)` without a matching `(` | `dp-find: unexpected ')'` |

Values are inserted exactly as given, with no escaping (CONV-15). `-name` and `-iname` accept
every glob, so they never produce `invalid argument`.

### 6.2 Runtime errors

Each diagnostic is one line. Traversal continues, and the final exit status is 1.

| Trigger | Exact line |
| :-- | :-- |
| A start path's metadata cannot be read (FR-17) | `dp-find: <start path>: <reason>` |
| A directory's entries cannot be read (FR-13, FR-18) | `dp-find: <path>: <reason>` |
| An entry's metadata cannot be read (FR-18) | `dp-find: <path>: <reason>` |
| An `-exec` program cannot be started (FR-16) | `dp-find: <first word>: <reason>` |

`<reason>` is one of `No such file or directory`, `Not a directory`, `Permission denied`, or
`Input/output error`, chosen per CONV-16.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-08, FR-10, FR-11, FR-14, FR-15, FR-17 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-01 … FR-04, FR-06, FR-07, FR-09, FR-11 … FR-16, FR-21 |
| Unit test (written by the implementer) | FR-02 … FR-04, FR-08, FR-09, FR-11, FR-12, NFR-07 |
| Integration test (written by the implementer) | FR-18, FR-22, NFR-02, NFR-05 |
| Inspection / review / measurement | NFR-03, NFR-04, NFR-06, NFR-09, NFR-10 |

The black-box fixtures (`tests/fixtures/`, copied into every test's working directory) contain
two `-exec` helper scripts, `show.py` (prints `show.py:` followed by ` [<argument>]` for each
argument, then LF) and `make-dir.py` (creates the directory named by its argument), and this
tree (sizes in bytes):

```text
tree/a-b.txt (4)   tree/a.txt (12)   tree/a_b.txt (4)   tree/ab.txt (3)
tree/data.bin (2048)   tree/empty.log (0)   tree/notes.md (28)
tree/docs/guide.md (1024)   tree/docs/huge.md (1025)   tree/docs/img/.keep (0)
tree/src/.hidden.txt (7)   tree/src/main.c (29)   tree/src/util.c (35)
tree/src/lib/core.c (30)   tree/src/lib/core.h (16)
```

Because the harness copies fixtures with fresh modification times for files only, tests use
`-mtime` only together with `-type f`, and `-size` only together with `-type f`.

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-find tree` | FR-05, FR-06, FR-07 |
| 02 | `dp-find tree -name '*.txt'` | FR-08 |
| 03 | `dp-find tree -type d` | FR-10 |
| 04 | `dp-find tree -type f -name '*.c'` | FR-03, FR-08, FR-10 |
| 05 | `dp-find tree -type f -size -2k` | FR-11 |
| 06 | `dp-find tree -mindepth 1 -maxdepth 1` | FR-14 |
| 07 | `dp-find tree -type f '(' -name '*.md' -o -name '*.log' ')'` | FR-03 |
| 08 | `dp-find tree/src -name '*.c' -exec {PYTHON} show.py {} ';' -print` | FR-15, FR-06 |
| 09 | `dp-find nope tree/docs` | FR-17, FR-01 |
| 10 | `dp-find tree -bogus` | FR-02, FR-21 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-05, FR-06 |
| UR-02 | FR-01, FR-05 |
| UR-03 | FR-08, FR-09 |
| UR-04 | FR-10 |
| UR-05 | FR-11 |
| UR-06 | FR-12 |
| UR-07 | FR-13 |
| UR-08 | FR-14 |
| UR-09 | FR-03, FR-06 |
| UR-10 | FR-15, FR-16 |
| UR-11 | FR-05, FR-07, NFR-01, NFR-10 |
| UR-12 | FR-16, FR-17, FR-18, §3.7 |
| UR-13 | FR-02, FR-04, FR-21 |
| UR-14 | FR-22, NFR-02 |
| UR-15 | FR-19, FR-20 |
| UR-16 | NFR-03, NFR-04 |
| UR-17 | §1.5, CLI-CONV |
| UR-18 | NFR-08 |

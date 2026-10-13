# Software Requirements Specification (SRS) — dp-grep

| Field | Value |
| :-- | :-- |
| Document ID | SRS-05 |
| Project | `05-grep-lite` — Pattern Matching Search Engine |
| Product | `dp-grep` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-05) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-grep`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope
`dp-grep` reads text from files, standard input, or directory trees and writes the lines that
match one or more patterns, or a count or list derived from them. Patterns are written in the
*portable ERE subset* defined in section 5, or are literal strings (`-F`). The tool never
modifies files.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR | The bytes `0x0A` and `0x0D` |
| Byte string | A finite sequence of bytes `0x00`–`0xFF` |
| Line | A byte string that contains no LF, obtained from an input as described in FR-04 |
| Pattern | One pattern argument: the value of a `-e` option, or the first operand (FR-01) |
| Pattern bytes | The UTF-8 encoding of a pattern argument (CONV-05) |
| Input | One source of lines: a file, standard input, or a file found during recursive search |
| Label | The name by which an input is identified in output and diagnostics (FR-16, FR-17) |
| Matching line | A line that at least one pattern matches under the active matching options (FR-05) |
| Selected line | A matching line, or with `-v` a line that is not matching |
| ASCII letter | A byte in `0x41`–`0x5A` (`A`–`Z`) or `0x61`–`0x7A` (`a`–`z`) |
| Case counterpart | For an ASCII letter, the same letter in the other case (the byte XOR `0x20`); other bytes have none |
| Word byte | An ASCII letter, an ASCII digit `0`–`9`, or `_` (`0x5F`). Every other byte, including every byte `0x80`–`0xFF`, is a non-word byte |
| Error | A file error (FR-19), a traversal error (FR-17), a usage error, or a pattern error (FR-02) |

### 1.4 References
- URD-05: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- IEEE Std 1003.1 (POSIX), *Base Definitions*, chapter 9 "Regular Expressions" (background
  only; section 5 of this SRS is normative and deliberately smaller)
- RFC 3629, *UTF-8, a transformation format of ISO 10646*

## 2. Overall description

### 2.1 Product perspective
`dp-grep` is a standalone executable. Its interfaces are the command line, the file system
(read-only), standard input, standard output, standard error, and the exit status. It applies
the conventions of CLI-CONV, with the overrides listed in section 2.5.

### 2.2 Product functions
1. Search inputs for lines matched by one or more patterns.
2. Validate patterns against a portable regular-expression grammar before reading any input.
3. Literal (`-F`), case-insensitive (`-i`), inverted (`-v`), whole-line (`-x`), and whole-word
   (`-w`) matching.
4. Output selected lines, optionally with file names and line numbers; or counts (`-c`); or the
   names of files with selected lines (`-l`); or nothing (`-q`).
5. Recursive directory search (`-r`) with deterministic order and `/`-joined paths.
6. Report errors with fixed messages and a three-valued exit status.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language, toolchain, and any regular-expression library are chosen by the
  implementing repository. This specification constrains only observable behavior. Whatever
  engine is used, the set of accepted patterns and the set of lines each pattern matches MUST be
  exactly those defined in section 5 (NFR-02).

### 2.4 Assumptions
- Command-line arguments are UTF-8 text (CONV-05). Input files are arbitrary bytes and need not
  be text or valid UTF-8.
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.

### 2.5 Deliberate differences from CLI-CONV

| Convention | Override in this SRS |
| :-- | :-- |
| CONV-18 (exit status) | Replaced by the table in section 3.7: 0 = a line was selected, 1 = no line was selected, 2 = an error occurred. |
| CONV-16 / CONV-17 (runtime errors exit 1) | File and traversal errors make the exit status **2**, not 1, except under `-q` when a line was selected (FR-20). Processing of the remaining operands continues as CONV-17 requires, except under `-q` after the first selected line (FR-13). |
| CONV-11 (last value wins) | `-e`/`--regexp` accumulates: every occurrence adds one pattern (FR-01). `-H` and `-h` override each other: the one written last wins (FR-15). |
| CONV-04 (byte-for-byte copy) | A selected line is copied byte-for-byte, CR included, but its terminator is always written as a single LF, including for a final line that had no LF in the input (FR-09). |
| CONV-13 / CONV-14 (usage errors) | An invalid or unsupported pattern is **not** a usage error: it has its own diagnostic, is not followed by the `Try ...` line, and exits with status 2 (FR-02). |

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-grep [OPTION]... PATTERN [FILE]...
dp-grep [OPTION]... -e PATTERN [-e PATTERN]... [FILE]...
dp-grep --help
dp-grep --version
```

### 3.2 Options

| Short | Long | Argument | Description |
| :-- | :-- | :-- | :-- |
| `-e` | `--regexp` | PATTERN (required) | Add PATTERN to the pattern list; may be repeated (FR-01) |
| `-F` | `--fixed-strings` | none | Every pattern is a literal byte string (FR-03) |
| `-i` | `--ignore-case` | none | ASCII case-insensitive matching (FR-06) |
| `-v` | `--invert-match` | none | Select the lines that do not match (FR-05) |
| `-x` | `--line-regexp` | none | A pattern must match the entire line (FR-07) |
| `-w` | `--word-regexp` | none | A pattern must match a whole word (FR-08) |
| `-n` | `--line-number` | none | Prefix each output line with its line number (FR-10) |
| `-c` | `--count` | none | Print a count of selected lines per input (FR-11) |
| `-l` | `--files-with-matches` | none | Print the label of each input with a selected line (FR-12) |
| `-q` | `--quiet` | none | Print nothing; stop at the first selected line (FR-13) |
| `-s` | `--no-messages` | none | Suppress file and traversal error diagnostics (FR-19) |
| `-r` | `--recursive` | none | Search directories recursively (FR-17) |
| `-H` | `--with-filename` | none | Always prefix output lines with the label (FR-15) |
| `-h` | `--no-filename` | none | Never prefix output lines with the label (FR-15) |
| — | `--help` | none | Print the help text and exit 0 (FR-21) |
| — | `--version` | none | Print the version line and exit 0 (FR-22) |

Option syntax (bundling, attached values, `--`, interleaving with operands, and scan order)
follows CONV-07 … CONV-12, except for the repetition rules in section 2.5. For example,
`-rc fox tree`, `-r -c fox tree`, and `fox -rc tree` are equivalent, and `-efox`, `-e fox`,
`--regexp=fox`, and `--regexp fox` are equivalent. Flags may be repeated with no further effect.
Note that `-h` means `--no-filename`; help is available only as `--help`.

### 3.3 Operands
- If no `-e` option is given, the first operand is the PATTERN and the remaining operands are
  FILEs. If `-e` is given at least once, every operand is a FILE.
- A FILE operand of exactly `-` means standard input (CONV-10). Other FILE operands are paths,
  echoed in output and diagnostics exactly as given (CONV-19).
- With no FILE operands, `dp-grep` reads standard input, or with `-r` searches the working
  directory (FR-16, FR-17).
- A pattern that begins with `-` is given with `-e` (`-e -x`) or after `--` (`-- -x file`).

### 3.4 Standard input
Read only when it is an input: when there are no FILE operands and `-r` is not given, or for
each FILE operand `-`. Standard input is read in binary mode; no newline translation occurs on
any platform. If `-` appears more than once, the later occurrences find standard input already
at end of file and contribute zero lines.

### 3.5 Standard output
Selected lines (FR-09), counts (FR-11), or labels (FR-12), in the order the inputs are processed
(FR-16, FR-17). Nothing under `-q`. Every line `dp-grep` writes ends with a single LF.

### 3.6 Standard error
Diagnostics only (section 7). Nothing when no error occurs.

### 3.7 Exit status (overrides CONV-18)

| Status | Condition |
| :-- | :-- |
| 0 | At least one line was selected and no error occurred; or `-q` was given and a line was selected (even if an error occurred earlier); or `--help` / `--version` was handled |
| 1 | No line was selected and no error occurred |
| 2 | An error occurred (usage error, pattern error, file or traversal error), unless `-q` was given and a line was selected |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
Processing happens in this order: (1) argument parsing and usage errors (CONV-12); (2) pattern
validation (FR-02); (3) inputs in order (FR-16). Nothing is read and nothing is written to
standard output before step 3.

**FR-01: Pattern sources.**
Each `-e PATTERN` / `--regexp=PATTERN` adds PATTERN to the pattern list, in command-line order;
the option may be repeated any number of times, and an empty PATTERN is allowed. If no `-e` is
given, the first operand is the only pattern. If no `-e` is given and there are no operands, the
tool MUST report the usage error `dp-grep: missing operand` (CONV-13, CONV-14) and exit 2.
*AC:* `dp-grep -x -e cat -e 'dog|bird' words.txt` uses two patterns; `dp-grep` alone exits 2
with `missing operand`. *(UR-12, UR-21)*

**FR-02: Pattern validation.**
Unless `-F` is given, every pattern MUST be validated against the grammar of section 5 before
any input is opened or read. Patterns are validated in pattern-list order; at the first invalid
pattern the tool MUST write exactly one diagnostic,
`dp-grep: invalid pattern '<PATTERN>': <reason>`, where `<PATTERN>` is the pattern exactly as
given (CONV-15) and `<reason>` is determined by section 5.6, and MUST exit with status 2 without
writing to standard output. No `Try ...` line follows, and `-s` does not suppress it.
*AC:* `dp-grep '(a)\1' poem.txt` → stderr `dp-grep: invalid pattern '(a)\1': unsupported escape
\1`, stdout empty, exit 2. `dp-grep -n -e fox -e '(lazy|dog' poem.txt` → `... '(lazy|dog':
unmatched (`, stdout empty, exit 2. *(UR-02, UR-15)*

**FR-03: Fixed strings.**
With `-F`, every pattern is a literal: its pattern bytes, compared byte for byte (subject to
`-i`). No pattern is validated and no character is special. A fixed pattern P matches a line at
every span `[i, i+len(P))` where the line's bytes equal P; the empty fixed pattern matches the
empty span at every position.
*AC:* `dp-grep -F -n 'a.b*' meta.txt` prints only the two lines containing the literal text
`a.b*`, not `axb` or `a.bbb`. *(UR-03)*

**FR-04: Line splitting.**
Each input is divided into lines at every LF byte. The LF is not part of the line. If the input
is non-empty and does not end with LF, the bytes after the last LF form a final line. An empty
input has no lines; an input consisting of one LF has one empty line. All other bytes, including
CR (`0x0D`), NUL (`0x00`), and bytes that are not valid UTF-8, are line data (CONV-04). There is
no binary-file detection: every input is searched as lines of bytes. Lines are numbered from 1
within each input.
*AC:* in `crlf.txt` (`one` CR LF `two` CR LF `three` CR LF), the second line is the four bytes
`two` CR, so `dp-grep -n 'o.$' crlf.txt` selects line 2 and prints `2:two` CR LF. *(UR-01,
UR-17)*

**FR-05: Matching and selection.**
A pattern matches a line as defined in section 5.5 (or FR-03 for `-F`), modified by `-x`
(FR-07) and `-w` (FR-08). A line is *matching* if at least one pattern in the list matches it.
Without `-v`, the matching lines are selected; with `-v`, the lines that are not matching are
selected. Only *whether* a line matches is observable; which part of the line matched is never
output.
*AC:* `dp-grep fox poem.txt` prints lines 1, 4, and 7 of `poem.txt`; `dp-grep -v -n e <
poem.txt` prints `4:a fox, a box, a sock` and `6:` (the empty line). *(UR-01, UR-05)*

**FR-06: Case-insensitive matching.**
With `-i`, matching uses ASCII case folding only: a pattern literal that is an ASCII letter also
matches its case counterpart, and bracket expressions are folded as specified in section 5.5.
With `-F -i`, a pattern byte that is an ASCII letter matches either case of that letter. Bytes
`0x80`–`0xFF` are never folded, so `-i` does not make `é` match `É`. The behavior does not
depend on the locale (CONV-06).
*AC:* `dp-grep -i -n the poem.txt` selects `The`, `the`, and `THE` lines (1, 2, 3, 7).
*(UR-04)*

**FR-07: Whole-line matching.**
With `-x`, a pattern matches a line only if it matches the entire line, that is, if the span
`[0, len(line))` is one of its match spans (section 5.5; for `-F`, if the line equals the pattern).
`-x` takes precedence over `-w`: when both are given, `-w` has no effect.
*AC:* `dp-grep -x -e cat -e 'dog|bird' words.txt` prints `cat`, `dog`, `bird`, and not
`concatenate`, `the cat sat`, or the literal line `dog|bird`. *(UR-11, UR-12)*

**FR-08: Whole-word matching.**
With `-w` (and without `-x`), a pattern matches a line only if it has a match span `[i, j)` such
that `i = 0` or the byte at `i-1` is a non-word byte, **and** `j = len(line)` or the byte at `j` is
a non-word byte. Every span is considered, not only the leftmost or longest one.
*AC:* `dp-grep -w -n -i cat words.txt` prints `1:cat`, `6:the cat sat`, and `7:CAT!`, but not
`concatenate`, `cat_food`, or `bobcat`. *(UR-11)*

**FR-09: Selected-line output.**
In line mode (FR-14), each selected line is written as: the label followed by `:` if file names
are shown (FR-15); then the line number in ASCII decimal followed by `:` if `-n` is given; then
the line's bytes unchanged; then one LF. Lines are written in input order.
*AC:* `dp-grep -r fox tree` prints `tree/a.txt:fox in a`; `dp-grep -i -n the poem.txt` prints
`3:THE END is not near`. *(UR-01, UR-06)*

**FR-10: Line numbers.**
`-n` adds the 1-based line number (FR-04) of each selected line, in plain ASCII decimal with no
padding (CONV-06). `-n` has no effect in count, list, or quiet mode.
*AC:* `dp-grep -n '^[0-9]{3}-[0-9]{4}$' phones.txt` → `1:555-0100` and `5:555-0123`. *(UR-06)*

**FR-11: Count mode.**
With `-c` (count mode, FR-14), no lines are written. After each input has been read completely,
one line is written: the label followed by `:` if file names are shown (FR-15), then the number
of selected lines in that input in ASCII decimal (possibly `0`), then LF. No count is written for
an input that could not be opened or read (FR-19).
*AC:* `dp-grep -c zebra poem.txt words.txt` → `poem.txt:0` and `words.txt:0`, exit 1.
*(UR-07)*

**FR-12: List mode.**
With `-l` (list mode, FR-14), no lines are written. For each input that has at least one selected
line, its label followed by LF is written once; reading that input stops at its first selected
line. Labels are written whether or not file names are shown; `-H` and `-h` have no effect in
list mode. Inputs with no selected line produce no output.
*AC:* `dp-grep -l fox poem.txt missing.txt words.txt` → stdout `poem.txt`, plus the
`missing.txt` diagnostic, exit 2. *(UR-08)*

**FR-13: Quiet mode.**
With `-q` (quiet mode, FR-14), nothing is written to standard output. At the first selected line
in any input, the tool MUST stop immediately and exit with status 0: no further lines or inputs
are read, and inputs that follow are not opened (so they produce no diagnostics). Errors that
occurred before that point have already been diagnosed (unless `-s`), but the exit status is
still 0. If no line is selected, the exit status follows section 3.7.
*AC:* `dp-grep -q fox missing.txt poem.txt` → stdout empty, stderr
`dp-grep: missing.txt: No such file or directory`, exit 0. *(UR-09, UR-14)*

**FR-14: Output mode precedence.**
Exactly one output mode is active: quiet mode if `-q` is given; otherwise list mode if `-l` is
given; otherwise count mode if `-c` is given; otherwise line mode. Options that only affect
another mode are accepted and ignored.
*AC:* `dp-grep -c -l fox poem.txt` behaves as `dp-grep -l fox poem.txt`. *(UR-07, UR-08,
UR-09)*

**FR-15: File name prefixes.**
Whether line-mode and count-mode output lines start with `<label>:` is decided once per run:
if `-H`/`--with-filename` or `-h`/`--no-filename` was given, the one that appears **last** on the
command line decides (`-H` shows, `-h` hides); otherwise names are shown if `-r` is given or
there is more than one FILE operand, and hidden otherwise. A single FILE operand, or none, gives
no prefixes without `-r`.
*AC:* `dp-grep fox poem.txt` prints no prefix; `dp-grep -c zebra poem.txt words.txt` prints
`poem.txt:0`; `dp-grep -s fox missing.txt - < poem.txt` prints
`(standard input):The quick brown fox`. *(UR-18)*

**FR-16: Inputs and labels.**
FILE operands are processed in command-line order. If there are no FILE operands and `-r` is not
given, standard input is the only input. The label of standard input is the exact text
`(standard input)`. The label of a FILE operand is the operand exactly as given (CONV-19). A
FILE operand that names a directory is handled by FR-17 with `-r` and by FR-18 without it; any
other operand (including a special file such as a FIFO) is opened and read as a file.
*AC:* `dp-grep fox < poem.txt` reads standard input and prints three lines without prefixes.
*(UR-13)*

**FR-17: Recursive search.**
With `-r`:
1. A FILE operand that is a directory (following symbolic links when deciding this for an
   operand) is searched recursively; other operands are processed per FR-16.
2. If there are no FILE operands, the working directory is searched recursively, and entry paths
   are displayed relative to it **without** a leading `./` (for example `tree/a.txt`).
   Diagnostics about the working directory itself use the label `.`.
3. Searching a directory D (displayed as label L): its entries are listed, `.` and `..`
   excluded, and visited in ascending byte-wise order of their UTF-8 encoded names (CONV-21).
   For each entry named N, the child label is L joined with N: `L + N` if L ends with `/` (or,
   on Windows only, with `\`), otherwise `L + "/" + N` (CONV-20). The child is then handled
   in place, before the next entry (pre-order): a directory is searched recursively; a regular
   file is searched as an input with the child label; a symbolic link (to anything) is skipped
   without a diagnostic; any other kind of entry (FIFO, socket, device) is skipped without a
   diagnostic.
4. Entry names beginning with `.` are not special: they are listed and searched like any other.
5. If a directory cannot be listed, the traversal error `dp-grep: L: <reason>` (CONV-16, using
   the directory's label) is reported (unless `-s`), the error is recorded, and the traversal
   continues with the next entry of the parent directory.

The operand `.` therefore gives labels such as `./tree/a.txt`, and the operand `tree/` gives
labels such as `tree/a.txt`.
*AC:* `dp-grep -r fox tree` prints matches from `tree/.hidden.txt`, `tree/a/deep.txt`,
`tree/a-b.txt`, `tree/a.txt`, and `tree/b/c/notes.txt`, in exactly that order (the directory
`a` sorts before `a-b.txt`, and its contents are output at that position). *(UR-10, UR-17)*

**FR-18: Directory operand without -r.**
Without `-r`, a FILE operand that is a directory is a file error with reason `Is a directory`:
`dp-grep: <operand>: Is a directory`. This applies on every platform, including Windows, where
the operating system would report access denied.
*AC:* `dp-grep fox tree poem.txt` → stderr `dp-grep: tree: Is a directory`, stdout the three
`poem.txt:` lines, exit 2. *(UR-16, UR-17)*

**FR-19: File errors.**
If an input cannot be opened or read, the tool MUST write `dp-grep: <label>: <reason>`, with the
reason from the CONV-16 table (never operating-system text), record the error, and continue with
the next input (CONV-17). With `-s`/`--no-messages`, file errors (FR-18, FR-19) and traversal
errors (FR-17 step 5) are not written, but they are still recorded and still affect the exit
status. `-s` suppresses no other diagnostic. If an error occurs part way through reading an
input, lines already written stay written and no count or label is written for that input.
*AC:* `dp-grep -s fox missing.txt - < poem.txt` → stderr empty, three `(standard input):`
lines on stdout, exit 2. *(UR-16)*

**FR-20: Exit status.**
The exit status MUST follow section 3.7. In particular, an error makes the status 2 even if
lines were selected, unless `-q` was given and a line was selected (FR-13).
*AC:* `dp-grep -l fox poem.txt missing.txt words.txt` exits 2 although `poem.txt` was listed;
`dp-grep -q fox missing.txt poem.txt` exits 0; `dp-grep -c zebra poem.txt words.txt` exits 1.
*(UR-14)*

**FR-21: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12.
*AC:* `dp-grep --help` matches the user manual exactly. *(UR-19)*

**FR-22: Version.**
`--version` MUST write `dp-grep (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-19)*

**FR-23: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to flags (`--count=1`) MUST be
reported with the CONV-13 messages, followed by the CONV-14 line, and exit 2. Long options MUST
NOT be abbreviated (CONV-08).
*AC:* `dp-grep -Z fox` → `dp-grep: invalid option -- 'Z'`; `dp-grep -e` →
`dp-grep: option requires an argument -- 'e'`; each exits 2. *(UR-21)*

**FR-24: Error atomicity.**
After a usage error or a pattern error, nothing is written to standard output and no input is
read.
*AC:* stdout is empty for `dp-grep '(a)\1' poem.txt` and for `dp-grep -Z fox poem.txt`.
*(UR-15, UR-21)*

## 5. Pattern language: the portable ERE subset

### 5.1 Rationale (informative)
Regular-expression engines disagree. Backtracking engines (as in Perl-compatible libraries) and
automaton engines (RE2-style, which guarantee linear time) accept different syntax: `\d`,
`(?=…)`, lazy `*?`, possessive `*+`, and backreferences exist in some and not in others; `{`
and `]` are literal in some contexts in one engine and errors in another; `\` inside a bracket
expression is an escape in some and a literal in POSIX. Engines also disagree about *which* text
a pattern matches when several matches are possible (leftmost-longest in POSIX, leftmost-first
in backtracking engines).

`dp-grep` avoids every one of these differences:

1. It accepts only a small grammar whose meaning is the same in every mainstream engine, and it
   rejects everything else with a fixed diagnostic. An implementation MUST validate patterns
   itself (section 5.6) and MUST NOT rely on its engine's parser to accept or reject a pattern.
2. It never outputs *what* matched (there is no `-o` or color option), so only *whether* a line
   matches is observable. Whether at least one match exists is the same under leftmost-longest
   and leftmost-first semantics, so the matching-preference difference cannot affect output.
3. It matches bytes, not characters, and folds case only for ASCII letters, so neither Unicode
   tables nor the locale can change the result.

### 5.2 Characters of a pattern
A pattern is processed as its pattern bytes. They are divided into *pattern characters* from
left to right: a byte `0x00`–`0x7F` is one character; a byte sequence that forms one complete,
valid UTF-8 encoded character (RFC 3629: 2 to 4 bytes, no overlong forms, no surrogates, at most
U+10FFFF) is one character; any other byte is one character by itself. Syntax characters are
ASCII. The *metacharacters* are the fourteen characters `^ . [ ] $ ( ) | * + ? { } \`.

### 5.3 Grammar
The grammar uses ABNF notation (RFC 5234). `CHAR` is any pattern character; prose rules restrict
it.

```text
pattern     = branch *( "|" branch )
branch      = *piece                      ; may be empty
piece       = anchor / atom [ quantifier ]
anchor      = "^" / "$"
atom        = "." / bracket / group / escape / literal
group       = "(" pattern ")"             ; may be empty: "()"
escape      = "\" metachar                ; the escaped metacharacter as a literal
literal     = CHAR                        ; any pattern character except
                                          ;   ^ . [ $ ( ) | * + ? { \
                                          ; ("]" and "}" ARE ordinary literals)
quantifier  = "*" / "+" / "?" / interval
interval    = "{" bound "}" / "{" bound ",}" / "{" bound "," bound "}"
bound       = 1*DIGIT                     ; ASCII digits, leading zeros allowed
bracket     = "[" [ "^" ] members "]"     ; structure defined in section 5.4
```

Additional constraints:

- **C1 (bounds).** In an interval, every bound has a value from 0 to 255 inclusive (the number
  of digits is unlimited, so `{007}` is valid), and in `{m,n}`, m ≤ n.
- **C2 (one quantifier).** A piece has at most one quantifier. `a**`, `a+?`, `a*+`, and `a{2}*`
  are invalid. Anchors take no quantifier: `^*` is invalid.
- **C3 (nesting).** Groups nest at most 100 deep: the 101st `(` opened inside 100 open groups is
  invalid.
- **C4 (repetition product).** The *weight* of a quantifier is 1 for `*`, `+`, and `?`;
  `max(m, 1)` for `{m}` and `{m,}`; and `max(n, 1)` for `{m,n}`. The *product* of a quantifier
  is its weight multiplied by the largest product of any quantifier inside the atom it applies
  to (1 if there is none). Every product MUST be at most 1000. Example: `(a{30}){33}` has
  product 990 and is valid; `(a{30}){40}` has product 1200 and is invalid; `(a{30}|b{40}){20}`
  has product 800.

C3 and C4 keep every valid pattern within the compile-size limits of automaton-based engines.

### 5.4 Bracket expressions
After `[`, a `^` makes the expression *negated*. Then *members* are read, left to right, until
a `]` that is not the first member. Each step reads one *element*:

1. If the pattern ends, the pattern is invalid (`unmatched [`).
2. If the next character is `]` and at least one member has been read, the expression ends.
   (So `]` is an ordinary member when it is first: `[]a]` and `[^]a]` contain `]`.)
3. An element is one of:
   - **a class** `[:name:]`: `[` immediately followed by `:`. The class ends at the first
     occurrence of `:]` after the `[:`; if there is none, the pattern is invalid
     (`unmatched [`). The name between them MUST be one of the twelve names in the table below,
     otherwise the pattern is invalid (`invalid character class`).
   - **an unsupported construct**: `[` immediately followed by `.` or `=` (POSIX collating
     symbols and equivalence classes) makes the pattern invalid
     (`unsupported bracket construct`).
   - **a single ASCII character** `0x00`–`0x7F`. Every ASCII character is literal here,
     including `\` (backslash is **not** an escape inside brackets), `[` when not followed by
     `:`, `.`, or `=`, `^` when not first, `-`, `.`, `*`, `$`, `|`, `(`, and `)`.
   - A pattern character that is not ASCII makes the pattern invalid
     (`non-ASCII character in bracket expression`).
4. **Ranges.** If an element is immediately followed by `-`, and the `-` is followed by a
   character other than `]`, the three form a range:
   - if the first element is a class, the pattern is invalid (`invalid range`);
   - if the character after `-` is `[` followed by `:`, `.`, or `=`, the pattern is invalid
     (`invalid range`);
   - otherwise the end element is read as in step 3 (so a non-ASCII end is
     `non-ASCII character in bracket expression`); if the start byte is greater than the end
     byte, the pattern is invalid (`invalid range`). The range contains every byte from start to
     end inclusive.

   A `-` that is first, last (immediately before the closing `]`), or immediately after a range
   is an ordinary member: `[-a]`, `[a-]`, and `[a-c-e]` (`a`–`c`, `-`, `e`) are valid. `[--/]`
   is the range `-`–`/`.

The member set S of the expression is the union of its characters, ranges, and classes. The
classes are defined on ASCII bytes only:

| Name | Bytes |
| :-- | :-- |
| `alpha` | `A`–`Z`, `a`–`z` |
| `digit` | `0`–`9` |
| `alnum` | `A`–`Z`, `a`–`z`, `0`–`9` |
| `upper` | `A`–`Z` |
| `lower` | `a`–`z` |
| `space` | `0x09`–`0x0D`, `0x20` |
| `blank` | `0x09`, `0x20` |
| `punct` | `0x21`–`0x2F`, `0x3A`–`0x40`, `0x5B`–`0x60`, `0x7B`–`0x7E` |
| `print` | `0x20`–`0x7E` |
| `graph` | `0x21`–`0x7E` |
| `cntrl` | `0x00`–`0x1F`, `0x7F` |
| `xdigit` | `0`–`9`, `A`–`F`, `a`–`f` |

### 5.5 Semantics
Matching is defined on a line L whose length is len(L) bytes, with positions 0 … len(L). Each construct
denotes a set of *match spans* `[i, j)` with 0 ≤ i ≤ j ≤ len(L):

| Construct | Match spans |
| :-- | :-- |
| literal or escape, character with bytes s | every `[i, i+len(s))` where L's bytes from i equal s. With `-i`, when s is a single ASCII letter, a byte equal to s or to its case counterpart also matches |
| `.` | every `[i, i+1)`: exactly one byte, of any value (a line never contains LF) |
| bracket, member set S | every `[i, i+1)` where byte L[i] is in S′. Without `-i`, S′ = S. With `-i`, S′ = S plus the case counterpart of every ASCII letter in S. A negated expression uses the complement of S′ in `0x00`–`0xFF`, so it can match bytes `0x80`–`0xFF`. Example: with `-i`, `[^a]` matches neither `a` nor `A` |
| `^` | the span `[0, 0)` only |
| `$` | the span `[len(L), len(L))` only |
| empty branch, `()` | every empty span `[i, i)` |
| concatenation x y | every `[i, k)` such that `[i, j)` is a span of x and `[j, k)` is a span of y |
| alternation x \| y | the union of the spans of x and y |
| group `( x )` | the spans of x |
| x quantified with minimum m and maximum n | the union, over every count c with m ≤ c ≤ n, of c-fold concatenations of x (0-fold is the empty span at every position). `*` is {0,∞}, `+` is {1,∞}, `?` is {0,1}, `{m}` is {m,m}, `{m,}` is {m,∞} |

A pattern **matches** line L if its set of spans is not empty. With `-x` it matches only if
`[0, len(L))` is one of its spans; with `-w`, FR-08 applies. Consequences that every
implementation must reproduce:

- A non-ASCII literal character is matched as a unit and a quantifier repeats the whole
  character: `ë+` matches `ëë`, not `ë` followed by a stray byte.
- `.` matches one *byte*: `^.{3}$` does not match the three-character, four-byte line `Zoë`.
- `$` matches only at the very end of the line, so `two$` does not match the line `two` CR
  taken from a CRLF file; `two.$` does.
- `^` and `$` may appear anywhere: `a^b` is valid and matches nothing; `(^|,)x` is valid.
- The empty pattern, `()`, and `a|` match every line.
- LF is an ordinary pattern character (it is not a metacharacter). Because no line contains LF,
  a piece consisting of LF never matches; a pattern containing LF is **not** split into several
  patterns.

### 5.6 Validation procedure and error reasons
A pattern is validated by one left-to-right scan; the **first** condition met determines the
reason. In a branch, the "previous piece" is absent at the start of the pattern, right after
`(`, and right after `|`.

| # | When the scan reaches … | Condition | `<reason>` |
| :-- | :-- | :-- | :-- |
| 1 | `\` | It is the last character of the pattern | `trailing backslash` |
| 2 | `\` | The next character C is not a metacharacter | `unsupported escape \C` (C written as its pattern bytes) |
| 3 | `(` | 100 groups are already open | `nesting too deep` |
| 4 | the end of the pattern | At least one group is open | `unmatched (` |
| 5 | `)` | No group is open | `unmatched )` |
| 6 | `*` `+` `?` `{` | The previous piece is absent or is an anchor | `nothing to repeat` |
| 7 | `*` `+` `?` `{` | The previous piece already has a quantifier | `multiple repeat` |
| 8 | `{` | The text from `{` does not have the form `{` DIGITS `}`, `{` DIGITS `,}`, or `{` DIGITS `,` DIGITS `}` (DIGITS = one or more ASCII digits), or violates C1 | `invalid interval` |
| 9 | a quantifier that has just been read | Its product exceeds 1000 (C4) | `repetition too large` |
| 10 | inside `[` … `]` | The rules of section 5.4 | `unmatched [`, `invalid character class`, `unsupported bracket construct`, `non-ASCII character in bracket expression`, or `invalid range` |

Rows 6 and 7 are checked before row 8, so `a*{x` is `multiple repeat` and `{2}` at the start of
a pattern is `nothing to repeat`. The constructs that users most often expect from other tools
are therefore rejected as follows:

| Construct | Example | `<reason>` |
| :-- | :-- | :-- |
| Backreference | `(a)\1` | `unsupported escape \1` |
| Shorthand classes, word boundaries | `\d`, `\w`, `\s`, `\b`, `\<` | `unsupported escape \d` (etc.) |
| Escaped ordinary character | `\-`, `\/`, `\n`, `\t` | `unsupported escape \-` (etc.) |
| Lookaround, inline flags, non-capturing group | `(?=x)`, `(?i)x`, `(?:x)` | `nothing to repeat` |
| Lazy or possessive quantifier | `a+?`, `a*+` | `multiple repeat` |
| Interval with omitted lower bound | `a{,3}` | `invalid interval` |
| Literal brace without escape | `f{oo}` | `invalid interval` |
| Collating element, equivalence class | `[[.a.]]`, `[[=a=]]` | `unsupported bracket construct` |

### 5.7 Implementation guidance (informative)
An implementation may build its own matcher, or translate a validated pattern into the syntax of
its platform's engine. A translation must quote every literal so the target engine sees it as a
literal (for example, `]` and `}` outside brackets, and `\` inside brackets), should express each
bracket expression as an explicit list of bytes after applying `-i` folding, should map `^` and
`$` to absolute start/end-of-subject assertions (some engines let `$` also match before a final
LF), and must make `.` match exactly one byte. Engines that match Unicode code points rather
than bytes can be used by mapping each byte 0–255 to the code point of the same value, both in
the line and in the translated pattern. `-x` can be implemented as a full match of the pattern,
and `-w` as a search for `(^|N)(P)(N|$)`, where N is the bracket expression of the non-word
bytes and P the translated pattern.

## 6. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output MUST be byte-identical on Linux, macOS, and Windows, and every line the tool writes MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Portability (regular expressions) | The set of valid patterns and the lines each one matches MUST be exactly those of section 5, independent of the engine, library version, locale, or platform. Patterns MUST be validated by the implementation's own code (section 5.6) before any engine sees them. | Black-box tests; unit tests of the validator against every row of the 5.6 tables |
| NFR-03 | Portability (paths) | Constructed paths MUST use `/` (CONV-20); directory entries MUST be visited in byte-wise order (CONV-21); user-supplied paths MUST be echoed unchanged (CONV-19). Output MUST NOT depend on the order in which the operating system returns directory entries. | CI black-box tests on 3 OSes; code review |
| NFR-04 | Portability (input) | Standard input and files MUST be read in binary mode; CR bytes MUST reach the matcher unchanged on every platform. | Black-box test (CRLF fixture) |
| NFR-05 | Performance | Start-up and exit MUST take under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware. Searching a 10 MiB file of 80-byte lines with a literal pattern MUST complete in under 1 s native (3 s interpreted). | Measurement |
| NFR-06 | Memory | Inputs MUST be processed as a stream: peak memory MUST NOT grow with the size of an input, only with the length of its longest line, and MUST stay under 64 MiB for inputs whose lines are at most 1 MiB long. | Measurement; code review |
| NFR-07 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list, pattern, or input bytes, including invalid UTF-8 and NUL bytes (CONV-24). It MUST handle directory trees nested at least 64 levels deep. | Unit + black-box tests |
| NFR-08 | Maintainability | Argument parsing, pattern validation, pattern matching, input traversal, and output formatting MUST be separate units (Principles 13, 18). | Design review |
| NFR-09 | Testability | The pattern validator and the line matcher MUST be pure functions of their inputs, covered by unit tests that include every error reason of section 5.6. | Code review |
| NFR-10 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-11 | Security | The tool MUST only read: the files and directories named or found by traversal, and standard input. It MUST NOT write or modify files, follow symbolic links found during traversal, read environment variables, or run subprocesses. | Inspection |
| NFR-12 | Efficiency (matching) | The matcher SHOULD run in time linear in the line length for a fixed pattern (as automaton-based engines guarantee). Implementations that use a backtracking engine remain conformant, but SHOULD document that patterns such as `(a+)+b` can be slow on long lines. | Design review |

## 7. Diagnostics (complete list)

Every diagnostic is one line on standard error, ending in LF.

### 7.1 Usage errors
Each is followed by `Try 'dp-grep --help' for more information.` and exit status 2. Nothing is
read and nothing is written to standard output.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-grep: invalid option -- 'x'` |
| Unknown long option token `T` | `dp-grep: unrecognized option 'T'` |
| `-e` without an argument | `dp-grep: option requires an argument -- 'e'` |
| `--regexp` without an argument | `dp-grep: option '--regexp' requires an argument` |
| A flag given `=value`, for example `--count=1` | `dp-grep: option '--count' doesn't allow an argument` |
| No `-e` and no operand | `dp-grep: missing operand` |

### 7.2 Pattern errors
Exit status 2, no `Try ...` line, not suppressed by `-s`, nothing written to standard output.

| Trigger | Exact line |
| :-- | :-- |
| The first invalid pattern P, with reason R from section 5.6 | `dp-grep: invalid pattern 'P': R` |

The complete set of reasons R is: `trailing backslash`, `unsupported escape \C`,
`nesting too deep`, `unmatched (`, `unmatched )`, `nothing to repeat`, `multiple repeat`,
`invalid interval`, `repetition too large`, `unmatched [`, `invalid character class`,
`unsupported bracket construct`, `non-ASCII character in bracket expression`, `invalid range`.

### 7.3 File and traversal errors
The error is recorded (exit status 2 unless FR-13 applies) and processing continues. With `-s`
the line is not written.

| Trigger | Exact line |
| :-- | :-- |
| An input (operand or traversal entry) labelled L does not exist, cannot be opened, or cannot be read | `dp-grep: L: <reason>`, with `<reason>` from the CONV-16 table |
| A directory operand L without `-r` | `dp-grep: L: Is a directory` |
| A directory labelled L cannot be listed during `-r` | `dp-grep: L: <reason>`, with `<reason>` from the CONV-16 table |
| Reading standard input fails | `dp-grep: (standard input): Input/output error` |

## 8. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-05, FR-07, FR-09 … FR-12, FR-15 … FR-17, FR-19, FR-20, FR-24, section 5 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-02, FR-04, FR-06, FR-08, FR-12, FR-13, FR-15 … FR-20, FR-24, section 5 |
| Unit test (written by the implementer) | FR-02 … FR-08, section 5 (every grammar rule and error reason), NFR-09 |
| Inspection / review | NFR-05, NFR-06, NFR-08, NFR-11, NFR-12 |

Fixture files are shared by both suites and live in `tests/fixtures/`.

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-grep fox poem.txt` | FR-05, FR-09, FR-15 (single file, no prefix) |
| 02 | `dp-grep -i -n the poem.txt` | FR-06, FR-10 |
| 03 | `dp-grep -v -n e < poem.txt` | FR-05 (`-v`), FR-04 (empty line), FR-16 (standard input) |
| 04 | `dp-grep -c zebra poem.txt words.txt` | FR-11, FR-15, FR-20 (exit 1) |
| 05 | `dp-grep -F -n 'a.b*' meta.txt` | FR-03 |
| 06 | `dp-grep -x -e cat -e 'dog\|bird' words.txt` | FR-01, FR-07, section 5 (alternation) |
| 07 | `dp-grep -n '^[0-9]{3}-[0-9]{4}$' phones.txt` | Section 5 (anchors, brackets, intervals) |
| 08 | `dp-grep -r fox tree` | FR-17 (order, pre-order, `/` joining, dot files) |
| 09 | `dp-grep '(a)\1' poem.txt` | FR-02, FR-24, section 5.6 (backreference) |
| 10 | `dp-grep -l fox poem.txt missing.txt words.txt` | FR-12, FR-19, FR-20 |

## 9. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-04, FR-05, FR-09 |
| UR-02 | FR-02, section 5, NFR-02 |
| UR-03 | FR-03 |
| UR-04 | FR-06 |
| UR-05 | FR-05 |
| UR-06 | FR-09, FR-10 |
| UR-07 | FR-11, FR-14 |
| UR-08 | FR-12, FR-14 |
| UR-09 | FR-13, FR-14 |
| UR-10 | FR-17 |
| UR-11 | FR-07, FR-08 |
| UR-12 | FR-01, FR-07 |
| UR-13 | FR-16, §3.4 |
| UR-14 | FR-13, FR-20, §3.7 |
| UR-15 | FR-02, FR-24, section 5.6 |
| UR-16 | FR-18, FR-19 |
| UR-17 | FR-04, FR-17, FR-18, NFR-01, NFR-03, NFR-04, CONV-03, CONV-20, CONV-21 |
| UR-18 | FR-15 |
| UR-19 | FR-21, FR-22 |
| UR-20 | NFR-05, NFR-06, NFR-12 |
| UR-21 | FR-01, FR-23, FR-24, CLI-CONV |
| UR-22 | NFR-10 |

# Software Requirements Specification (SRS) — dp-diff

| Field | Value |
| :-- | :-- |
| Document ID | SRS-07 |
| Project | `07-diff-lite` — Line-by-Line File Comparison |
| Product | `dp-diff` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-07) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-diff`. It is complete and precise
enough that independent implementations in any programming language, using any comparison
algorithm, produce **byte-identical** output for every invocation. It is the authoritative
source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-diff` compares two inputs line by line and writes the differences in *normal* format
(default) or *unified* format, or only reports whether they differ. One input may be standard
input. The tool never modifies its inputs.

### 1.3 Definitions

| Term | Definition |
| :-- | :-- |
| LF, CR | The bytes `0x0A` and `0x0D` |
| Input | The complete byte content of an operand: a file, or standard input for `-` |
| Line | See FR-03. A line includes its terminating LF, if it has one |
| Unterminated line | The last line of an input that does not end in LF |
| A, B | The line sequences of FILE1 and FILE2: A = a₀ … a₍N−1₎, B = b₀ … b₍M−1₎ |
| N, M | The number of lines in A and in B |
| Edit script | A sequence of operations K (keep aᵢ and bⱼ), D (delete aᵢ), I (insert bⱼ) that consumes A and B from front to back |
| Canonical edit script | The single edit script defined in FR-05 |
| D (distance) | The number of D and I operations in the canonical edit script |
| Change | A maximal run of consecutive D and I operations in the canonical edit script (FR-06) |
| NUM | The unified-format context size (FR-12) |
| Half-open range [lo, hi) | The 0-based line indices lo, lo+1, …, hi−1; it is empty when lo = hi |

### 1.4 References
- URD-07: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- E. W. Myers, "An O(ND) Difference Algorithm and Its Variations", *Algorithmica* 1 (1986)
  (informative; see FR-07)
- GNU diffutils manual, "Normal" and "Unified Format" sections (informative; the formats here
  follow GNU conventions except where section 9 lists a deviation)

## 2. Overall description

### 2.1 Product perspective
`dp-diff` is a standalone executable. Its interfaces are the command line, the two inputs,
standard output, standard error, and the exit status. It is project 07 of the curriculum and
builds on the file-handling conventions of projects 02–06.

### 2.2 Product functions
1. Read two inputs (files or standard input) completely.
2. Split each into lines, optionally removing a CR before each LF.
3. Compute the canonical edit script between the two line sequences.
4. Write it in normal format, in unified format with NUM lines of context, or as a one-line
   "differ" message.
5. Report the result through the exit status: same, different, or trouble.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language, toolchain, and comparison algorithm are chosen by the
  implementing repository. This specification constrains only observable behavior.

### 2.4 Assumptions
- Inputs are text, but the tool treats them as bytes: any byte value, including NUL and
  invalid UTF-8, is allowed and is compared and copied unchanged.
- Each input fits in memory (NFR-04).

### 2.5 Why one canonical edit script (rationale)
For most pairs of inputs there are **many** shortest edit scripts. For example, with
A = `ping ping pong` and B = `ping pong pong`, deleting the second `ping` and appending a `pong`
is exactly as short as changing the second line from `ping` to `pong`. Different algorithms
(dynamic programming, Myers, Hunt–Szymanski, patience diff) and even different correct
implementations of the *same* algorithm pick different ones. GNU `diff`, for instance, prints
`2c2` for this pair, while this specification requires `2d1` … `3a3` (see FR-05, example).

A byte-exact acceptance test can only work if the expected output is unique. This SRS therefore
defines one canonical edit script mathematically (FR-05) and requires every implementation to
produce exactly that script, by whatever algorithm the implementer chooses (FR-07). The same
idea — define the result, not the procedure — is what makes the output reproducible across
operating systems and implementations (UR-08, UR-12).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-diff [-q | --brief] [-u | -U NUM | --unified[=NUM]] [--strip-trailing-cr] FILE1 FILE2
dp-diff --help
dp-diff --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-q` | `--brief` | none | off | Only report whether the inputs differ (FR-14) |
| `-u` | — | none | — | Unified format with 3 lines of context; exactly equivalent to `-U 3` |
| `-U` | `--unified` | NUM: required for `-U`; **optional** for `--unified` | 3 | Unified format with NUM lines of context (FR-12) |
| — | `--strip-trailing-cr` | none | off | Remove a CR that immediately precedes an LF in the inputs (FR-04) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax follows CONV-07 … CONV-12, with one extension: `--unified` takes an **optional**
argument, which can only be attached with `=` (`--unified=5`). A bare `--unified` never consumes
the next token; it means `--unified=3`. So `dp-diff a --unified b` compares `a` and `b` in
unified format, and `dp-diff --unified 5 a b` treats `5` as an operand (and reports
`extra operand 'b'`). `-U` takes a required argument per CONV-07 (`-U5`, `-U 5`, `-qU5`).

`-u`, `-U NUM`, and `--unified[=NUM]` set the same setting; per CONV-11 the last occurrence
wins (`-U 5 -u` means NUM = 3), and only the winning value is validated (FR-12).

### 3.3 Operands
Exactly two operands, FILE1 and FILE2, are required (FR-15). Either one (but not both) may be
`-`, meaning standard input. Operands are paths to regular files; directories are not
supported (FR-02).

### 3.4 Standard input
Read only when an operand is `-`. It is then read completely, in binary mode, until end of
file (CONV-26). Empty standard input is an input with zero lines.

### 3.5 Standard output
Normal-format output (FR-08), unified-format output (FR-09 … FR-11), or the brief message
(FR-14). Nothing when the inputs are the same, and nothing on any error. On Windows, standard
output MUST be in binary mode (CONV-03); bytes copied from the inputs, including CR, are
written unchanged (CONV-04).

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success, whether or not the inputs differ.

### 3.7 Exit status (overrides CONV-18)

| Status | Condition |
| :-- | :-- |
| 0 | The inputs are the same (FR-03), or `--help` / `--version` was handled |
| 1 | The inputs differ |
| 2 | Trouble: a usage error (CONV-13/14, FR-15), or an operand could not be read (FR-02) |

Unlike CONV-18 and CONV-16, a file error yields status **2**, not 1, because status 1 means
"differences found". This matches the long-standing convention of POSIX `diff` and lets
scripts tell "different" from "broken".

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.

### 4.1 Input

**FR-01: Reading the inputs.**
After successful option parsing, the tool MUST read FILE1 completely and then FILE2 completely,
as bytes. An operand `-` reads standard input. Both inputs are read before any output is
produced.
*AC:* `dp-diff -u - new.txt < old.txt` compares the content of `old.txt` with `new.txt`.
*(UR-05)*

**FR-02: Unreadable operands and directories.**
If an operand cannot be opened or read, the tool MUST write the CONV-16 diagnostic
`dp-diff: <operand>: <reason>`, with the operand exactly as given (CONV-19) and the reason from
the CONV-16 table. An operand that names a directory MUST be reported with the reason
`Is a directory`: directory comparison is not supported. Following CONV-17, the tool MUST still
attempt the other operand and report its failure too, FILE1 before FILE2. If either operand
failed, the tool MUST write nothing to standard output and MUST exit with status **2**. A read
failure on standard input is reported with the operand `-`.
*AC:* `dp-diff fruits.txt nosuch.txt` → stderr `dp-diff: nosuch.txt: No such file or
directory`, stdout empty, exit 2. `dp-diff dir nosuch.txt` (where `dir` is a directory) → two
diagnostic lines, `dir` first, exit 2. *(UR-09)*

**FR-03: Line model and equality.**
Each input is split into lines as follows: a line is a maximal sequence of bytes that ends with
(and includes) an LF byte; if the input does not end with LF, the bytes after the last LF form
one final *unterminated line*. An empty input has zero lines; an input consisting of a single
LF has one line (the line `\n`). No byte other than LF terminates a line; in particular CR is
ordinary data (CONV-04).
Two lines are **equal** if and only if they are identical byte sequences, *including* the
terminating LF. Consequently `x` + LF and the unterminated `x` are different lines, and
`x` + CR + LF differs from `x` + LF unless FR-04 applies.
The inputs are **the same** when A and B have the same length and are equal line by line
(equivalently, after FR-04, the two byte strings are identical).
*AC:* `poem.txt` and `poem-no-eol.txt`, which differ only in the final LF, are reported as
different (FR-10, test 07). *(UR-02, UR-07)*

**FR-04: `--strip-trailing-cr`.**
With `--strip-trailing-cr`, before splitting into lines, every CR byte that is immediately
followed by an LF byte MUST be removed from each input. No other CR is removed: a CR at the very
end of an input (not followed by LF) is kept, and in CR CR LF only the second CR is removed.
The stripped content is what is compared *and* what is written in normal and unified output.
Without this option, CR bytes are compared and written unchanged.
*AC:* `dp-diff --strip-trailing-cr crlf.txt lf.txt`, where the files differ only in CRLF versus
LF line endings → no output, exit 0. Without the option, every line differs and the output
contains the CR bytes of `crlf.txt`. *(UR-06)*

### 4.2 The canonical edit script

**FR-05: Definition.**
Let A = a₀ … a₍N−1₎ and B = b₀ … b₍M−1₎ be the line sequences (FR-03, FR-04). Define the
table L for 0 ≤ i ≤ N, 0 ≤ j ≤ M, where L[i][j] is the length of a longest common subsequence
of the suffixes aᵢ … a₍N−1₎ and bⱼ … b₍M−1₎:

```text
L[i][j] = 0                              if i = N or j = M
L[i][j] = L[i+1][j+1] + 1                if i < N, j < M, and a[i] = b[j]
L[i][j] = max(L[i+1][j], L[i][j+1])      if i < N, j < M, and a[i] ≠ b[j]
```

The **canonical edit script** is the sequence of operations produced by this walk, starting
at i = 0, j = 0:

```text
while i < N and j < M:
    if a[i] = b[j]:                 emit K (keep a[i] and b[j]);  i ← i+1; j ← j+1
    else if L[i+1][j] ≥ L[i][j+1]:  emit D (delete a[i]);         i ← i+1
    else:                           emit I (insert b[j]);         j ← j+1
emit D for each remaining a[i] (i < N), in order
emit I for each remaining b[j] (j < M), in order
```

In words: equal heads are always kept; otherwise a deletion is preferred whenever it still
allows a longest common subsequence, and an insertion is made only when deleting would lose
one. The script is a shortest edit script: its number of K operations equals L[0][0], and its
distance is D = N + M − 2·L[0][0].
*AC:* every normal-format and unified-format test output corresponds to this script.
*(UR-08, UR-12)*

*Worked example (informative).* A = `ping`,`ping`,`pong`; B = `ping`,`pong`,`pong`
(fixtures `pings.txt`, `pongs.txt`, test 06):

| L | j=0 | j=1 | j=2 | j=3 |
| :-- | :-- | :-- | :-- | :-- |
| i=0 | 2 | 1 | 1 | 0 |
| i=1 | 2 | 1 | 1 | 0 |
| i=2 | 1 | 1 | 1 | 0 |
| i=3 | 0 | 0 | 0 | 0 |

The walk: (0,0) `ping`=`ping` → K. (1,1) `ping`≠`pong`, L[2][1] = 1 ≥ L[1][2] = 1 → D.
(2,1) `pong`=`pong` → K. Now i = N, so the remaining b₂ is inserted → I. Script: K D K I, which
prints as `2d1` / `< ping` / `3a3` / `> pong`. The equally short script K D I K (printed by GNU
`diff` as `2c2`) is *not* canonical and is a conformance failure.

**FR-06: Changes.**
A **change** is a maximal run of consecutive D and I operations in the canonical edit script
(that is, a run bounded by K operations or by the ends of the script). Each change is described
by four 0-based indices (i1, i2, j1, j2): it deletes the lines of A in [i1, i2) and inserts the
lines of B in [j1, j2), where i1 and j1 are the numbers of lines of A and B consumed by the
operations before the change. Within a change, the order in which D and I operations
interleave is irrelevant to the output: every format prints all deleted lines (in order)
before all inserted lines. Changes are numbered in script order; consecutive changes are
separated by at least one K, and the number of K operations between a change C and the next
change C′ is C′.i1 − C.i2 (which equals C′.j1 − C.j2).

**FR-07: Freedom of algorithm (conformance rule).**
An implementation MAY compute the canonical edit script with any algorithm, such as the full
table of FR-05, a space-optimized variant, or Myers' O((N+M)·D) algorithm, provided the
resulting script is **identical** to the FR-05 script for every pair of inputs. Producing a
different shortest edit script is a conformance failure even though it is a "correct diff".
The following notes are informative:

1. *Common-prefix trimming is safe.* While a₀ = b₀ the walk emits K, and L of the remaining
   suffixes does not depend on the removed prefix, so removing a common prefix and emitting K
   for it gives the identical script.
2. *Common-suffix trimming is NOT safe in general.* For A = `x` and B = `x`,`x` the canonical
   script is K I (normal format `1a2`). Removing the common last line first leaves an empty
   A and B = `x`, whose script is I; appending K for the removed line gives I K (`0a1`),
   which is wrong. Use suffix trimming only with a proof that it cannot change the result.
3. *Heuristics that give up minimality* (GNU's "speed-large-files" style cut-offs) are not
   allowed: the script must be the canonical one for every input size.
4. *An O((N+M)·D) method.* Let E(i, j) = (N − i) + (M − j) − 2·L[i][j], the edit distance of
   the suffixes. When aᵢ ≠ bⱼ, the rule "L[i+1][j] ≥ L[i][j+1]" is equivalent to
   E(i+1, j) = E(i, j) − 1. Running Myers' greedy algorithm *backward* from (N, M), and keeping
   the furthest-reaching point of every diagonal for every distance d, answers "is
   E(i, j) ≤ d?" in constant time, because E is monotone along each diagonal. A forward walk
   that keeps track of the current E then reproduces the canonical script in O((N+M)·D) time
   and O(N + M + D²) memory.

### 4.3 Output

**FR-08: Normal format.**
When neither `--brief` nor a unified option is given and the inputs differ, the tool MUST write,
for each change (i1, i2, j1, j2) in order:

1. A command line, built from 1-based ranges. RANGE(lo, hi) for a non-empty half-open range is
   `lo+1` when hi − lo = 1, and `lo+1,hi` otherwise (both numbers in plain decimal):
   - only deletions (j1 = j2): RANGE(i1, i2) + `d` + j1, e.g. `3d2`;
   - only insertions (i1 = i2): i1 + `a` + RANGE(j1, j2), e.g. `1a2,3`;
   - both: RANGE(i1, i2) + `c` + RANGE(j1, j2), e.g. `2c2`.

   The bare number after `d` (or before `a`) is the number of lines of the other input that
   precede the change; it is `0` when the change is at the very beginning.
2. For each deleted line aᵢ (i1 ≤ i < i2): `< ` followed by the line (FR-10).
3. If the change has both deletions and insertions: the line `---`.
4. For each inserted line bⱼ (j1 ≤ j < j2): `> ` followed by the line (FR-10).

Every line the tool generates ends in LF.
*AC:* test 02 → `2c2`, `< banana`, `---`, `> blueberry`; test 03 → `1a2,3`, `3d4`, `6d6`
commands. *(UR-02)*

**FR-09: Unified format — file header.**
When a unified option is given (and `--brief` is not) and the inputs differ, the output MUST
begin with exactly two lines:

```text
--- <FILE1>
+++ <FILE2>
```

where `<FILE1>` and `<FILE2>` are the operands exactly as given (CONV-05, CONV-19); an operand
`-` appears as `-`. Unlike GNU `diff`, **no tab and no modification timestamp** follow the
names (section 9).
*AC:* test 04 begins `--- long-old.txt` / `+++ long-new.txt`; hidden stdin test begins
`--- -`. *(UR-03, UR-05, UR-08)*

**FR-10: Line output and the no-newline marker.**
Whenever an input line is written (after a `< `, `> `, ` `, `-`, or `+` prefix), its bytes are
written unchanged. If the line ends in LF, nothing more is written. If it is an unterminated
line, the tool MUST write the line's bytes, then an LF, then the line
`\ No newline at end of file` + LF (the first character is a backslash). This applies in normal
format and in unified format, to deleted, inserted, and context lines alike.
*AC:* test 07 ends with `+sugar is sweet`, LF, `\ No newline at end of file`, LF. *(UR-07)*

**FR-11: Unified format — hunks.**
Let C₁ … Cₖ be the changes (FR-06) and NUM the context size (FR-12).

1. *Grouping.* Changes are grouped into hunks in order: change Cₜ₊₁ joins the hunk of Cₜ when
   Cₜ₊₁.i1 − Cₜ.i2 ≤ 2·NUM (the kept lines between them would otherwise be shown twice or
   adjoin); otherwise it starts a new hunk. With NUM = 0 every change is its own hunk.
   Implementations MUST evaluate 2·NUM without integer overflow.
2. *Extent.* For a hunk whose first change is F and last change is G, let
   lead = min(NUM, F.i1) and trail = min(NUM, N − G.i2). The hunk covers [F.i1 − lead,
   G.i2 + trail) of A and [F.j1 − lead, G.j2 + trail) of B.
3. *Header.* The hunk header is `@@ -` + R(A-range) + ` +` + R(B-range) + ` @@`, where for a
   half-open range [lo, hi) with count = hi − lo:
   - count = 0: `lo,0` (the number is the line *before* the empty range; `0,0` at the start);
   - count = 1: `lo+1` (the `,1` is omitted);
   - count ≥ 2: `lo+1,count`.
4. *Body.* For each change in the hunk, in order: the kept lines of A from the end of the
   previous change (or from the hunk start) up to i1, each prefixed by one space; then the
   deleted lines A[i1, i2), each prefixed by `-`; then the inserted lines B[j1, j2), each
   prefixed by `+`. After the last change: the kept lines of A up to the hunk end, prefixed by
   one space. Context lines are taken from A (they are equal to the corresponding lines of B).
   Each line is written per FR-10.

Hunks are written in order, directly after the file header, with nothing between them.
*AC:* test 04 (`-u`) → one merged hunk `@@ -1,12 +1,12 @@`; test 05 (`-U 1`) on the same
files → two hunks `@@ -1,3 +1,3 @@` and `@@ -8,3 +8,3 @@`; an empty FILE1 against a two-line
FILE2 → `@@ -0,0 +1,2 @@`. *(UR-03)*

**FR-12: Context size.**
`-u` and a bare `--unified` set NUM = 3. `-U NUM` and `--unified=NUM` set NUM to the given
value, which MUST consist only of ASCII digits `0`–`9` (leading zeros allowed) with a value
from 0 to 2147483647 inclusive. Any other value (empty, signed, non-digit, or too large) MUST
be reported as `dp-diff: invalid argument '<NUM>' for '<option>'`, where `<option>` is `-U` or
`--unified` as written, and exit 2 (CONV-13). The last of these options wins (CONV-11), and
only the winning value is validated. The value is validated even when `--brief` is also given.
*AC:* `--unified=x` → `dp-diff: invalid argument 'x' for '--unified'`, exit 2;
`dp-diff old.txt --unified new.txt` → unified output with 3 lines of context. *(UR-03, UR-11)*

**FR-13: Inputs that are the same.**
If the inputs are the same (FR-03, after FR-04), the tool MUST write nothing to standard output
and exit 0, in every output mode.
*AC:* test 01 and test 08 → stdout empty, exit 0. *(UR-01)*

**FR-14: Brief mode.**
With `-q` / `--brief`, when the inputs differ the tool MUST write exactly
`Files <FILE1> and <FILE2> differ` + LF to standard output (operands as given) and exit 1,
writing no other output. `--brief` takes precedence over the unified options.
*AC:* test 09 → `Files fruits.txt and fruits-changed.txt differ`, exit 1. *(UR-04)*

**FR-15: Operand count.**
With fewer than two operands the tool MUST report `dp-diff: missing operand`; with more than
two, `dp-diff: extra operand '<third operand>'`. If both operands are `-`, it MUST report
`dp-diff: '-' may be given as only one operand`. Each is a usage error: it is followed by
`Try 'dp-diff --help' for more information.` and exit 2, and no input is read (CONV-12, CONV-14).
Tokens after `--` are operands, so `dp-diff -- -q b` compares a file named `-q` with `b`.
*AC:* `dp-diff old.txt` → missing operand, exit 2; `dp-diff old.txt new.txt extra.txt` →
`extra operand 'extra.txt'`, exit 2. *(UR-09)*

**FR-16: Help and version.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0; `--version` MUST write `dp-diff (dialectic-playground) 1.0.0` + LF and exit
0. Both follow the scan order of CONV-12.
*AC:* exact match. *(UR-10)*

**FR-17: Other usage errors.**
Unknown options, a missing argument for `-U`, and an argument given with `=` to `--brief`,
`--strip-trailing-cr`, `--help`, or `--version` MUST be reported with the CONV-13 messages and
exit 2. Long options MUST NOT be abbreviated (`--unif` is unrecognized).
*AC:* `dp-diff -x a b` → `dp-diff: invalid option -- 'x'`, exit 2. *(UR-09, UR-11)*

**FR-18: Error atomicity.**
On any usage error or unreadable operand, standard output MUST remain empty.
*AC:* stdout is empty in every exit-2 test. *(UR-09)*

**FR-19: No binary detection.**
The tool MUST NOT treat inputs differently because they contain NUL bytes or invalid UTF-8;
such bytes are compared and copied like any others. There is no "Binary files differ" message.
*AC:* inspection; output bytes are copies of input bytes. *(UR-08)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability / determinism | Output MUST be byte-identical on Linux, macOS, and Windows and across implementations: generated lines end in LF only, standard input and output are binary, headers contain no timestamps, and nothing depends on locale, time zone, or the file system (CONV-03, CONV-06). | CI black-box tests on 3 OSes |
| NFR-02 | Newline handling | CR is data unless `--strip-trailing-cr` is given (FR-04); the tool MUST NOT translate line endings on input or output on any platform. | Tests 08, hidden 01 |
| NFR-03 | Performance (Must) | For inputs with N·M ≤ 4,000,000 (for example 2,000 lines each, any distance), run time MUST be under 1 s for a natively compiled build (3 s for an interpreted runtime) on CI hardware, with peak memory under 128 MiB. A full L table meets this. | Measurement |
| NFR-04 | Input size | Implementations MUST accept inputs of at least 64 MiB each and lines of any length (no line-length limit). Inputs are held in memory; memory use MUST be O(size of inputs) plus the algorithm's working storage. | Measurement |
| NFR-05 | Scalability (Should) | For inputs of up to 100,000 lines each whose canonical distance D is at most 1,000, run time SHOULD be under 2 s (native) and working memory SHOULD be O(N + M + D²), for example by the method in FR-07 note 4. An O(N·M) table does not meet this. | Measurement |
| NFR-06 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any input or argument list (CONV-24); EPIPE terminates it quietly (CONV-25). | Unit + black-box tests |
| NFR-07 | Maintainability | Argument parsing, input reading and line splitting, edit-script computation, and each output format MUST be separate units. The edit-script computation MUST be a pure function of two line sequences. | Design review |
| NFR-08 | Testability | Implementers MUST unit-test the edit-script function against the FR-05 definition, including inputs with repeated lines where several shortest scripts exist. | Code review |
| NFR-09 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-10 | Security | The tool MUST open its inputs read-only, MUST NOT write any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (each followed by `Try 'dp-diff --help' for more information.` and exit 2; no
input is read and nothing is written to standard output):

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-diff: invalid option -- 'x'` |
| Unknown long option token `T` (as given, including any `=value`) | `dp-diff: unrecognized option 'T'` |
| `-U` without an argument | `dp-diff: option requires an argument -- 'U'` |
| `--brief=…`, `--strip-trailing-cr=…`, `--help=…`, `--version=…` | `dp-diff: option '--brief' doesn't allow an argument` (or the respective name) |
| Invalid context value `V` | `dp-diff: invalid argument 'V' for '-U'` (or `'--unified'`) |
| Fewer than two operands | `dp-diff: missing operand` |
| More than two operands; `X` is the third | `dp-diff: extra operand 'X'` |
| Both operands are `-` | `dp-diff: '-' may be given as only one operand` |

`--unified` never produces "requires an argument", because its argument is optional.

Runtime errors (no "Try" line; exit 2 after both operands have been attempted, FR-02):

| Trigger | Exact line |
| :-- | :-- |
| Operand `P` does not exist | `dp-diff: P: No such file or directory` |
| Operand `P` is not readable | `dp-diff: P: Permission denied` |
| Operand `P` is a directory | `dp-diff: P: Is a directory` |
| A component of `P` is not a directory | `dp-diff: P: Not a directory` |
| Any other failure opening or reading `P` (including `-`) | `dp-diff: P: Input/output error` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-05, FR-08 … FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-01, FR-02, FR-04, FR-05, FR-07, FR-09, FR-11, FR-12, FR-15, FR-18 |
| Unit test (written by the implementer) | FR-03 … FR-12, NFR-08 |
| Measurement | NFR-03, NFR-04, NFR-05 |
| Inspection / review | FR-19, NFR-07, NFR-10 |

Public test map (fixtures in `tests/public/fixtures/`):

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-diff same-1.txt same-2.txt` | FR-13 (identical files, exit 0) |
| 02 | `dp-diff fruits.txt fruits-changed.txt` | FR-08 (single change, `c`) |
| 03 | `dp-diff list-old.txt list-new.txt` | FR-08 (insertions `a`, deletions `d`) |
| 04 | `dp-diff -u long-old.txt long-new.txt` | FR-09, FR-11 (default context, merged hunk, clamped lead) |
| 05 | `dp-diff -U 1 long-old.txt long-new.txt` | FR-11, FR-12 (custom context, separate hunks) |
| 06 | `dp-diff pings.txt pongs.txt` | FR-05 (tie-breaking with repeated lines) |
| 07 | `dp-diff -u poem.txt poem-no-eol.txt` | FR-03, FR-10 (missing final newline) |
| 08 | `dp-diff --strip-trailing-cr crlf.txt lf.txt` | FR-04, FR-13 (CRLF vs LF equal) |
| 09 | `dp-diff -q fruits.txt fruits-changed.txt` | FR-14 |
| 10 | `dp-diff fruits.txt nosuch.txt` | FR-02, §3.7 (missing file, exit 2) |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-13, §3.7 |
| UR-02 | FR-03, FR-06, FR-08 |
| UR-03 | FR-09, FR-11, FR-12 |
| UR-04 | FR-14 |
| UR-05 | FR-01, FR-09, §3.4 |
| UR-06 | FR-04, NFR-02 |
| UR-07 | FR-03, FR-10 |
| UR-08 | FR-05, FR-09, FR-19, NFR-01, CONV-03 |
| UR-09 | FR-02, FR-15, FR-17, FR-18, §3.7 |
| UR-10 | FR-16 |
| UR-11 | FR-12, FR-17, CLI-CONV |
| UR-12 | §2.5, FR-05, FR-06, FR-07, NFR-08 |
| UR-13 | NFR-03, NFR-04, NFR-05 |
| UR-14 | NFR-09 |

## 9. Deviations

### 9.1 Overrides of CLI-CONV

| Convention | Override in this SRS |
| :-- | :-- |
| CONV-18 (exit status) | 0 = same, 1 = different, 2 = trouble (§3.7) |
| CONV-16 / CONV-17 (runtime errors exit 1) | Unreadable operands exit **2**; both operands are still attempted (FR-02) |
| CONV-08 (long option arguments) | `--unified` takes an *optional* argument that can only be attached with `=`; a bare `--unified` does not consume the next token (§3.2) |
| CONV-13 (usage error formats) | One additional usage error: `'-' may be given as only one operand` (FR-15) |

### 9.2 Deliberate differences from GNU diff

| GNU behavior | dp-diff behavior | Reason |
| :-- | :-- | :-- |
| Unified headers end with a tab and the file's modification time | Headers are `--- FILE1` / `+++ FILE2` only (FR-09) | Timestamps are environment-dependent and break byte-exact comparison |
| Edit script chosen by GNU's Myers variant and heuristics | Canonical edit script (FR-05) | Unique expected output across implementations |
| Directories are compared entry by entry | `Is a directory`, exit 2 (FR-02) | Out of scope |
| NUL bytes trigger `Binary files … differ` | No binary detection (FR-19) | Simplicity; byte-transparent output |
| `diff - -` compares standard input with itself | Usage error (FR-15) | Standard input can only be read once |
| `missing operand after 'X'` | `missing operand` (CONV-13) | Curriculum-wide message format |

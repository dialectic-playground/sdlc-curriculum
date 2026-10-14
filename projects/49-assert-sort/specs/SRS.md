# Software Requirements Specification (SRS) — dp-assert-sort

| Field | Value |
| :-- | :-- |
| Document ID | SRS-49 |
| Project | `49-assert-sort` — Formal Program Verification via Assertions & Loop Invariants |
| Product | `dp-assert-sort` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-49) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-assert-sort`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-assert-sort` reads integers as tokens from standard input or from one file, sorts them in
ascending order by selection sort, and writes them one per line. After every pass it checks a
bounds assertion and the loop invariant of selection sort on the actual array. It can write a
trace line for every invariant check that holds, and it can inject one of three precisely
defined faults into the algorithm so that a check fails. It reports a failed check, invalid
integers, and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| *a*, *n* | The array of the input's integers, in input order, indexed from 0, and its length; *a*[*k*] is the element at index *k* |
| Pass *i* | The *i*-th step of the sort (FR-03), for *i* = 0, 1, …, *n* − 2; there are no passes when *n* ≤ 1 |
| *min_ind* | The index chosen in a pass as the position of the minimum, after any fault has been applied (FR-03, FR-08) |
| Invariant *sorted(a, i, n)* | The condition of FR-05: *a*[0] ≤ *a*[1] ≤ … ≤ *a*[*i*], and *a*[*j*] ≥ *a*[*i*] for every *j* with *i* < *j* < *n* |
| Decimal | The plain ASCII decimal representation of an integer: a `-` before a negative value, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06) |
| Array text | The decimals of *a*[0], …, *a*[*n* − 1], in index order, separated by single spaces |

### 1.4 References
- URD-49: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §11.1 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-assert-sort` is a standalone executable. Its interfaces are the command line, standard
input or the file named by its operand, standard output, standard error, and the exit status.
It belongs to the curriculum's applications-programming track (Projects 11–52) and adapts
§11.1 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*. Its companion in the same
chapter, `dp-divide` (Project 50), treats the other side of defensive programming: recovering
from a fault instead of stopping at it.

### 2.2 Product functions
1. Read integers as tokens, and validate all of them before sorting.
2. Sort them by selection sort, checking the bounds assertion and the invariant after every
   pass.
3. Write the sorted integers, one per line.
4. Optionally write a trace line for every invariant check that holds.
5. Optionally inject a fault into one step of every pass or of one chosen pass.
6. Report a failed assertion, invalid integers, and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, apart from the design requirements of
  NFR-05.
- The checks of FR-04 and FR-05 MUST be evaluated on the array the sort is actually operating
  on, in every build of the tool (NFR-05).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only tokens that match the *integer* grammar are accepted.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §11.1 sorts the built-in array 5 4 3 2 1 by selection sort. In each
pass it finds the index of the minimum of the unsorted part, asserts that this index lies
inside the array, swaps, and asserts the invariant through a predicate `sorted(a, i, n)`: the
prefix a[0..i] is sorted and every later element is at least a[i]. It then prints the sorted
numbers. `dp-assert-sort` keeps:

- the algorithm exactly: *n* − 1 passes numbered from 0, the search for the minimum over
  a[i..n−1], one swap per pass, even when the minimum is already in place;
- the two assertions, their placement (the bounds assertion before the swap, the invariant
  after it), and their wording: the diagnostic quotes the bounds condition as
  `min_ind >= 0 && min_ind < n` and the invariant as `sorted(a, i, n)` with *i* and *n*
  replaced by their values;
- the textbook's array as the fixture `textbook.txt`, which sorts to 1 2 3 4 5 with every
  check holding (FR-06 AC).

It changes the following, for the reasons given:

- **Any input.** The integers are read from standard input or a file (FR-01, FR-02) instead of
  being built in, so the checks can be exercised on any data. They are validated before the
  sort starts, so a typo never produces partial output (FR-10).
- **Output layout.** The section's description does not fix the layout of the sorted numbers.
  The tool writes one integer per line, the usual form for a filter whose output feeds other
  tools (FR-06).
- **Tie rule.** The textbook's array has no equal elements. For equal minima the tool chooses
  the smallest index (a strict "less than" comparison), which makes *min_ind*, and therefore
  the trace and every diagnostic, fully determined (FR-03).
- **Assertions are part of the specification.** A C assertion prints an implementation-defined
  message and aborts the program, and disappears entirely when the program is compiled with
  `NDEBUG`. Here a failed check writes one specified diagnostic (FR-09) and exits with status 1
  like any other runtime failure, and the checks MUST be present in every build (NFR-05).
- **Fault injection.** The section asks the reader to corrupt the swap by hand and observe the
  assertion fail. The tool makes this reproducible with `-f`, `--fault`: three faults, each a
  precisely defined change to one step of a pass, injected in every pass or in one chosen pass
  (FR-08). Because the checks examine data rather than code, a fault that happens to leave the
  array correct is, correctly, not reported.
- **Trace.** `-t`, `--trace` makes each successful invariant check visible (FR-07). It is
  written to standard error, so the sorted output is identical with and without it, in the
  same way as prompts are kept off standard output (CONV-36).
- **No prompts.** The textbook program reads nothing from the keyboard, so the tool has no
  `--prompt` option; the input is a plain list of integers.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
*integer* grammar, with its full range −2⁶³ … 2⁶³−1 and no further restriction), CONV-34 (data
diagnostics, with the standard message `invalid integer` and the default consequences; no
output has been produced when it is reported), and CONV-37 (the input is *text data*). CONV-35
does not apply, because no real number is written; CONV-36 does not apply, because the tool
has no prompts (see §2.5); and CONV-38 does not apply, because nothing is random — the faults
are selected explicitly. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18: a failed assertion is a runtime
failure with status 1. Standard input is read as permitted by CONV-26. `dp-assert-sort` copies
no input bytes to its output (numbers are rewritten as decimals), so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-assert-sort [-t | --trace] [-f FAULT | --fault=FAULT] [FILE]
dp-assert-sort --help
dp-assert-sort --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-t` | `--trace` | none | off | Write a trace line to standard error for every invariant check that holds (FR-07) |
| `-f` | `--fault` | FAULT | none | Inject the fault FAULT into the sort (FR-08) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, attached values, `--`, repetition, and scan order) follows
CONV-07 … CONV-12: `-tf skip-swap`, `-fskip-swap`, `--fault skip-swap`, and
`--fault=skip-swap` are all valid. If `-f`/`--fault` is repeated, the last value is used
(CONV-11); only that value is validated. Giving `-t` more than once has the same effect as
giving it once.

FAULT has the form `KIND` or `KIND:PASS`:

- `KIND` is exactly one of `skip-swap`, `off-by-one`, and `search-from-next` (lowercase ASCII,
  as written).
- `PASS` is one or more ASCII digits (leading zeros allowed) whose value lies in
  0 … 9223372036854775807.

Any other value, including the empty string, a missing or empty `PASS` after `:`, a sign, and a
different letter case, is an invalid option value (FR-14).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The sorted integers (FR-06), written only when every pass has completed with both checks
holding. Nothing else. On a usage error, or when `--help` / `--version` is handled, the output
is as specified by FR-12 … FR-15 instead.

### 3.6 Standard error
Trace lines (FR-07, only with `--trace`) and diagnostics (section 6). Without `--trace`,
nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The input was sorted with every check holding (including an empty input), or `--help` / `--version` was handled |
| 1 | An assertion failed (FR-09), the input contained an invalid integer (FR-10), the input could not be opened or read (FR-11), or standard output could not be written |
| 2 | Usage error (FR-14) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `textbook.txt`, `mixed.txt`, and `bad.txt` are the
public fixture files in `tests/fixtures/`: `textbook.txt` is `5 4 3 2 1\n`; `mixed.txt` is
`12 -7\t+3\r\n0 3 -0\r\n\r\n  0042 -15\n`; `bad.txt` is `8 6\n7 5\n3 0x9 1\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. More than one operand is a
usage error (FR-14).
*AC:* `dp-assert-sort < textbook.txt`, `dp-assert-sort textbook.txt`, and
`dp-assert-sort - < textbook.txt` write the same output. *(UR-01, UR-08)*

**FR-02: Tokens and integers.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32). Each token
MUST be a valid *integer* (CONV-33): an optional sign and one or more ASCII digits, with a
value in −9223372036854775808 … 9223372036854775807. Leading zeros and a `+` sign are allowed.
Line structure has no meaning: integers may be separated by any mixture of space, TAB, VT, FF,
CR, and LF. The integers, in input order, form the array *a* of length *n* ≥ 0. The whole input
MUST be read and every token validated before the first pass starts; the first invalid token
is handled by FR-10. There is no limit on *n* other than available memory (see NFR-03).
*AC:* `dp-assert-sort mixed.txt` sorts the eight integers 12, −7, 3, 0, 3, 0, 42, −15.
*(UR-01, UR-10)*

**FR-03: Selection sort.**
The tool MUST sort *a* in place by the following algorithm, and by no other. For each pass
*i* = 0, 1, …, *n* − 2, in that order:

1. **Search.** Let *s* = *i* (or *s* = *i* + 1 under the fault `search-from-next`, FR-08).
   *min_ind* is the smallest index *k* with *s* ≤ *k* ≤ *n* − 1 such that *a*[*k*] ≤ *a*[*j*]
   for every *j* with *s* ≤ *j* ≤ *n* − 1; that is, among equal minima the leftmost one is
   chosen. (Scanning *k* = *s* + 1 … *n* − 1 and replacing the candidate only when
   *a*[*k*] < *a*[candidate] gives exactly this index.)
2. **Fault adjustment.** Under the fault `off-by-one`, *min_ind* becomes *min_ind* + 1 (FR-08).
3. **Bounds assertion** (FR-04).
4. **Swap.** The elements *a*[*i*] and *a*[*min_ind*] are exchanged (when *min_ind* = *i* this
   leaves *a* unchanged). Under the fault `skip-swap` this step is omitted (FR-08).
5. **Invariant check** (FR-05).
6. **Trace** (FR-07), only with `--trace`.

When *n* ≤ 1 there are no passes: nothing is checked, no trace line is written, and no fault
is injected. Elements are compared as signed 64-bit integers by their values.
*AC:* for `textbook.txt` the passes choose *min_ind* = 4, 3, 2, 3 and leave *a* as 1 4 3 2 5,
1 2 3 4 5, 1 2 3 4 5, 1 2 3 4 5; for the array 3 1 2 1 3 0 the passes choose
*min_ind* = 5, 1, 3, 3, 4. *(UR-02)*

**FR-04: Bounds assertion.**
In every pass, after the search and any fault adjustment and before the swap, the tool MUST
check that 0 ≤ *min_ind* < *n*. If the check fails, the pass stops at once (no swap, no
invariant check, no trace line) and FR-09 applies with the expression
`min_ind >= 0 && min_ind < n` and the detail `min_ind = <m>, n = <n>`, where `<m>` and `<n>`
are the decimals of *min_ind* and *n*. Without a fault this check always holds; with
`off-by-one` it fails in a pass whose minimum is at index *n* − 1.
*AC:* `dp-assert-sort --fault=off-by-one textbook.txt` → stderr
`dp-assert-sort: assertion failed in pass 0: min_ind >= 0 && min_ind < n (min_ind = 5, n = 5)\n`.
*(UR-03, UR-06)*

**FR-05: Invariant check.**
In every pass *i*, after the swap step, the tool MUST evaluate *sorted(a, i, n)* on the current
array, and MUST do so through a single predicate of the array, *i*, and *n* (NFR-05). The
check examines the two conditions in this order and reports the **first** violation found:

1. *Prefix sorted:* for *k* = 1, 2, …, *i*, in increasing order, the first *k* with
   *a*[*k* − 1] > *a*[*k*] is a violation with the detail
   `a[<k−1>] = <x> > a[<k>] = <y>`, where `<x>` = *a*[*k* − 1] and `<y>` = *a*[*k*].
2. *Suffix not smaller:* for *j* = *i* + 1, …, *n* − 1, in increasing order, the first *j* with
   *a*[*j*] < *a*[*i*] is a violation with the detail `a[<j>] = <x> < a[<i>] = <y>`, where
   `<x>` = *a*[*j*] and `<y>` = *a*[*i*].

Indices and values are written as decimals. If a violation is found, FR-09 applies with the
expression `sorted(a, <i>, <n>)` (the decimals of *i* and *n*) and that detail. At *i* = 0 the
first condition is empty, so the check asserts that *a*[0] is not greater than any later
element; at *i* = *n* − 2 a successful check means the whole array is sorted. No separate
final check is made.
*AC:* `dp-assert-sort -f skip-swap textbook.txt` → stderr
`dp-assert-sort: assertion failed in pass 0: sorted(a, 0, 5) (a[1] = 4 < a[0] = 5)\n`.
*(UR-03, UR-06)*

**FR-06: Output.**
When every pass has completed with both checks holding, the tool MUST write the elements of
the sorted array, in index order, each as its decimal followed by one LF, and nothing else: no
header, no blank line, no spaces. Each integer is written as its value, not as its token was
spelled (`+3`, `0042`, and `-0` are written as `3`, `42`, and `0`). An empty input (or one with
only whitespace and a trailing Ctrl-Z run) produces no output and exit status 0. The output
does not depend on `--trace`.
*AC:* `dp-assert-sort < textbook.txt` → stdout `1\n2\n3\n4\n5\n`, stderr empty, exit 0;
`dp-assert-sort mixed.txt` → stdout `-15\n-7\n0\n0\n3\n3\n12\n42\n`, exit 0. *(UR-01)*

**FR-07: Trace.**
With `-t`, `--trace`, after each invariant check that holds, the tool MUST write to standard
error the line

```text
pass <i>: min_ind = <m> in bounds; a = <array text>; sorted(a, <i>, <n>) holds
```

where `<i>`, `<m>`, and `<n>` are the decimals of *i*, *min_ind*, and *n*, and
`<array text>` is the array text (section 1.3) after the swap step of that pass. The line ends
with one LF; there are no other spaces than those shown. No trace line is written for a pass
in which a check fails, and none at all when *n* ≤ 1. Trace lines are written in pass order,
and those already written are kept when a later check fails.
*AC:* `dp-assert-sort --trace textbook.txt` → stdout as in FR-06, stderr
`pass 0: min_ind = 4 in bounds; a = 1 4 3 2 5; sorted(a, 0, 5) holds\n` followed by the lines
for passes 1, 2, and 3 (`min_ind = 3`, `2`, `3`, each with `a = 1 2 3 4 5`), exit 0.
*(UR-04)*

**FR-08: Fault injection.**
With `-f FAULT`, `--fault=FAULT` (syntax in section 3.2), the fault KIND is injected into
pass *p* if FAULT has the form `KIND:p`, and into every pass if it has the form `KIND`. A pass
into which no fault is injected runs exactly as in FR-03. If *p* ≥ *n* − 1, no pass has number
*p*, and the run is the same as without `--fault`. The three faults change exactly one step of
an affected pass:

| KIND | Step changed (FR-03) | Effect in the affected pass |
| :-- | :-- | :-- |
| `skip-swap` | 4 (swap) | The swap is omitted; *min_ind* is still computed and checked |
| `off-by-one` | 2 (fault adjustment) | *min_ind* is one more than the index of the leftmost minimum; the bounds assertion and the swap use the adjusted value |
| `search-from-next` | 1 (search) | The search for the minimum covers *a*[*i* + 1 … *n* − 1] instead of *a*[*i* … *n* − 1]; since *i* ≤ *n* − 2 this range is never empty |

The checks themselves are never changed by a fault. A fault is detected only through the
checks: if an injected fault leaves the array in a state that satisfies the invariant (for
example `skip-swap` in a pass whose minimum is already at index *i*, or `search-from-next` when
*a*[*i*] is not smaller than the minimum of the rest), the pass completes normally and the run
continues.
*AC:* with `textbook.txt`: `-t --fault=search-from-next` → trace lines for passes 0 and 1, then
`dp-assert-sort: assertion failed in pass 2: sorted(a, 2, 5) (a[3] = 3 < a[2] = 4)`, exit 1;
`--fault off-by-one:1` → `assertion failed in pass 1: sorted(a, 1, 5) (a[2] = 3 < a[1] = 5)`,
exit 1; `-f skip-swap:3` and `--fault=off-by-one:4` → stdout `1\n2\n3\n4\n5\n`, exit 0.
*(UR-05)*

**FR-09: Assertion failure.**
When a check of FR-04 or FR-05 fails in pass *i*, the tool MUST write to standard error the
single line

```text
dp-assert-sort: assertion failed in pass <i>: <expression> (<detail>)
```

with `<i>` the decimal of *i* and `<expression>` and `<detail>` as defined in FR-04 or FR-05,
and then stop: no further pass is run, nothing is written to standard output, and the exit
status is 1. Trace lines already written (FR-07) are kept, so with `--trace` the diagnostic
follows the trace line of pass *i* − 1.
*AC:* public tests 04, 05, and 06: stdout empty, exactly one diagnostic line, exit 1.
*(UR-06, UR-07)*

**FR-10: Invalid integers.**
If a token is not a valid *integer* (CONV-33), including an integer outside
−2⁶³ … 2⁶³−1, the tool MUST write `dp-assert-sort: <source>:<line>: invalid integer '<token>'`,
where `<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32),
and `<token>` is the token's exact bytes (CONV-34). Only the first invalid token is reported.
Because all tokens are validated before the sort (FR-02), nothing has been written to standard
output and no trace line has been written. The exit status is 1.
*AC:* `dp-assert-sort bad.txt` → stdout empty, stderr
`dp-assert-sort: bad.txt:3: invalid integer '0x9'\n`, exit 1. The tokens
`-9223372036854775809` and `9223372036854775808` give `invalid integer`; a token `1` followed
by a `0x1A` byte and more input gives `invalid integer` because that Ctrl-Z byte does not end
the input. *(UR-09)*

**FR-11: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-assert-sort: <source>: <reason>` with `<reason>` from the CONV-16
table, write nothing to standard output, and exit with status 1. When standard input fails,
`<source>` is `-`.
*AC:* `dp-assert-sort missing.txt` → stderr
`dp-assert-sort: missing.txt: No such file or directory\n`, stdout empty, exit 1;
`dp-assert-sort subdir` where `subdir` is a directory → `dp-assert-sort: subdir: Is a directory`.
*(UR-09)*

**FR-12: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-assert-sort --help` matches the user manual exactly; `dp-assert-sort extra --help`
and `dp-assert-sort --fault=bogus --help` also print it. *(UR-11)*

**FR-13: Version.**
`--version` MUST write `dp-assert-sort (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-11)*

**FR-14: Usage errors.**
Unknown options, a missing argument to `-f`/`--fault`, and arguments supplied to options that
take none (`--trace=…`, `--help=…`, `--version=…`), MUST be reported with the CONV-13 messages
followed by the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated
(CONV-08). After the whole argument list has been scanned (CONV-12), the tool checks, in this
order: the FAULT value (section 3.2), reported as
`dp-assert-sort: invalid argument '<value>' for '<option>'` with `<option>` the option as last
written (`-f` or `--fault`); then the number of operands, a second operand being reported as
`dp-assert-sort: extra operand '<second operand>'`.
*AC:* `dp-assert-sort --fault=bogus textbook.txt` →
`dp-assert-sort: invalid argument 'bogus' for '--fault'`; `-f :1` →
`invalid argument ':1' for '-f'`; `--fault ''` → `invalid argument '' for '--fault'`;
`dp-assert-sort textbook.txt -f` → `dp-assert-sort: option requires an argument -- 'f'`;
`dp-assert-sort - extra` → `dp-assert-sort: extra operand 'extra'`; `--trace=yes` →
`dp-assert-sort: option '--trace' doesn't allow an argument`; each followed by the CONV-14
line, exit 2. *(UR-11, UR-12)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: assertions that behave the same everywhere | A failed check MUST produce exactly the diagnostic of FR-09 and exit status 1 on every platform. It MUST NOT rely on a platform's assertion facility, abort routine, signal, crash dialog, core dump, or debugger hook, whose messages, exit statuses (for example 134 on POSIX shells, 3 or a dialog on Windows), and side effects differ between operating systems and runtimes. The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. Standard output and standard error MUST be written in binary mode (CONV-03). | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Sorting 10 000 integers without `--trace` MUST take under 2 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Each invariant check MUST take time proportional to *n*, so a run takes time proportional to *n*²; memory MUST be proportional to *n*, and the trace MUST be written line by line, not collected. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and every FAULT on every input (an `off-by-one` index MUST be caught by the bounds assertion before it is used to access the array). A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, FAULT parsing, tokenizing and validation, the sort, the invariant predicate, output formatting, and I/O MUST be separate units. The invariant MUST be one predicate function of the array, *i*, and *n* that returns whether *sorted(a, i, n)* holds (and, for the diagnostic, the first violation); the sort MUST call it after every pass. The bounds assertion and the invariant check MUST be active in every build configuration: they MUST NOT be implemented with a language or library assertion facility that a release or optimized build can disable (such as C's `assert` under `NDEBUG`, Java's `assert` without `-ea`, Python's `assert` under `-O`, or Rust's `debug_assert!`). Fault injection MUST change only the steps listed in FR-08 and MUST NOT alter or bypass the checks. | Design review |
| NFR-06 | Testability | The invariant predicate MUST be a pure function covered by unit tests, including arrays that satisfy it, arrays that violate only the prefix condition, arrays that violate only the suffix condition, *i* = 0, *i* = *n* − 2, and equal elements. The sort MUST be unit-testable with each fault in each pass of a small array. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-assert-sort --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-assert-sort: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-assert-sort: unrecognized option 'T'` |
| `-f` as the last argument | `dp-assert-sort: option requires an argument -- 'f'` |
| `--fault` as the last argument | `dp-assert-sort: option '--fault' requires an argument` |
| `--trace=…`, `--help=…`, `--version=…` | `dp-assert-sort: option '--trace' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| Invalid FAULT value `V` given with `-f` or `--fault` | `dp-assert-sort: invalid argument 'V' for '-f'` (or `'--fault'`) |
| A second operand `X` | `dp-assert-sort: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-assert-sort: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-assert-sort: F: Permission denied` |
| FILE `F` is a directory | `dp-assert-sort: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-assert-sort: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-assert-sort: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *integer* | `dp-assert-sort: S:L: invalid integer 'K'` |
| Bounds assertion fails in pass `I` with index `M` and length `N` | `dp-assert-sort: assertion failed in pass I: min_ind >= 0 && min_ind < n (min_ind = M, n = N)` |
| Invariant fails in pass `I` (length `N`) on the prefix at indices `K−1`, `K` with values `X`, `Y` | `dp-assert-sort: assertion failed in pass I: sorted(a, I, N) (a[K−1] = X > a[K] = Y)` |
| Invariant fails in pass `I` (length `N`) on the suffix at index `J` with value `X`, *a*[`I`] = `Y` | `dp-assert-sort: assertion failed in pass I: sorted(a, I, N) (a[J] = X < a[I] = Y)` |
| Standard output cannot be written (other than a broken pipe) | `dp-assert-sort: write error` |

In the invariant rows, `K−1` stands for the decimal of the index *k* − 1. With the faults of
FR-08 the prefix condition cannot fail (every fault moves only elements at index *i* or later,
and the prefix a[0..i−1] was verified in the previous pass), but the check and its message are
required nonetheless.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-12, FR-14, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 and 04 … 10 have several steps) | FR-02 … FR-15 |
| Unit test (written by the implementer) | FR-03 … FR-05, FR-08, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-assert-sort < textbook.txt` | FR-01, FR-03, FR-06 |
| 02 | `dp-assert-sort --trace textbook.txt` | FR-05, FR-07 |
| 03 | `dp-assert-sort mixed.txt` | FR-02 (CRLF, TAB, signs, leading zeros, duplicates), FR-06 |
| 04 | `dp-assert-sort --fault=off-by-one textbook.txt` | FR-04, FR-08, FR-09 |
| 05 | `dp-assert-sort -t --fault=search-from-next textbook.txt` | FR-05, FR-07, FR-08, FR-09 |
| 06 | `dp-assert-sort -f skip-swap - < textbook.txt` | FR-01, FR-05, FR-08, FR-09 |
| 07 | `dp-assert-sort bad.txt` | FR-10 |
| 08 | `dp-assert-sort missing.txt` | FR-11 |
| 09 | `dp-assert-sort --help` | FR-12 |
| 10 | `dp-assert-sort --fault=bogus textbook.txt` | FR-14, FR-15 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-02, FR-06 |
| UR-02 | FR-03 |
| UR-03 | FR-04, FR-05 |
| UR-04 | FR-07 |
| UR-05 | FR-08 |
| UR-06 | FR-04, FR-05, FR-09 |
| UR-07 | FR-09 |
| UR-08 | FR-01, CONV-26 |
| UR-09 | FR-10, FR-11, CONV-16, CONV-33, CONV-34 |
| UR-10 | FR-02, NFR-02, CONV-37 |
| UR-11 | FR-12, FR-13, FR-14, FR-15 |
| UR-12 | FR-14, NFR-01, NFR-02, CONV-03, CLI-CONV |
| UR-13 | NFR-03, NFR-07 |
| UR-14 | NFR-02, NFR-05 |

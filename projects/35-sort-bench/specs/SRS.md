<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-sort-bench](#software-requirements-specification-srs--dp-sort-bench)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
    - [2.5 Relationship to the textbook program (informative)](#25-relationship-to-the-textbook-program-informative)
    - [2.6 Relationship to CLI-CONV](#26-relationship-to-cli-conv)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-sort-bench

| Field                     | Value                                                      |
| :------------------------ | :--------------------------------------------------------- |
| Document ID               | SRS-35                                                     |
| Project                   | `35-sort-bench` — Empirical Algorithm Runtime Benchmarking |
| Product                   | `dp-sort-bench` (canonical name)                           |
| Version                   | 1.0.0                                                      |
| Status                    | Approved (pre-written by the curriculum)                   |
| Parent document           | `URD.md` (URD-35)                                          |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)               |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                       |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-sort-bench`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation that does not request timing. It is the
authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-sort-bench` generates arrays of pseudo-random integers of chosen sizes (by default 1000,
2000, and 4000), sorts a copy of each array with a quadratic algorithm (selection sort) and a
copy with an _N_ log _N_ algorithm (quicksort), both specified step by step, and reports for
each sort the exact number of comparisons and swaps it made and whether its result is sorted.
On request it also reports the elapsed time of each sort, measured with a monotonic clock.
The report without timing is a pure function of the sizes and the seed.

### 1.3 Definitions

| Term           | Definition                                                                                                                             |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| LF, TAB        | The bytes `0x0A` and `0x09`                                                                                                            |
| Size           | The number of elements _n_ of one array, 0 … 100000                                                                                    |
| Size list      | The sizes to benchmark, in the order given (FR-01)                                                                                     |
| Original array | The array generated for one size (FR-02); it is never sorted itself                                                                    |
| Clone          | A copy of the original array, element for element, made for one algorithm (FR-03)                                                      |
| _a_[0 … *n*−1] | The clone being sorted; positions are numbered from 0                                                                                  |
| Comparison     | One evaluation of the order relation between two array elements, as counted by FR-06                                                   |
| Swap           | An exchange of the elements at two **different** positions, as counted by FR-06                                                        |
| ⌊_x_⌋          | The largest integer not greater than _x_                                                                                               |
| Block          | The report lines for one size (FR-08)                                                                                                  |
| Decimal        | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References

- URD-35: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular CONV-35 and CONV-38
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §6.10 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-sort-bench` is a standalone executable. Its interfaces are the command line, standard
output, standard error, and the exit status; it reads no input. It belongs to the curriculum's
applications-programming track (Projects 11–52) and adapts §6.10 of Johnsonbaugh & Kalin,
_Applications Programming in ANSI C_, which times sorting functions on arrays of growing size.
Selection sort is also the sort of `dp-sort-host` and `dp-sort-child` (Project 34).

### 2.2 Product functions

1. Generate one pseudo-random array per requested size, from one seeded generator.
2. Sort a clone of each array with selection sort and another with quicksort.
3. Count the comparisons and swaps of each sort exactly.
4. Verify that each sort's result is the sorted original.
5. Report the counts and the verification, and optionally the elapsed time of each sort.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through FR-04 … FR-06 and NFR-05, the two
  sorting algorithms.
- The two sorts MUST be implemented by the project itself; a library sort MUST NOT be used for
  them (it MAY be used for the verification of FR-07).

### 2.4 Assumptions

- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Elapsed times (FR-09) depend on the machine and its load; they are informative and are never
  compared by tests.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §6.10 fills arrays of 1000, 2000, and 4000 random integers, gives a
copy of each to a quadratic sort and to quicksort through a function pointer, and prints the
elapsed time of each sort under the headings `Array size:` and `Algorithm:`. `dp-sort-bench`
keeps:

- the default sizes 1000, 2000, 4000, in that order, one random array per size, and a fresh
  copy of the same array for each algorithm;
- a quadratic sort (selection sort) and quicksort;
- the report headings and their layout: `Array size: <n>`, a TAB-indented
  `Algorithm: <name>` line per algorithm, and TAB-TAB-indented result lines, with a blank line
  between sizes;
- the line `Time = <seconds> seconds` with six decimals, now behind the opt-in `--time`.

It changes the following, for the reasons given:

- **Deterministic default report.** Elapsed times differ on every run and every machine, so
  they cannot be the specified output. The default report gives exact operation counts
  instead (FR-06), which show the same growth — comparisons of selection sort grow 4× when _n_
  doubles; those of quicksort only about 2× — and can be checked byte for byte. Times
  are written only with `--time` (FR-09), which the black-box tests never use.
- **Fully specified algorithms.** The textbook's sorts are not reproduced. FR-04 and FR-05 fix
  selection sort and a quicksort (pivot: the middle element, moved to the left end;
  partition: one left-to-right scan) precisely enough that every implementation makes the same
  comparisons and swaps.
- **Portable random numbers.** The textbook used the C library's `rand()`, whose sequence
  differs between libraries. The arrays here come from the CONV-38 generator with `--seed`
  (FR-02), so the report is the same everywhere.
- **Verification.** Each result is checked against the sorted original (FR-07), which also
  guards against an optimizer removing a sort whose result is unused.
- **Chosen sizes.** `-s`, `--sizes` replaces the fixed sizes, for quick experiments and fast
  tests (FR-01).
- **Clock.** The textbook measured with a one-second calendar clock, which reports 0 for fast
  sorts. FR-09 requires a monotonic clock with sub-microsecond resolution where available.
- No prompts: the textbook program read nothing from the keyboard.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Of the
conventions for Projects 11–52:

| Convention                         | Use in this SRS                                                    |
| :--------------------------------- | :----------------------------------------------------------------- |
| CONV-32, CONV-33, CONV-34, CONV-37 | Not applicable: the tool reads no input.                           |
| CONV-35                            | `FIX(t, 6)` writes the elapsed times of `--time` (FR-09).          |
| CONV-36                            | Not applicable: the tool has no prompts.                           |
| CONV-38                            | Generates every array; `--seed` with the default 1 (FR-02, FR-10). |

The tool reads no standard input (CONV-26) and copies no input to its output, so CONV-04 does
not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-sort-bench [-s LIST | --sizes=LIST] [--seed=SEED] [-t | --time]
dp-sort-bench --help
dp-sort-bench --version
```

### 3.2 Options

| Short | Long        | Argument | Default          | Description                                       |
| :---- | :---------- | :------- | :--------------- | :------------------------------------------------ |
| `-s`  | `--sizes`   | LIST     | `1000,2000,4000` | The sizes to benchmark, in order (FR-01)          |
| —     | `--seed`    | SEED     | `1`              | Initial state of the generator (FR-10, CONV-38)   |
| `-t`  | `--time`    | none     | off              | Also report the elapsed time of each sort (FR-09) |
| —     | `--help`    | none     | —                | Print the help text and exit 0                    |
| —     | `--version` | none     | —                | Print the version line and exit 0                 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. If
`--sizes` or `--seed` is given more than once, the last value wins (CONV-11); only that value
is validated.

### 3.3 Operands

None. Every operand, including one after `--`, is a usage error (FR-13).

### 3.4 Standard input

Never read (CONV-26).

### 3.5 Standard output

The report (FR-08). Nothing else. On a usage error, or when `--help` / `--version` is
handled, the output is as specified by FR-11 … FR-13 instead.

### 3.6 Standard error

Diagnostics only (section 6). Nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                   |
| :----- | :------------------------------------------------------------------------------------------ |
| 0      | The report was written and every result was verified, or `--help` / `--version` was handled |
| 1      | A result failed verification (FR-07), or standard output could not be written               |
| 2      | Usage error (FR-13)                                                                         |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF and `\t` denotes TAB.

**FR-01: Sizes.**
Without `-s`, `--sizes`, the size list is 1000, 2000, 4000. With it, the size list is LIST: one
or more SIZEs separated by single commas, with no other characters, where each SIZE is one or
more ASCII digits (leading zeros allowed) whose value is 0 … 100000. Sizes may repeat and may
appear in any order; each entry of the list is benchmarked, in list order. Any other LIST —
empty, with an empty item (`10,,20`, `5,`, `,5`), a sign, a space, or a value above 100000 —
is an invalid option value (FR-13).
_AC:_ `dp-sort-bench --sizes=10,20,40` writes blocks for 10, 20, and 40, in that order;
`-s 0010,2` benchmarks 10 and 2; `--sizes=100001` and `-s 10,,20` are usage errors. _(UR-01,
UR-02)_

**FR-02: Random arrays.**
One CONV-38 generator is seeded once, with SEED (FR-10), before the first array is generated.
The sizes are processed in list order; for a size _n_, the original array is filled with the
next _n_ draws, in order: element _i_ (0 ≤ _i_ < _n_) is the (_i_ + 1)-th of those draws, the
integer _r_ in 0 … 32767 itself. No other draw is made. Consequently the array for a size
depends on the sizes before it in the list, and a list that starts with 1000 gives the same
first block as the default list.
_AC:_ with the default seed, the arrays for `-s 0,1,2,3` are [], [16838], [5758, 10113], and
[17515, 31051, 5627]; `dp-sort-bench -s 1000` writes the same block for 1000 as
`dp-sort-bench`. _(UR-03, UR-05)_

**FR-03: Clones.**
For each size, selection sort and then quicksort are each applied to their own clone of the
original array. Neither sort sees the other's result, and the original array is not modified,
so both sorts start from the same element order.
_AC:_ the counts reported for quicksort are those of FR-05 applied to the original array, not
to the output of selection sort (an already sorted array would give other counts). _(UR-03)_

**FR-04: Selection sort.**
Selection sort on _a_[0 … *n*−1] MUST perform exactly these steps: for each _i_ from 0 to
_n_ − 2 in increasing order, scan _j_ = _i_ + 1, …, _n_ − 1 in increasing order, keeping the
position _m_ (initially _i_) of the smallest element seen so far; for each _j_, compare
_a_[_j_] < _a_[_m_] and, if true, set _m_ ← _j_ (so _m_ is the **first** position of the
smallest remaining element). After the scan, if _m_ ≠ _i_, exchange _a_[_i_] and _a_[_m_]. For
_n_ ≤ 1 nothing is done.
_AC:_ for [17515, 31051, 5627]: 3 comparisons and 2 swaps; for [5758, 10113]: 1 comparison and
0 swaps. _(UR-04)_

**FR-05: Quicksort.**
Quicksort on a range _a_[_L_ … _R_] (initially _L_ = 0, _R_ = _n_ − 1) MUST perform exactly
these steps:

1. If _L_ ≥ _R_, the range is finished (nothing is compared or exchanged).
2. Let _M_ = ⌊(_L_ + _R_) / 2⌋. Exchange _a_[_L_] and _a_[_M_] (moving the middle element, the
   pivot, to the left end).
3. Let _p_ be the value now in _a_[_L_], and _last_ ← _L_. For each _k_ = _L_ + 1, …, _R_ in
   increasing order: compare _a_[_k_] < _p_; if true, set _last_ ← _last_ + 1 and exchange
   _a_[_last_] and _a_[_k_].
4. Exchange _a_[_L_] and _a_[_last_] (putting the pivot in its final place).
5. Apply quicksort to _a_[_L_ … _last_ − 1] and to _a_[_last_ + 1 … _R_].

The two ranges of step 5 MAY be processed in either order, recursively or with an explicit
stack, because they are disjoint and their counts do not depend on the order. Implementations
SHOULD process the smaller range first or iterate on the larger one, to bound the depth of
recursion by log₂ _n_ (NFR-04).
_AC:_ for [17515, 31051, 5627]: 3 comparisons and 2 swaps; with the default seed and sizes, the
first block reports `Comparisons = 11412` and `Swaps = 5980` for quicksort. _(UR-04)_

**FR-06: Operation counts.**
For each sort, the tool MUST count:

- **Comparisons:** each comparison of FR-04 (_a_[_j_] < _a_[_m_]) and of FR-05 step 3
  (_a_[_k_] < _p_) counts 1, whatever its result. No other comparison counts — in particular
  not the index comparisons that control the loops, _L_ ≥ _R_, or _m_ ≠ _i_. Selection sort
  therefore always makes _n_(_n_ − 1) / 2 comparisons, and quicksort makes _R_ − _L_ for each
  range with _L_ < _R_.
- **Swaps:** each exchange of FR-04 and FR-05 steps 2, 3, and 4 whose two positions are
  **different** counts 1. An exchange of a position with itself (for example _M_ = _L_, or
  _last_ = _k_) is not counted, whether or not the implementation performs it.

Counts are exact integers (64-bit is ample: at most 4 999 950 000 comparisons for one sort).
_AC:_ `dp-sort-bench -s 0,1,2,3` reports 0/0, 0/0, 1/0, and 3/2 comparisons/swaps for both
algorithms; the default run reports `Comparisons = 499500`, `1999000`, and `7998000` for
selection sort. _(UR-04, UR-06)_

**FR-07: Verification.**
After each sort, the tool MUST check that the clone is element for element equal to the
original array sorted in non-decreasing order (that is, it is sorted _and_ it is a permutation
of the original). The check MAY use any correct method, including a library sort of another
copy. The result is reported as `yes` or `no` (FR-08). If any check gives `no`, the tool
completes the report, then writes `dp-sort-bench: verification failed` to standard error and
exits with status 1. (A conforming implementation never gives `no`; the rule exists so that a
defective sort is reported instead of hidden.)
_AC:_ every block of every test reports `Sorted = yes`, and the exit status is 0. _(UR-07)_

**FR-08: Report format.**
For each size _n_ of the list, in order, the tool writes one block. Blocks after the first are
preceded by one empty line. A block is exactly:

```text
Array size: <n>
\tAlgorithm: Selection Sort
[\t\tTime = <seconds> seconds]
\t\tComparisons = <c>
\t\tSwaps = <s>
\t\tSorted = <yes|no>
\tAlgorithm: Quicksort
[\t\tTime = <seconds> seconds]
\t\tComparisons = <c>
\t\tSwaps = <s>
\t\tSorted = <yes|no>
```

where `\t` is one TAB byte, the bracketed `Time` lines appear only with `--time` (FR-09),
`<n>`, `<c>`, and `<s>` are decimals (section 1.3), every line ends with one LF, and there are no
other spaces: one space after each colon, one on each side of `=`. There is no header, no
trailing empty line, and no summary. Each block MUST be written, and standard output flushed,
as soon as its two sorts and their verification are complete, before the next array is
generated.
_AC:_ `dp-sort-bench -s 3` (the array [16838, 5758, 10113]) writes exactly
`Array size: 3\n\tAlgorithm: Selection Sort\n\t\tComparisons = 3\n\t\tSwaps = 2\n\t\tSorted = yes\n\tAlgorithm: Quicksort\n\t\tComparisons = 3\n\t\tSwaps = 2\n\t\tSorted = yes\n`,
stderr empty, exit 0. `dp-sort-bench -s 0,1` writes two blocks separated by exactly one empty
line. _(UR-05, UR-06)_

**FR-09: Timing.**
With `-t`, `--time`, each algorithm section contains the line `\t\tTime = <seconds> seconds`
directly after its `Algorithm:` line (FR-08). `<seconds>` is `FIX(t, 6)` (CONV-35) of the
elapsed time _t_ in seconds, a binary64 value. _t_ MUST be measured with a **monotonic** clock
(one that is never adjusted backwards or forwards by time synchronization, such as
`CLOCK_MONOTONIC`, `mach_absolute_time`, or `QueryPerformanceCounter`), never with the
time-of-day clock or with processor time. The clock is read immediately before the sort starts
and immediately after it returns; _t_ covers the sort of FR-04 or FR-05 with its counting,
and excludes generating the array, cloning, verification, and output. If the clock reports a
negative difference, _t_ is 0. Timing MUST NOT change any other byte of the report. The
black-box tests never use this option.
_AC (manual):_ `dp-sort-bench -t` writes six `Time = …` lines, each with six decimals; the
selection-sort times grow about 4× from one default size to the next. _(UR-08)_

**FR-10: Seed.**
`--seed=SEED` sets the generator's initial state (CONV-38): SEED consists only of ASCII digits
(leading zeros allowed) and lies in 0 … 4294967295. Without the option the seed is 1. Any other
SEED (empty, signed, non-digit, or larger) is an invalid option value (FR-13).
_AC:_ `dp-sort-bench --seed=0 --sizes=1000` reports 992 swaps for selection sort, while the
default seed gives 990; `--seed 00001` is the same as the default; `--seed=4294967296`,
`--seed=-1`, `--seed=+1`, and `--seed=` are usage errors. _(UR-03)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12.
_AC:_ `dp-sort-bench --help` matches the user manual exactly; `dp-sort-bench extra --help` also
prints it. _(UR-09)_

**FR-12: Version.**
`--version` MUST write `dp-sort-bench (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-sort-bench --time --version` also prints it. _(UR-09)_

**FR-13: Usage errors.**
Unknown options, a missing option argument, and arguments supplied to options that take none
(`--time=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08). After the
whole argument list has been scanned (CONV-12), the remaining checks are made in this order,
and the first failure is reported: (1) the last LIST (FR-01), as
`dp-sort-bench: invalid argument '<LIST>' for '<option>'`; (2) the last SEED (FR-10), in the
same form; (3) the first operand, as `dp-sort-bench: extra operand '<operand>'`. `<option>` is
the option as last written (`-s` or `--sizes`; `--seed`).
_AC:_ `dp-sort-bench extra` → `dp-sort-bench: extra operand 'extra'`;
`dp-sort-bench -s 5 --seed=x extra` → `dp-sort-bench: invalid argument 'x' for '--seed'`;
`dp-sort-bench --sizes --help` → `dp-sort-bench: invalid argument '--help' for '--sizes'`
(the option consumes `--help` as its value); `dp-sort-bench -x --help` →
`dp-sort-bench: invalid option -- 'x'`; each followed by the CONV-14 line, exit 2. _(UR-10)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT generate any array or write anything to standard
output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-10)_

## 5. Non-functional requirements

| ID     | Category                                       | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Verification                              |
| :----- | :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| NFR-01 | Portability                                    | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows for every invocation without `--time`, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: reproducible measurement | Every array MUST come from the CONV-38 generator, computed in exact unsigned 32-bit arithmetic (no platform `rand()`, no floating point), so the default report is identical on every platform and compiler. Elapsed times MUST come from the platform's monotonic high-resolution clock (`clock_gettime(CLOCK_MONOTONIC)` or equivalent on Linux, `mach_absolute_time`/`clock_gettime_nsec_np(CLOCK_UPTIME_RAW)` or equivalent on macOS, `QueryPerformanceCounter` on Windows, or the language runtime's documented monotonic clock); its readings are converted to seconds as binary64 only after subtracting. The verification of FR-07 MUST use the sorted result, so no compiler or runtime can remove a sort as dead code. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                    | The default run (sizes 1000, 2000, 4000) MUST finish in under 0.5 s for a natively compiled build (under 5 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST be O(_n_) for the largest size, independent of the number of sizes: only the original array, one clone, and the verification copy of the current size are held. Quicksort on random data MUST make O(_n_ log _n_) comparisons; selection sort makes exactly _n_(_n_ − 1)/2.                                                                                                                                                                      | Measurement                               |
| NFR-04 | Robustness                                     | The tool MUST NOT crash, panic, or print a stack trace for any argument list (CONV-24), including option values of any length. Quicksort MUST NOT overflow the call stack for any size up to 100000, whatever the element order. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                               | Unit + black-box tests                    |
| NFR-05 | Maintainability                                | Option parsing, the generator, array cloning, each sorting algorithm, the counters, verification, timing, and report formatting MUST be separate units. The benchmark loop MUST call the two sorts through one common interface (a function value, interface, or trait taking an array and returning its counts), as the textbook calls its sorts through a function pointer, so a third algorithm can be added without changing the loop. The two sorts MUST NOT write output or read the clock.                                                                                                                                                                                                                                | Design review                             |
| NFR-06 | Testability                                    | The generator MUST be unit-tested against the first draws for seeds 1 and 0. Each sort MUST be unit-tested on the empty array, one element, two elements in both orders, all-equal elements, sorted and reversed arrays, and the arrays of FR-02's acceptance criterion, checking both the result and the exact counts of FR-06.                                                                                                                                                                                                                                                                                                                                                                                                 | Code review                               |
| NFR-07 | Build                                          | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | CI                                        |
| NFR-08 | Security                                       | The tool MUST NOT read any file or standard input, create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Inspection                                |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by
`Try 'dp-sort-bench --help' for more information.`

| Trigger                                        | Exact first line                                                                          |
| :--------------------------------------------- | :---------------------------------------------------------------------------------------- |
| Unknown short option `x`                       | `dp-sort-bench: invalid option -- 'x'`                                                    |
| Unknown or abbreviated long option token `T`   | `dp-sort-bench: unrecognized option 'T'`                                                  |
| `-s` as the last argument                      | `dp-sort-bench: option requires an argument -- 's'`                                       |
| `--sizes` or `--seed` as the last argument     | `dp-sort-bench: option '--sizes' requires an argument` (or `'--seed'`)                    |
| `--time=…`, `--help=…`, `--version=…`          | `dp-sort-bench: option '--time' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| Invalid LIST `V` (FR-01) given with option `O` | `dp-sort-bench: invalid argument 'V' for 'O'`                                             |
| Invalid SEED `V` (FR-10)                       | `dp-sort-bench: invalid argument 'V' for '--seed'`                                        |
| An operand `X`                                 | `dp-sort-bench: extra operand 'X'`                                                        |

Runtime errors (exit status 1):

| Trigger                                                                 | Exact message                        |
| :---------------------------------------------------------------------- | :----------------------------------- |
| A result failed verification (FR-07); written after the complete report | `dp-sort-bench: verification failed` |
| Standard output cannot be written (other than a broken pipe)            | `dp-sort-bench: write error`         |

## 7. Verification

| Method                                                                                | Applies to                                |
| :------------------------------------------------------------------------------------ | :---------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                    | FR-01 … FR-08, FR-10, FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 05 … 10 have several steps) | FR-01 … FR-08, FR-10 … FR-14              |
| Unit test (written by the implementer)                                                | FR-02, FR-04 … FR-07, NFR-06              |
| Measurement                                                                           | NFR-03                                    |
| Inspection / review / demonstration                                                   | FR-09, NFR-02, NFR-04, NFR-05, NFR-08     |

The project has no fixture files: the tool reads no input.

Public test map:

| Test | Command                                | Verifies                             |
| :--- | :------------------------------------- | :----------------------------------- |
| 01   | `dp-sort-bench`                        | FR-01 (default sizes), FR-02 … FR-08 |
| 02   | `dp-sort-bench --sizes=10,20,40`       | FR-01, FR-02, FR-06, FR-08           |
| 03   | `dp-sort-bench -s 100 --seed=7`        | FR-01, FR-10                         |
| 04   | `dp-sort-bench --sizes 0,1,2,3`        | FR-02, FR-04 … FR-06 (edge sizes)    |
| 05   | `dp-sort-bench -s 8 --seed 4294967295` | FR-10 (largest seed)                 |
| 06   | `dp-sort-bench --help`                 | FR-11                                |
| 07   | `dp-sort-bench --sizes=100001`         | FR-01, FR-13                         |
| 08   | `dp-sort-bench -s 10,,20`              | FR-01, FR-13                         |
| 09   | `dp-sort-bench --seed=-1`              | FR-10, FR-13                         |
| 10   | `dp-sort-bench extra`                  | FR-13, FR-14                         |

## 8. Traceability (URD → SRS)

| User requirement | System requirements          |
| :--------------- | :--------------------------- |
| UR-01            | FR-01, FR-08                 |
| UR-02            | FR-01                        |
| UR-03            | FR-02, FR-03, FR-10, CONV-38 |
| UR-04            | FR-04, FR-05, FR-06, NFR-05  |
| UR-05            | FR-02, FR-08, NFR-01, NFR-02 |
| UR-06            | FR-06, FR-08                 |
| UR-07            | FR-07                        |
| UR-08            | FR-09, NFR-02, CONV-35       |
| UR-09            | FR-11, FR-12                 |
| UR-10            | FR-13, FR-14                 |
| UR-11            | NFR-01, NFR-02, CONV-03      |
| UR-12            | FR-13, CLI-CONV              |
| UR-13            | NFR-03, NFR-07               |

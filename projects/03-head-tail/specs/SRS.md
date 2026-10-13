# Software Requirements Specification (SRS) — dp-head, dp-tail

| Field | Value |
| :-- | :-- |
| Document ID | SRS-03 |
| Project | `03-head-tail` — Stream Slicing Utility |
| Products | `dp-head`, `dp-tail` (canonical names) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-03) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-head` and `dp-tail`. It is
complete and precise enough that independent implementations in any programming language
produce **byte-identical** output for every invocation. It is the authoritative source for
design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-head` copies a leading slice of each input to standard output; `dp-tail` copies a trailing
slice, and can then follow regular files as they grow. Both read files named as operands, or
standard input. The two tools share their number syntax, header rules, and error handling, and
are specified together. Requirements that apply to one tool name it; all others apply to both.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| CR | The carriage-return byte, `0x0D` |
| Input | The byte sequence read from one operand (a file, or standard input) |
| Line | A maximal run of bytes in an input that ends with LF and includes it; additionally, if the input is non-empty and its last byte is not LF, the bytes after the last LF (or the whole input when it contains no LF) form a final line without a terminator. An empty input has zero lines. |
| NUM | The value of `-n`/`--lines` or `-c`/`--bytes`, with grammar in FR-03 |
| COUNT | The non-negative integer denoted by NUM after any suffix is applied |
| SIGN | The optional leading `-` (dp-head) or `+`/`-` (dp-tail) of NUM |
| Unit | Lines when the winning amount option is `-n`/`--lines`; bytes when it is `-c`/`--bytes` |
| Header | The bytes `==> ` + NAME + ` <==` + LF, where NAME is the display name |
| Display name | `standard input` for the operand `-` (and for the implicit standard input when there are no operands); otherwise the operand exactly as given (CONV-19) |
| Seekable regular file | An opened input that the operating system reports as a regular file and whose read position can be changed |
| Followed file | An input that `dp-tail -f` keeps watching after the initial output (FR-11) |
| Poll | One wait-and-check cycle of follow mode (FR-12) |
| B | An implementation-chosen, fixed I/O block size of at least 512 bytes and at most 1 MiB |

### 1.4 References
- URD-03: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains both normative help texts)
- POSIX.1-2017 `head` and `tail` utilities; GNU coreutils `head(1)`/`tail(1)` (informative:
  the semantics below follow GNU where it is sensible, with the differences listed in §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-head` and `dp-tail` are two standalone executables built from one project. Their interfaces
are the command line, the named files, standard input, standard output, standard error, and the
exit status.

### 2.2 Product functions
1. Print the first N lines or bytes of each input, or all but its last N (`dp-head`).
2. Print the last N lines or bytes of each input, or everything from line or byte N (`dp-tail`).
3. Label each input with a header when several are processed, or as requested.
4. Follow regular files and print appended data, forever or for a fixed number of polls
   (`dp-tail -f`).
5. Display help and version information; detect and report usage and file errors.

### 2.3 Constraints
- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior and resource use.

### 2.4 Assumptions
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Inputs are arbitrary bytes. No encoding is assumed and none is validated.

### 2.5 Deliberate differences from GNU coreutils (informative)
- Diagnostics use the CLI-CONV formats, not GNU's wording (for example, an invalid count is
  `invalid argument`, not `invalid number of lines`).
- Only the suffixes `K`, `M`, and `G` (binary multiples) are accepted (FR-03).
- The obsolete forms `dp-head -5` and `dp-tail +5` are not supported: `-5` is an unknown option
  (CONV-13) and `+5` is a file operand.
- `-f` follows by open descriptor only; there is no `-F`, `--retry`, `--pid`, or `-z`.
- `--max-polls` is specific to this curriculum.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-head [-n [-]NUM | -c [-]NUM] [-q | -v] [FILE]...
dp-tail [-n [+]NUM | -c [+]NUM] [-q | -v] [-f [-s SECONDS] [--max-polls=N]] [FILE]...
dp-head --help | --version
dp-tail --help | --version
```

### 3.2 Options

`dp-head`:

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-n` | `--lines` | `[-]NUM` (required) | `10` | Slice by lines (FR-04) |
| `-c` | `--bytes` | `[-]NUM` (required) | — | Slice by bytes (FR-04) |
| `-q` | `--quiet` | none | — | Never print headers (FR-06) |
| `-v` | `--verbose` | none | — | Always print headers (FR-06) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

`dp-tail`:

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-n` | `--lines` | `[+]NUM` (required) | `10` | Slice by lines (FR-05) |
| `-c` | `--bytes` | `[+]NUM` (required) | — | Slice by bytes (FR-05) |
| `-f` | `--follow` | none | off | Follow regular files after the initial output (FR-11) |
| `-s` | `--sleep-interval` | SECONDS (required) | `1` | Wait between polls (FR-12) |
| — | `--max-polls` | N (required) | unlimited | Stop after N polls (FR-12) |
| `-q` | `--quiet` | none | — | Never print headers (FR-06) |
| `-v` | `--verbose` | none | — | Always print headers (FR-06) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, attached values, `--name=value`, `--`, repetition, and scan order)
follows CONV-07 … CONV-12. A value is always taken from the next token when it is not attached,
even if it begins with `-`: `dp-head -n -3` means `-n` with value `-3`. `-n` and `-c` are two
spellings of one setting, as are `-q` and `-v`; see FR-03 and FR-06.

### 3.3 Operands
Zero or more FILE operands, processed in the order given. With no operands, each tool reads
standard input exactly as if the single operand `-` had been given. The operand `-` means
standard input (CONV-10) wherever it appears; tokens after `--` are operands even when they
begin with `-`.

### 3.4 Standard input
Read when there are no operands or for each `-` operand (CONV-26). When `-` occurs more than
once, the first occurrence reads standard input as specified; what later occurrences see is
unspecified, except that it is empty when an earlier occurrence read standard input to its end.

### 3.5 Standard output
Headers (FR-06), the slices of the inputs in operand order (FR-04, FR-05), and in follow mode
the appended data (FR-12). Nothing else. Data bytes are copied unchanged (FR-02).

### 3.6 Standard error
Diagnostics only (§6). Nothing on success.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every operand was processed successfully, or `--help` / `--version` was handled |
| 1 | At least one operand could not be opened or read (FR-09), including a read failure during follow mode |
| 2 | Usage error (FR-10); nothing was read and nothing was written to standard output |

`dp-tail -f` without `--max-polls` never terminates on its own while at least one file is
followed (FR-12); its status when terminated by a signal is unspecified.

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
Examples use the fixture `lines.txt`, whose content is the 15 lines `line 1` … `line 15`, each
ending in LF.

**FR-01: Inputs and order.**
Each tool MUST process its operands one at a time in command-line order, writing the output for
an operand completely before opening the next one. With no operands it MUST process standard
input as the single operand `-`.
*AC:* `dp-tail -n 1 < lines.txt` → `line 15\n`, exit 0. *(UR-08)*

**FR-02: Lines and byte transparency.**
Lines are as defined in §1.3: only LF terminates a line; CR is ordinary data, so a CRLF line
ends at its LF and the CR stays part of it. A final run of bytes without LF counts as a line.
Every byte written from an input MUST be copied unchanged (CONV-04); the tools MUST NOT add,
remove, or translate any byte of a slice, and in particular MUST NOT append an LF to a final
line that lacks one.
*AC:* for an input `one\ntwo\nthree` (no final LF), `dp-tail -n 2` → `two\nthree` and
`dp-head -n -1` → `one\ntwo\n`; for `first\r\nsecond\r\nthird\r\n`, `dp-head -c -7` →
`first\r\nsecond\r\n`. *(UR-12)*

**FR-03: NUM syntax and unit selection.**
NUM MUST match `[SIGN]DIGITS[SUFFIX]`, where:
- SIGN is optional. For `dp-head` the only allowed sign is `-`. For `dp-tail` the allowed signs
  are `+` and `-`.
- DIGITS is one or more ASCII digits `0`–`9`. Leading zeros are allowed (`007` is 7).
- SUFFIX is optional and is exactly one of the uppercase letters `K` (×1024), `M` (×1048576), or
  `G` (×1073741824). No other suffix, lowercase letter, `B`, space, or decimal point is
  accepted.
- COUNT, the value of DIGITS multiplied by the suffix, MUST NOT exceed 9223372036854775807
  (2^63 − 1).

Any other value (including the empty string, a lone sign, `+` given to `dp-head`, and a value
whose COUNT exceeds the maximum) MUST be reported as the usage error
`<tool>: invalid argument '<NUM>' for '<option>'` (CONV-13), where `<option>` is `-n`,
`--lines`, `-c`, or `--bytes` exactly as written for the winning occurrence.

`-n`/`--lines` and `-c`/`--bytes` are one setting: the last occurrence of any of the four
spellings wins (CONV-11) and determines both the unit and NUM. Only the winning value is
validated. With none of them given, the unit is lines and COUNT is 10 with no sign.
*AC:* `dp-head -n abc lines.txt` → stderr `dp-head: invalid argument 'abc' for '-n'` plus the
CONV-14 line, exit 2, stdout empty; `dp-head --lines=+3 lines.txt` → `invalid argument '+3' for
'--lines'`; `dp-head --bytes=1K short.txt` prints the whole 17-byte file; `dp-head -n 9 -c 3`
slices 3 bytes. *(UR-03, UR-06, UR-14)*

**FR-04: dp-head slices.**
For each input, `dp-head` MUST write exactly the following bytes:

| Unit | SIGN | Output |
| :-- | :-- | :-- |
| lines | none | The first COUNT lines; the whole input if it has COUNT lines or fewer. COUNT 0 writes nothing. |
| lines | `-` | Every line except the last COUNT lines; nothing if the input has COUNT lines or fewer. `-0` writes the whole input. |
| bytes | none | The first min(COUNT, size) bytes. |
| bytes | `-` | The first max(0, size − COUNT) bytes. |

A slice of lines always consists of whole lines as defined in §1.3, so the final unterminated
line is included or excluded as a unit.
*AC:* `dp-head lines.txt` → `line 1` … `line 10`; `dp-head -n 3 lines.txt` → `line 1` …
`line 3`; `dp-head -n -12 lines.txt` → `line 1` … `line 3`. *(UR-01, UR-03, UR-04)*

**FR-05: dp-tail slices.**
For each input, `dp-tail` MUST write exactly the following bytes:

| Unit | SIGN | Output |
| :-- | :-- | :-- |
| lines | none or `-` | The last COUNT lines; the whole input if it has COUNT lines or fewer. COUNT 0 writes nothing. |
| lines | `+` | Everything from the start of line COUNT (lines numbered from 1) to the end of the input; nothing if the input has fewer than COUNT lines. `+0` is the same as `+1` (the whole input). |
| bytes | none or `-` | The last min(COUNT, size) bytes. |
| bytes | `+` | Everything from byte COUNT (bytes numbered from 1) to the end; nothing if size < COUNT. `+0` is the same as `+1`. |

The `-` sign is accepted for symmetry and means the same as no sign.
*AC:* `dp-tail lines.txt` → `line 6` … `line 15`; `dp-tail -c 20 lines.txt` →
` 13\nline 14\nline 15\n`; `dp-tail -n +13 lines.txt` → `line 13` … `line 15`;
`dp-tail -c +5 short.txt` (content `alpha\nbeta\ngamma\n`) → `a\nbeta\ngamma\n`; `dp-tail -n 5
short.txt` → the whole file. *(UR-02, UR-03, UR-05)*

**FR-06: Headers.**
Headers are *enabled* according to the last of `-q`/`--quiet` and `-v`/`--verbose` given:
`-q`/`--quiet` disables them, `-v`/`--verbose` enables them. When neither is given, headers are
enabled exactly when there are two or more operands (counting every operand, including ones that
later fail and repeated ones). When headers are enabled:
- After an operand is opened successfully and before any of its data is read or written, the
  tool MUST write its header. The header is written even when the slice is empty.
- Every header except the first one written by the process MUST be preceded by one extra LF,
  producing a blank line between consecutive files' output. An operand that fails to open
  writes no header and does not count as "first".
- The display name of standard input is `standard input`.

*AC:* `dp-head -n 2 lines.txt short.txt` →
`==> lines.txt <==\nline 1\nline 2\n\n==> short.txt <==\nalpha\nbeta\n`;
`dp-head -v -c 5 - < short.txt` → `==> standard input <==\nalpha`;
`dp-tail -v -q -n 1 lines.txt short.txt` → `line 15\ngamma\n`. *(UR-07)*

**FR-07: Output for a short input.**
When an input has fewer lines or bytes than requested, the tools MUST write what the tables in
FR-04 and FR-05 specify (the whole input, or nothing) without any diagnostic, and this MUST NOT
affect the exit status.
*AC:* `dp-tail -n 5 short.txt` → `alpha\nbeta\ngamma\n`, stderr empty, exit 0. *(UR-03)*

**FR-08: Reading strategy.**
On a seekable regular file (including standard input redirected from one), the slice is taken
relative to the file's read position when it is opened and the file's end. Specifically:
- `dp-tail` with unit lines and no `+` MUST locate the start of the slice by reading backwards
  from the end of the file in blocks of B bytes, stopping as soon as the start is found, and
  then copy forwards from there to the end of the file.
- `dp-tail` with unit bytes and no `+` MUST position directly at max(start, size − COUNT).
- `dp-head` with SIGN `-` MUST compute the cut point from the end in the same ways (backwards
  block scan for lines, size arithmetic for bytes) and copy from the start up to it.

On any other input (pipe, terminal, character device) the tools read sequentially:
- `dp-tail` without `+` MUST retain only a bounded ring buffer holding the most recent COUNT
  lines (unit lines) or COUNT bytes (unit bytes), and write it at end of input.
- `dp-head` with SIGN `-` MUST write data as soon as it is known not to belong to the last COUNT
  lines or bytes, retaining at most that many.

`dp-head` without a sign MAY stop reading an input once its slice is complete.
*AC:* inspection of the design; the NFR-02/NFR-03 demonstration. The observable output is the
same for both strategies (FR-04, FR-05). *(UR-11)*

**FR-09: File errors.**
If an operand cannot be opened, or reading it fails, the tool MUST write
`<tool>: <name>: <reason>` to standard error, where `<name>` is the display name (`standard
input` for `-`) and `<reason>` is the CONV-16 fixed text. A directory operand reports
`Is a directory`. The tool MUST then continue with the next operand (CONV-17) and finally exit
with status 1. Bytes already written for the failing operand (its header, and any data read
before a read failure) remain written.
*AC:* `dp-head -n 1 missing.txt short.txt` → stdout `==> short.txt <==\nalpha\n`, stderr
`dp-head: missing.txt: No such file or directory`, exit 1. *(UR-13)*

**FR-10: Usage errors.**
Unknown options, missing option values, values given to flags, and invalid values MUST be
reported with the CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options
MUST NOT be abbreviated. In addition to FR-03, `dp-tail` validates (only the winning occurrence
of each, and whether or not `-f` is given):
- SECONDS for `-s`/`--sleep-interval`: MUST match `DIGITS` or `DIGITS.DIGITS` (ASCII digits
  only, at least one on each side of the point) with a value of at most 86400.
- N for `--max-polls`: MUST be one or more ASCII digits with a value of at most
  9223372036854775807. 0 is allowed.

Obsolete numeric options such as `-5` are unknown options (`invalid option -- '5'`).
*AC:* `dp-tail -n +x lines.txt` → `dp-tail: invalid argument '+x' for '-n'`; `dp-tail -f -s
1.5.2 lines.txt` → `dp-tail: invalid argument '1.5.2' for '-s'`; each exits 2 with empty stdout.
*(UR-14, UR-17)*

**FR-11: Follow mode eligibility (dp-tail).**
With `-f`/`--follow`, after the initial output for all operands (FR-01 … FR-09), `dp-tail` MUST
follow every operand that (a) is not `-`, (b) opened and was read successfully, and (c) is a
seekable regular file. Standard input is never followed, whether it is a pipe, a terminal, or a
redirected regular file; this is silent. Operands that failed, directories, pipes, and devices
are not followed. If no operand is followed, `dp-tail` MUST NOT poll or wait and exits
immediately after the initial output. Without `-f`, the options `-s` and `--max-polls` are
validated (FR-10) but have no effect.
*AC:* `dp-tail -f --max-polls 1 -s 0 -n 2 < lines.txt` → `line 14\nline 15\n`, exit 0, with no
waiting. *(UR-09)*

**FR-12: Polling (dp-tail).**
Each followed file has a *position*, initially the offset just after the last byte the initial
output read (the end of the file at that time). Follow mode then repeats polls. One poll MUST:
1. flush standard output, then wait SECONDS seconds (no wait when SECONDS is 0);
2. visit the followed files in operand order, and for each one, if its current size is greater
   than its position, copy the bytes from the position to the current end of the file to
   standard output (FR-13 for headers) and set the position to the new end.

Without `--max-polls`, polls repeat for as long as at least one file is followed. With
`--max-polls=N`, exactly N polls are performed (none when N is 0), after which the tool exits
with the status of §3.7: 0 if every operand and poll succeeded, 1 otherwise. If reading a
followed file fails during a poll, the tool MUST report it as in FR-09 (exit status 1) and stop
following that file. The followed file is the one opened for the initial output (following by
descriptor); renaming or replacing the path is not detected.
*AC:* `dp-tail -f --max-polls 1 -s 0 lines.txt` → `line 6` … `line 15`, exit 0;
`dp-tail -f --max-polls 2 -s 0 -n 1 lines.txt missing.txt short.txt` → stdout
`==> lines.txt <==\nline 15\n\n==> short.txt <==\ngamma\n`, stderr
`dp-tail: missing.txt: No such file or directory`, exit 1. *(UR-09, UR-10)*

**FR-13: Follow headers and truncation (dp-tail).**
When headers are enabled (FR-06) and a poll is about to write appended data for a followed file
other than the file whose header was written most recently, the tool MUST first write that
file's header (preceded by an LF, per FR-06). If a followed file's current size is less than
its position, the tool MUST write `dp-tail: <name>: file truncated` to standard error, set the
position to 0, and then apply step 2 of FR-12. This message does not change the exit status.
*AC:* inspection and implementer unit tests (appending to a file during a run cannot be
expressed in the black-box harness). *(UR-09)*

**FR-14: Help.**
`--help` MUST write the tool's help text from user-manual §"HELP OUTPUT" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12.
*AC:* `dp-head --help` and `dp-tail --help` match the manual exactly. *(UR-15)*

**FR-15: Version.**
`--version` MUST write `dp-head (dialectic-playground) 1.0.0` or
`dp-tail (dialectic-playground) 1.0.0`, followed by LF, and exit 0 (CONV-02).
*AC:* exact match. *(UR-15)*

**FR-16: Error atomicity.**
All usage errors MUST be detected before any operand is opened or anything is written to
standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-14)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output MUST be byte-identical on Linux, macOS, and Windows. Generated line terminators (headers, diagnostics, help) MUST be LF only, and standard output MUST be written in binary mode so copied CR and LF bytes are never translated (CONV-03, CONV-04). | CI black-box tests on 3 OSes |
| NFR-02 | Memory | Memory used for input data MUST be independent of the input size. It MUST be bounded by B for every mode on a seekable regular file and for `dp-head` without a sign and `dp-tail` with `+` on any input; by COUNT + B bytes for `dp-head -c -NUM` and `dp-tail -c NUM` on non-seekable input; and by the total length of the COUNT (or COUNT + 1) most recent lines plus B for `dp-head -n -NUM` and `dp-tail -n NUM` on non-seekable input. No mode may read a whole input into memory. | Inspection; demonstration on a ≥ 4 GiB file |
| NFR-03 | Performance | On a seekable regular file, `dp-tail` without `+`, and `dp-head` with SIGN `-` when locating the cut point, MUST NOT read the file sequentially from the start: time to locate the slice depends on the slice size, not the file size (FR-08). `dp-tail -n 10` on a 4 GiB file MUST complete in under 1 second on CI hardware. | Demonstration |
| NFR-04 | Large files | All offsets, sizes, and counts MUST be handled as 64-bit quantities: files larger than 4 GiB and COUNT values up to 2^63 − 1 MUST work on every platform. | Inspection; unit tests |
| NFR-05 | Determinism | With `--max-polls`, follow mode MUST terminate after exactly the specified number of polls; output MUST not depend on timing when files do not change. | Black-box tests |
| NFR-06 | Robustness | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input (CONV-24). A broken output pipe terminates them quietly (CONV-25). | Unit + black-box tests |
| NFR-07 | Maintainability | Option parsing, NUM parsing, header logic, slicing strategies, and follow mode MUST be separate units, and logic common to both tools MUST be shared rather than duplicated. | Design review |
| NFR-08 | Testability | The slicing functions MUST be testable on in-memory streams with a configurable block size, so block-boundary cases (a LF exactly at a block edge, lines longer than B) are unit-tested. | Code review |
| NFR-09 | Build | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-10 | Security | The tools MUST read only the files named as operands (and standard input), MUST NOT write any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2) are each followed by `Try '<tool> --help' for more information.`,
where `<tool>` is `dp-head` or `dp-tail`.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (including digits, e.g. `-5`) | `<tool>: invalid option -- 'x'` |
| Unknown long option token `T` | `<tool>: unrecognized option 'T'` |
| `-n` / `-c` without a value (both tools); `-s` without a value (dp-tail) | `<tool>: option requires an argument -- 'n'` (or `'c'`, `'s'`) |
| `--lines` / `--bytes` without a value; `--sleep-interval` / `--max-polls` without a value (dp-tail) | `<tool>: option '--lines' requires an argument` (or `'--bytes'`, `'--sleep-interval'`, `'--max-polls'`) |
| `=value` given to a flag: `--quiet`, `--verbose`, `--help`, `--version`; `--follow` (dp-tail) | `<tool>: option '--quiet' doesn't allow an argument` (or the flag's name) |
| Invalid NUM `V` (FR-03) | `<tool>: invalid argument 'V' for '-n'` (or `'--lines'`, `'-c'`, `'--bytes'`, as written) |
| Invalid SECONDS `V` (dp-tail, FR-10) | `dp-tail: invalid argument 'V' for '-s'` (or `'--sleep-interval'`) |
| Invalid N `V` (dp-tail, FR-10) | `dp-tail: invalid argument 'V' for '--max-polls'` |

Runtime diagnostics (no CONV-14 line):

| Trigger | Exact line | Effect on exit status |
| :-- | :-- | :-- |
| Operand cannot be opened or read | `<tool>: <name>: <reason>` with the CONV-16 reason | 1 |
| Followed file shrank below its position (dp-tail -f) | `dp-tail: <name>: file truncated` | none |

`<name>` is the display name: the operand as given, or `standard input` for `-`.

### 6.1 Deviations from and extensions to CLI-CONV

| CLI-CONV item | This SRS |
| :-- | :-- |
| CONV-11 | `-n`/`--lines`/`-c`/`--bytes` are one setting (last wins across all four spellings); `-q`/`--quiet` and `-v`/`--verbose` are one setting (last wins). |
| CONV-16 | For standard input, `<path>` is the display name `standard input` rather than `-`. |
| CONV-16, CONV-18 | Adds the informational runtime diagnostic `file truncated`, which does not affect the exit status. |
| CONV-18 | `dp-tail -f` without `--max-polls` does not exit on its own. |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01, FR-03 … FR-06, FR-09, FR-11, FR-12 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-02, FR-03, FR-05 … FR-07, FR-09 … FR-12 |
| Black-box (checked by `check-curriculum.py`) | FR-14 |
| Unit test (written by the implementer) | FR-02 … FR-05, FR-08, FR-13, NFR-04, NFR-08 |
| Inspection / review / demonstration | FR-08, FR-13, NFR-02, NFR-03, NFR-07, NFR-10 |

Fixtures (`tests/fixtures/`): `lines.txt` (`line 1` … `line 15`, LF-terminated), `short.txt`
(`alpha\nbeta\ngamma\n`), `nonl.txt` (`one\ntwo\nthree`, no final LF), `crlf.txt`
(`first\r\nsecond\r\nthird\r\n`).

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-head lines.txt` | FR-04 (default 10 lines) |
| 02 | `dp-tail lines.txt` | FR-05 (default 10 lines) |
| 03 | `dp-head -n 3 lines.txt` | FR-03, FR-04 |
| 04 | `dp-tail -c 20 lines.txt` | FR-03, FR-05 |
| 05 | `dp-head -n -12 lines.txt` | FR-04 (all but last N) |
| 06 | `dp-tail -n +13 lines.txt` | FR-05 (from line N) |
| 07 | `dp-head -n 2 lines.txt short.txt` | FR-06 |
| 08 | `dp-tail -n 1 < lines.txt` | FR-01 (standard input) |
| 09 | `dp-head -n 1 missing.txt short.txt` | FR-06, FR-09 |
| 10 | `dp-tail -f --max-polls 1 -s 0 lines.txt` | FR-11, FR-12 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-04 |
| UR-02 | FR-05 |
| UR-03 | FR-03, FR-04, FR-05, FR-07 |
| UR-04 | FR-04 |
| UR-05 | FR-05 |
| UR-06 | FR-03 |
| UR-07 | FR-06, FR-13 |
| UR-08 | FR-01, §3.3, §3.4 |
| UR-09 | FR-11, FR-12, FR-13 |
| UR-10 | FR-12, NFR-05 |
| UR-11 | FR-08, NFR-02, NFR-03, NFR-04 |
| UR-12 | FR-02, NFR-01 |
| UR-13 | FR-09, §3.7 |
| UR-14 | FR-03, FR-10, FR-16 |
| UR-15 | FR-14, FR-15 |
| UR-16 | NFR-01, CONV-03 |
| UR-17 | FR-10, §6.1, CLI-CONV |
| UR-18 | NFR-09 |

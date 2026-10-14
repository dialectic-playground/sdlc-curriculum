# Software Requirements Specification (SRS) — dp-echo

| Field | Value |
| :-- | :-- |
| Document ID | SRS-01 |
| Project | `01-echo` — Stream Echo & Formatting |
| Product | `dp-echo` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-01) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0), with the overrides listed in §2.5 |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-echo`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope
`dp-echo` writes its operands to standard output, separated by single spaces and followed by a
line feed. Options suppress the line feed and enable the interpretation of backslash escape
sequences. The tool reads no input, touches no files, and has no usage errors: every argument
list is valid.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| CR | The carriage-return byte, `0x0D` |
| CRLF | The two-byte sequence `0x0D 0x0A` |
| SP | The space byte, `0x20` |
| Backslash | The byte `0x5C` (`\`) |
| Argument | One element of the command-line argument list after the program name, as text (CONV-05) |
| Option token | An argument consisting of `-` followed by one or more of the letters `n`, `e`, `E` (FR-02) |
| Operand | Every argument from the first argument that is not an option token to the end of the list (FR-02) |
| Operand bytes | The UTF-8 encoding of an operand, exactly as given (CONV-05) |
| Escape mode | The state in which backslash escape sequences are interpreted (FR-04) |
| Octal digit | One of the bytes `0`–`7` (`0x30`–`0x37`) |
| Hex digit | One of the bytes `0`–`9`, `a`–`f`, `A`–`F` |

### 1.4 References
- URD-01: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- POSIX.1-2017, `echo` utility (XSI escape sequences); GNU coreutils `echo` (option handling).
  These are informative background only; where they differ from this SRS, this SRS governs.

## 2. Overall description

### 2.1 Product perspective
`dp-echo` is a standalone executable. Its interfaces are the command line, standard output,
standard error, and the exit status. It is the second of the fifty-three curriculum projects and
the first whose argument syntax deliberately departs from the common conventions, because `echo`
exists to print arbitrary text, including text that looks like options.

### 2.2 Product functions
1. Write the operands to standard output, separated by single spaces.
2. Terminate the output with a single LF, unless `-n` is given.
3. Interpret backslash escape sequences when `-e` is in effect, including `\c` to stop output.
4. Display help and version information.
5. Report a failure to write standard output.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Implementations MUST NOT delegate to a shell built-in `echo`, the system `echo` program, or any
  other external program (NFR-07): their behavior varies between platforms.

### 2.4 Assumptions
- The terminal or consumer accepts UTF-8.
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.

### 2.5 Deliberate overrides of CLI-CONV
CLI-CONV applies in full except for the following, which this SRS replaces for `dp-echo`
(as CLI-CONV §3 anticipates):

| CLI-CONV clause | Override for `dp-echo` | Requirement |
| :-- | :-- | :-- |
| CONV-07 … CONV-11 (option syntax) | Only *leading* option tokens (`-` followed by one or more of `n`, `e`, `E`) are options. There are no long options apart from FR-03. `--` is not a terminator and is printed. Options and operands are not interleaved: an option token after the first operand is an operand. Unknown options are not errors; they are operands. | FR-02 |
| CONV-12 (scan order for `--help`/`--version`) | `--help` and `--version` are recognized only when the argument list consists of exactly that one argument. In every other position they are printed as text. | FR-03 |
| CONV-13, CONV-14 (usage errors) | `dp-echo` has **no usage errors** and never exits with status 2. | FR-11 |
| CONV-22 (every tool accepts `--help`, `--version`) | Accepted only as the sole argument (FR-03); `--help=x` and `--version=x` are ordinary operands. | FR-03 |
| CONV-23 (help layout) | The help text has the standard layout plus two `or:` synopsis lines and an escape-sequence table after the option list. The text in the user manual is normative. | FR-12 |
| CONV-18 (exit status) | Status 1 means only "standard output could not be written" (FR-14); status 2 is never used. | §3.7 |

CONV-03 (LF-only generated line terminators) and CONV-05 (arguments emitted as their exact UTF-8)
apply unchanged and are central to this project (FR-06, FR-05, NFR-01).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-echo [-n] [-e | -E] [STRING]...
dp-echo --help
dp-echo --version
```

Option letters may be bundled into one token (`-ne`, `-neE`) and repeated in any order, but only
before the first STRING (FR-02).

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-n` | — | none | off | Do not write the trailing LF (FR-06) |
| `-e` | — | none | off | Enable escape mode (FR-04, FR-07) |
| `-E` | — | none | on | Disable escape mode (FR-04) |
| — | `--help` | none | — | Print the help text and exit 0; recognized only as the sole argument (FR-03) |
| — | `--version` | none | — | Print the version line and exit 0; recognized only as the sole argument (FR-03) |

### 3.3 Operands
Zero or more STRING operands. Any text is a valid operand, including the empty string and text
that begins with `-`.

### 3.4 Standard input
Not read (CONV-26).

### 3.5 Standard output
The output defined by FR-05 … FR-10, or the help text (FR-12), or the version line (FR-13).

### 3.6 Standard error
Empty, except for the single diagnostic of FR-14.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The output was written, or `--help` / `--version` was handled |
| 1 | Writing to standard output failed for a reason other than a broken pipe (FR-14) |

`dp-echo` never exits with status 2, because it has no usage errors (FR-11). After a broken
pipe the exit status is unspecified (CONV-25).

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, arguments are written in single quotes as a POSIX shell would take them:
a backslash inside single quotes is an ordinary character, so `'a\tb'` is the four characters
`a`, `\`, `t`, `b`. Output is written with C-style escapes (`\n` = LF, `\r` = CR, `\t` = tab).

**FR-01: Argument classification order.**
The tool MUST classify its argument list in this order:
1. If the list consists of exactly one argument and that argument is `--help`, apply FR-12.
2. Otherwise, if the list consists of exactly one argument and that argument is `--version`,
   apply FR-13.
3. Otherwise, split the list into option tokens and operands (FR-02) and produce the output
   (FR-05 … FR-10).

*AC:* `dp-echo --help` prints the help text; `dp-echo --help extra` prints `--help extra\n`.
*(UR-09, UR-12, UR-13, UR-14)*

**FR-02: Option tokens.**
Arguments MUST be examined from left to right. An argument is an *option token* if and only if
it is at least two characters long, its first character is `-`, and every following character is
one of `n`, `e`, `E` (case-sensitive). The tool MUST treat each leading option token as options,
applying its letters from left to right. The first argument that is not an option token, and
every argument after it, are operands, whatever they look like. In particular, each of the
following is an operand (not an option and not an error): `-` (no letters), `--`, `--help` and
`--version` when not the sole argument (FR-03), any `--…` token, `-x`, `-nx` (contains a letter
other than `n`, `e`, `E`), `-N`, the empty string, and any option token that follows an operand.
Bundling and repetition are allowed: `-ne` means `-n -e`, and `-nn` means `-n`.
*AC:* `dp-echo -- -n` → `-- -n\n`; `dp-echo - -x -n` → `- -x -n\n`;
`dp-echo -ne 'a\tb' -nx` → `a<TAB>b -nx` (no trailing LF). *(UR-09, UR-14)*

**FR-03: Help and version only as the sole argument.**
`--help` and `--version` MUST be recognized only when they are the entire argument list (FR-01).
In any other case they are classified by FR-02 and, since they are not option tokens, they and
everything after them are operands. `--help=…`, `--version=…`, and abbreviations such as `--he`
are never recognized and are always operands.
*AC:* `dp-echo --help extra` → `--help extra\n`, exit 0; `dp-echo -n --version` → `--version`
(no trailing LF), exit 0. *(UR-09, UR-12, UR-13)*

**FR-04: Option effects.**
- `-n` MUST suppress the trailing LF (FR-06). Repeating it has no further effect.
- `-e` MUST enable escape mode; `-E` MUST disable it. Escape mode is **off** by default.
- When both `-e` and `-E` occur among the option tokens, the letter that occurs **last** (in
  left-to-right order across all option tokens and within bundles) decides: `-e -E`, `-eE`, and
  `-Ee -E` disable escape mode; `-E -e` and `-Ee` enable it.

*AC:* `dp-echo -e -E 'a\nb'` → `a\nb` followed by LF (the backslash and `n` printed literally).
*(UR-02, UR-03, UR-04)*

**FR-05: Operand output.**
The tool MUST write, in order, the processed bytes of each operand, writing exactly one SP
between consecutive operands. Nothing is written before the first operand or after the last
apart from the trailing LF (FR-06). Outside escape mode, an operand's processed bytes are its
operand bytes, unchanged: backslashes, CR bytes, and every other character are copied verbatim
(CONV-05). In escape mode, they are the result of FR-07. An empty operand contributes no bytes,
but the separators around it are still written. Spaces inside an operand are preserved; spaces
between operands come only from the separator (the shell has already removed the original
spacing between words).
*AC:* `dp-echo hello   world` (two arguments) → `hello world\n`; `dp-echo '' ''` → ` \n` (one SP
then LF); `dp-echo 'Zoë' '日本語'` → the UTF-8 bytes of `Zoë 日本語` followed by LF.
*(UR-01, UR-04, UR-11)*

**FR-06: Trailing line feed — always LF, never CRLF.**
Unless `-n` is in effect, after the last operand (or immediately, when there are no operands) the
tool MUST write exactly one LF (`0x0A`). It MUST NOT write CR before it, on any platform,
including Windows (CONV-03); implementations on Windows MUST put standard output in binary mode
so the runtime does not translate LF to CRLF. With `-n`, nothing is written after the last
operand. Therefore `dp-echo` with no arguments writes a single LF, and `dp-echo -n` writes
nothing. A CR appears in the output **only** when the user supplies it, either in an operand or
through the `\r`, `\0015`, or `\x0d` escapes in escape mode; to emit a CRLF-terminated line, the
user writes `dp-echo -ne 'text\r\n'`.
*AC:* `dp-echo -n hello` → `hello` (5 bytes); `dp-echo -e 'windows\r\nline'` → `windows\r\nline\n`
(the only CR is the one requested). *(UR-02, UR-07, UR-08)*

**FR-07: Escape sequences.**
In escape mode, each operand MUST be processed independently, scanning its operand bytes from
left to right. A byte other than backslash is copied unchanged. A backslash that is the last byte
of the operand is copied unchanged (FR-10). Otherwise, the backslash and the byte that follows it
(the *escape letter*) form an escape sequence, interpreted by this table:

| Sequence | Output |
| :-- | :-- |
| `\\` | `0x5C` (one backslash) |
| `\a` | `0x07` (alert, BEL) |
| `\b` | `0x08` (backspace) |
| `\c` | Nothing; stop all output (FR-08) |
| `\e` | `0x1B` (escape) |
| `\f` | `0x0C` (form feed) |
| `\n` | `0x0A` (LF) |
| `\r` | `0x0D` (CR) |
| `\t` | `0x09` (horizontal tab) |
| `\v` | `0x0B` (vertical tab) |
| `\0` followed by 0–3 octal digits | One byte; see FR-09 |
| `\x` followed by 1–2 hex digits | One byte; see FR-09 |
| anything else | See FR-10 |

Escape letters are case-sensitive (`\N`, `\T`, `\E`, `\X` are not in the table). Scanning
resumes after the last byte consumed by the sequence. The bytes an escape produces are never
rescanned, and an escape sequence never spans two operands. Escapes are interpreted only in
operands, never in option tokens.
*AC:* `dp-echo -e 'col1\tcol2\nrow2'` → `col1\tcol2\nrow2\n` (a real tab and LF);
`dp-echo -e '\\n'` → `\n` as two characters (backslash, `n`) followed by LF;
`dp-echo -e '\e\a\b\f\v\\'` → bytes `1B 07 08 0C 0B 5C 0A`. *(UR-03, UR-11)*

**FR-08: Stopping output with `\c`.**
When escape mode processing reaches `\c`, the tool MUST write the bytes produced from that
operand before the `\c` and then write **nothing more**: not the rest of that operand, not any
further separator or operand, and not the trailing LF (even without `-n`). Bytes written before
the `\c` (earlier operands and their separators) remain written. The exit status is 0. Outside
escape mode, `\c` is ordinary text.
*AC:* `dp-echo -e 'one\c' two` → `one` (3 bytes); `dp-echo -e a 'b\cc' d` → `a b` (3 bytes).
*(UR-05)*

**FR-09: Numeric escapes.**
- `\0NNN`: after `\0`, the tool MUST take the longest run of **at most three** octal digits that
  immediately follows (possibly none). The output is one byte whose value is the octal number
  formed by those digits, or 0 when there are none, reduced modulo 256. Scanning resumes after
  the last digit taken. Examples: `\0` → `0x00`; `\0101` → `A`; `\01234` → `S` followed by the
  ordinary character `4`; `\08` → `0x00` followed by `8`; `\0777` → `0xFF`; `\0400` → `0x00`.
- `\xHH`: when at least one hex digit immediately follows `\x`, the tool MUST take the longest run
  of **at most two** hex digits (either case). The output is one byte with that hexadecimal value.
  Examples: `\x41` → `A`; `\x4a` and `\x4A` → `J`; `\x7` → `0x07`; `\x414` → `A` followed by `4`.
  When no hex digit follows `\x`, FR-10 applies.
- `\1` … `\7` (an octal digit other than `0` directly after the backslash) are **not** numeric
  escapes; FR-10 applies.
- Bytes produced by numeric escapes are written as-is, even when they do not form valid UTF-8
  (for example `\0377`, `\xff`).

*AC:* `dp-echo -e '\0101\x42\x4a\0|\x7|\0'` → bytes `41 42 4A 00 7C 07 7C 00 0A`;
`dp-echo -e '\01234|\0777|\0400'` → bytes `53 34 7C FF 7C 00 0A`. *(UR-06)*

**FR-10: Unknown escapes and a trailing backslash.**
In escape mode:
- If the escape letter is not in the FR-07 table, or is `x` not followed by a hex digit, the tool
  MUST write the backslash and the escape letter unchanged and resume scanning after the escape
  letter. When the byte after the backslash begins a multi-byte UTF-8 character, its remaining
  bytes are ordinary bytes, so the backslash and the whole character are written unchanged.
- A backslash that is the last byte of an operand MUST be written unchanged. (The separator and
  the next operand are not part of the escape.)

*AC:* `dp-echo -e 'a\qb\' 'c\x' 'd\8\1'` → `a\qb\ c\x d\8\1` followed by LF. *(UR-04, UR-14)*

**FR-11: No usage errors.**
Every argument list, including an empty one, MUST be accepted. The tool MUST NOT write any
diagnostic for any argument content and MUST NOT exit with status 2. Standard error is empty in
every case except FR-14.
*AC:* `dp-echo -x foo`, `dp-echo --bogus`, and `dp-echo --help=1` each print their arguments
followed by LF and exit 0 with empty standard error. *(UR-09, UR-10)*

**FR-12: Help.**
When `--help` is the sole argument (FR-01), the tool MUST write the help text from user-manual
§"Help output" byte-for-byte to standard output and exit 0.
*AC:* `dp-echo --help` matches the user manual exactly. *(UR-12)*

**FR-13: Version.**
When `--version` is the sole argument (FR-01), the tool MUST write
`dp-echo (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-13)*

**FR-14: Output failure.**
If writing to standard output fails because the reader has gone away (broken pipe), the tool MUST
terminate promptly without a diagnostic (CONV-25). If writing fails for any other reason (for
example, the device is full), the tool MUST write the diagnostic `dp-echo: write error` + LF to
standard error, write nothing further to standard output, and exit with status 1. The diagnostic
contains no operating-system message text. Bytes that were already delivered before the failure
are not retracted.
*AC:* on Linux, `dp-echo hi > /dev/full` writes `dp-echo: write error\n` to standard error and
exits 1. *(UR-10)*

**FR-15: Streaming.**
The tool MAY write its output incrementally (for example, operand by operand) or all at once; the
resulting byte stream MUST be the same. Because there are no usage errors, no validation has to
precede output. All output MUST be flushed before the tool exits.
*AC:* the output of every test is complete and identical whether standard output is a pipe or a
file. *(UR-01, UR-15)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability (cross-platform focus) | Output MUST be byte-identical on Linux, macOS, and Windows. The tool MUST generate only LF line terminators (FR-06, CONV-03) and MUST NOT translate LF to CRLF or CRLF to LF in either direction: a CR reaches the output only from an operand or an escape, and is never added or removed. Standard output MUST be in binary mode on Windows. | CI black-box tests on 3 OSes (public 04; hidden 02) |
| NFR-02 | Performance | Wall-clock run time MUST be under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware for argument lists up to the platform's command-line limit, with peak memory under 32 MiB. Processing time MUST be linear in the total length of the arguments. | Measurement |
| NFR-03 | Memory | Apart from the argument list itself, the tool MUST need at most O(L) additional memory, where L is the length of the longest single operand; it MUST NOT need to hold the complete output in memory. | Design review |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list, including empty arguments, arguments consisting only of backslashes, and numeric escapes producing NUL or non-UTF-8 bytes (CONV-24). | Unit + black-box tests |
| NFR-05 | Maintainability | Argument classification (FR-01 … FR-04), escape expansion (FR-07 … FR-10), and output writing MUST be separate units. | Design review |
| NFR-06 | Testability | Escape expansion MUST be a pure function from an operand's bytes to (output bytes, stop flag), covered by unit tests for every row of the FR-07 table and every example in FR-09 and FR-10. | Code review |
| NFR-07 | Security | The tool MUST read no files, no standard input, and no environment variables, and MUST run no subprocesses (in particular, no shell or system `echo`). | Inspection |
| NFR-08 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |

## 6. Diagnostics (complete list)

`dp-echo` has no usage errors (FR-11), so it never writes the CONV-14 `Try 'dp-echo --help'…`
line. Its only diagnostic is:

| Trigger | Exact message (one line on standard error) | Exit status |
| :-- | :-- | :-- |
| Standard output cannot be written, for a reason other than a broken pipe (FR-14) | `dp-echo: write error` | 1 |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-08, FR-12, FR-13, NFR-01 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-02 … FR-11, NFR-01, NFR-04 |
| Unit test (written by the implementer) | FR-02, FR-04, FR-07 … FR-10, NFR-06 |
| Manual test on Linux (`> /dev/full`) | FR-14 |
| Inspection / review | NFR-02, NFR-03, NFR-05, NFR-07 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-echo hello   world` | FR-05, FR-06 |
| 02 | `dp-echo -n hello` | FR-04, FR-06 |
| 03 | `dp-echo -e 'col1\tcol2\nrow2'` | FR-07 |
| 04 | `dp-echo -e 'windows\r\nline'` | FR-06, FR-07, NFR-01 |
| 05 | `dp-echo -e 'one\c' two` | FR-08 |
| 06 | `dp-echo -e -E 'a\nb'` | FR-04, FR-05 |
| 07 | `dp-echo -- -n` | FR-02, FR-11 |
| 08 | `dp-echo '' ''` | FR-05 |
| 09 | `dp-echo --help` | FR-01, FR-12 |
| 10 | `dp-echo --version` | FR-01, FR-13 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-05, FR-06, FR-15 |
| UR-02 | FR-04, FR-06 |
| UR-03 | FR-04, FR-07 |
| UR-04 | FR-04, FR-05, FR-10 |
| UR-05 | FR-08 |
| UR-06 | FR-09 |
| UR-07 | FR-06, NFR-01, CONV-03 |
| UR-08 | FR-06, FR-07, NFR-01 |
| UR-09 | FR-01, FR-02, FR-03, FR-11 |
| UR-10 | FR-11, FR-14, §3.7 |
| UR-11 | FR-05, FR-07, CONV-05 |
| UR-12 | FR-01, FR-03, FR-12 |
| UR-13 | FR-01, FR-03, FR-13 |
| UR-14 | §2.5, FR-01, FR-02, FR-10, CLI-CONV |
| UR-15 | FR-15, NFR-02, NFR-03 |
| UR-16 | NFR-08 |

# Software Requirements Specification (SRS) — dp-reverse

| Field | Value |
| :-- | :-- |
| Document ID | SRS-33 |
| Project | `33-reverse` — Two-Pointer In-Place Sequence Reversal |
| Product | `dp-reverse` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-33) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-reverse`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-reverse` reads strings — whitespace-free tokens, or whole lines with `-l`, `--lines` — from
standard input or from one file until the end of the input. Each string of at most 100
characters is reversed in place and written on one labelled line. Characters follow a fixed
UTF-8 rule, so multibyte characters stay intact; with `-b`, `--bytes`, bytes are reversed and
counted instead. The tool can write the textbook's prompt to standard error before each string
is read. It reports a string over the limit with its line number and unreadable files with
fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR, TAB | The bytes `0x0A`, `0x0D`, and `0x09` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Line | One of the byte sequences into which the input is divided by FR-03 |
| String | A token (word mode) or a line (line mode, `-l`) |
| Character, character length, byte length | As defined in FR-04 |
| Unit | The element that is reversed and counted: a character, or a byte when `-b` is given |
| *N* | The number of units of a string |
| Limit | 100 units |
| Complete string | A token whose terminating whitespace byte has been read, or a line whose LF has been read, or the last string of the input once the end of the input has been reached |

### 1.4 References
- URD-33: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- SRS-04 (`projects/04-wc/specs/SRS.md`) FR-06: the decoding rule that FR-04 restates
- SRS-27 (`projects/27-line-wrap/specs/SRS.md`) FR-04 and SRS-29
  (`projects/29-strlen/specs/SRS.md`) FR-05: the same character rule, word for word; SRS-29
  FR-04 divides lines by the same rule as FR-03
- The Unicode Standard, Version 15.0, §3.9, Table 3-7 "Well-Formed UTF-8 Byte Sequences"
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §6.5 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-reverse` is a standalone executable, related to the `rev` utility. Its interfaces are the
command line, standard input or the file named by its operand, standard output, standard error,
and the exit status. It belongs to the curriculum's applications-programming track
(Projects 11–52) and adapts §6.5 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.
It measures characters with the rule of `dp-wc -m` (Project 04), which `dp-wrap` (Project 27)
and `dp-strlen` (Project 29) also use.

### 2.2 Product functions
1. Read strings — tokens, or lines with `-l` — until the end of the input.
2. Check each string against the 100-unit limit.
3. Reverse each string in place, by characters or by bytes.
4. Write one labelled line per string as soon as the string has been read.
5. Optionally write the textbook's prompt to standard error before each string is read.
6. Report a string over the limit and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, and the design requirement of FR-07.
- Characters MUST be determined from the byte-level rule of FR-04. Library facilities whose
  results depend on locale or platform (locale-aware classification, multibyte-conversion
  functions, text-mode file reading) MUST NOT determine any character boundary (NFR-02).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-08.
- The input may contain any bytes and need not be valid UTF-8 or end with LF.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §6.5 prompts with `Enter a string:` and a tab, reads one string of up
to 100 characters with no embedded whitespace, reverses it in place with two pointers that
start at its first and last characters and move toward each other, swapping, until they meet,
and prints `Reversed string:`, a tab, and the result. `dp-reverse` keeps:

- the prompt text and the report label exactly, each with its tab;
- the definition of a string as a word without whitespace (the default, word mode);
- the limit of 100 characters;
- the in-place reversal with converging indices, and its O(1) extra space (FR-07).

It changes the following, for the reasons given:

- **Every string of the input is reversed.** The textbook reverses one string and stops.
  `dp-reverse` reads strings until the end of the input and writes one result per string
  (FR-08), so the same program serves a keyboard and a pipe; one string gives exactly the
  textbook's dialog.
- **Characters, not bytes.** The textbook swaps bytes, which turns every multibyte UTF-8
  character into invalid bytes. `dp-reverse` reverses characters, determined by the rule of
  `dp-wc -m` (FR-04), so `Zoë` becomes `ëoZ`; the limit is counted in the same characters.
  The reversal is still done in place in constant extra space (FR-07). `-b`, `--bytes` restores
  the textbook's byte reversal, for comparison.
- **The limit is enforced.** The textbook reads into a fixed array without checking the length,
  so a longer word overruns it. `dp-reverse` reports a string over the limit with its line
  number and stops (FR-05).
- **Whole lines on request.** With `-l`, `--lines`, each line is one string, spaces included
  (FR-03), as `rev` does.
- **Layout for redirected output.** The textbook's output contains blank lines that separated
  the result from the echoed keyboard input. They are dropped: standard output holds exactly
  one line per string (FR-08).
- **Prompts are optional and go to standard error.** With `-p`, `--prompt`, the textbook's
  prompt is written to standard error before each string is read (FR-09); without it, nothing
  is written but the results.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02, FR-03).

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Applies in word mode: the input is read as tokens (FR-02). In line mode the input is line-oriented (FR-03), and the CONV-32 line-number rule is used. |
| CONV-33 | Not applicable: no numbers are read. |
| CONV-34 | Applies, with one further message, `string exceeds 100 characters` (or `bytes`), and the default consequences (FR-05). |
| CONV-35 | Not applicable: no real numbers are written. |
| CONV-36 | Applies: `-p`, `--prompt` (FR-09). |
| CONV-37 | Applies: the input is *text data* in both modes (FR-02, FR-03). |
| CONV-38 | Not applicable: nothing is random. |

**Override of CONV-04:** the input is not copied; each string's units are written in reverse
order (FR-06). In line mode one CR at the end of a line is not part of the string (FR-03).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-reverse [-l | --lines] [-b | --bytes] [-p | --prompt] [FILE]
dp-reverse --help
dp-reverse --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-l` | `--lines` | none | off (word mode) | Read each line as one string (FR-03) |
| `-b` | `--bytes` | none | off (characters) | Reverse and count bytes instead of characters (FR-05, FR-06) |
| `-p` | `--prompt` | none | off | Write the prompt to standard error before each string is read (FR-09) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling such as `-lp`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. Giving a flag more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The result lines (FR-08), in input order. Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error
Prompts (FR-09, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The whole input was processed (including an input with no strings), or `--help` / `--version` was handled |
| 1 | A string exceeded the limit (FR-05), the input could not be opened or read (FR-10), or standard output could not be written |
| 2 | Usage error (FR-13) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\t` denotes TAB, `\r` denotes CR, and the files named
are the public fixtures in `tests/fixtures/`: `words.txt` is
`Antigravity\nHello 123456\nA ABCD ABCDE\nracecar\n`; `utf8.txt` is `Zoë naïve 日本語 🙂x\n`;
`lines.txt` is `Hello, World!\n\nstressed  desserts\n`; `toolong.txt` is `short\n`, then a
101-character word followed by ` fine\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
*AC:* `dp-reverse words.txt` and `dp-reverse - < words.txt` write the same lines. *(UR-01, UR-07)*

**FR-02: Strings in word mode.**
Without `-l`, the input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends
to the very end of the input is ignored. The remaining input is divided into tokens (CONV-32),
and each token, in order, is one string. Line structure has no meaning: strings may be
separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF
input. A `0x1A` byte followed by any other byte is ordinary data. Every string in word mode has
at least one byte.
*AC:* `dp-reverse words.txt` reverses the seven strings `Antigravity`, `Hello`, `123456`, `A`,
`ABCD`, `ABCDE`, and `racecar`; the hidden fixture `dos.txt` (`abc\r\ndef\r\n` and a final
`0x1A`) gives the two strings `abc` and `def`. *(UR-01, UR-09)*

**FR-03: Strings in line mode.**
With `-l`, `--lines`, each line is one string. The input is *text data* (CONV-37): a run of one
or more `0x1A` bytes that extends to the very end of the input is first removed. The remaining
bytes are divided at each LF: every LF ends one line, and the bytes after the last LF, if there
are any, form one more line. A line does not include its LF. If a line's last byte is CR, that
one CR is removed from the line (so a CR before an LF, or at the very end of the input, is not
part of the line); every other CR is part of the line. Every other byte, including NUL, TAB,
`0x1A` followed by more data, and every byte `0x80`–`0xFF`, is part of the line. Consequently:
an empty input, or one made only of `0x1A` bytes, has no lines; an input that ends with LF has
no empty last line; each empty line in the middle of the input is a line of length 0; and `\r`
alone forms a line of length 0.
*(The division into lines is word for word the same as SRS-29 FR-04.)*
The line number of a line is 1 plus the number of LF bytes before its first byte (CONV-32).
*AC:* `dp-reverse -l lines.txt` →
`Reversed string:\t!dlroW ,olleH\nReversed string:\t\nReversed string:\tstressed  desserts\n`;
the hidden fixture `crlf.txt` (`abc\r\n\r\n a b \r\nxyz\r`) gives the strings `abc`, the empty
string, ` a b `, and `xyz`. *(UR-02, UR-09)*

**FR-04: Characters and lengths.**
The *characters* of a byte sequence *b*[0] … *b*[*n*−1] are found by the following scan. Set
*p* = 0. While *p* < *n*: if the bytes starting at *b*[*p*] form a complete well-formed sequence
of length *k* — that is, *b*[*p*] … *b*[*p*+*k*−1] all exist in the sequence and match one row
of the table below — they are one character and *p* advances by *k*; otherwise the single byte
*b*[*p*] is one character and *p* advances by 1. The *character length* of the sequence is the
number of characters found; its *byte length* is *n*.

| Code points | Byte 1 | Byte 2 | Byte 3 | Byte 4 |
| :-- | :-- | :-- | :-- | :-- |
| U+0000..U+007F | `00`–`7F` | | | |
| U+0080..U+07FF | `C2`–`DF` | `80`–`BF` | | |
| U+0800..U+0FFF | `E0` | `A0`–`BF` | `80`–`BF` | |
| U+1000..U+CFFF | `E1`–`EC` | `80`–`BF` | `80`–`BF` | |
| U+D000..U+D7FF | `ED` | `80`–`9F` | `80`–`BF` | |
| U+E000..U+FFFF | `EE`–`EF` | `80`–`BF` | `80`–`BF` | |
| U+10000..U+3FFFF | `F0` | `90`–`BF` | `80`–`BF` | `80`–`BF` |
| U+40000..U+FFFFF | `F1`–`F3` | `80`–`BF` | `80`–`BF` | `80`–`BF` |
| U+100000..U+10FFFF | `F4` | `80`–`8F` | `80`–`BF` | `80`–`BF` |

This is the decoding rule of SRS-04 FR-06 (`dp-wc -m`), applied to one sequence. Consequences,
all normative: every valid UTF-8 code point counts 1; each byte of an invalid or truncated
sequence counts 1 (`E2 82 41` is three characters: two invalid bytes and `A`); overlong forms,
encoded surrogates, values above U+10FFFF, and lone continuation bytes count 1 per byte; a
sequence truncated by the end of the sequence counts 1 per byte present; a byte-order mark
(`EF BB BF`) is one ordinary character; NUL and every other control byte count 1. No display
width is involved: a TAB, a combining mark, and a wide East Asian character each count 1.
*(This requirement is word for word the same as SRS-27 FR-04 and SRS-29 FR-05.)*
In `dp-reverse`, the scan is applied to each string separately. The *units* of a string are its
characters, in order, or its bytes when `-b`, `--bytes` is given; *N* is their number.
*AC:* `utf8.txt` holds the strings `Zoë` (*N* = 3 characters, 4 bytes), `naïve` (5, 6), `日本語`
(3, 9), and `🙂x` (2, 5). *(UR-03, UR-04)*

**FR-05: Length limit.**
A string MUST have at most 100 units. If a string has more than 100 units, the tool MUST write
`dp-reverse: <source>:<line>: string exceeds 100 characters` (or, with `-b`,
`dp-reverse: <source>:<line>: string exceeds 100 bytes`), where `<source>` is as defined in
section 1.3 and `<line>` is the line number of the string (its first byte's line, CONV-32). The
string itself is not echoed. The tool then stops: it writes no result for that string, reads no
further input, and exits with status 1. Results already written for earlier strings are kept
(CONV-34). A string of exactly 100 units is accepted. In line mode the limit applies to the line
after the removal of FR-03.
*AC:* `dp-reverse toolong.txt` → stdout `Reversed string:\ttrohs\n`, stderr
`dp-reverse: toolong.txt:2: string exceeds 100 characters\n`, exit 1. A line of 100 `é`
characters (200 bytes) is accepted without `-b`, and reported as `string exceeds 100 bytes`
with `-b`. *(UR-05)*

**FR-06: Reversal.**
For a string with units *u*₁ … *u*_N, the reversed string MUST be *u*_N … *u*₁: the same units
in the opposite order, each unit keeping its own bytes in their original order. In character
mode every character, including each invalid byte, is one unit, so every well-formed sequence
stays intact and well-formed. In byte mode every byte is one unit, so the bytes of a multibyte
character come out in reverse order, which is not valid UTF-8; this is intended (UR-04). The
empty string reverses to the empty string, and a one-unit string to itself.
*AC:* `dp-reverse utf8.txt` → `ëoZ`, `evïan`, `語本日`, and `x🙂`; `dp-reverse -b utf8.txt`
→ the first result is the bytes `AB C3 6F 5A`; the hidden fixture `invalid.txt` maps
`41 E2 82 42` to `42 82 E2 41` and `é€🙂` to `🙂€é`. *(UR-03, UR-04)*

**FR-07: In-place reversal (design requirement).**
Each string MUST be reversed **in place**: in the storage that holds the string after it has
been read, by exchanging units with two indices that start at the two ends of the string and
move toward each other, one step per exchange, until they meet or cross. The auxiliary storage
used by the reversal MUST be a constant number of scalar variables, independent of *N*: the
string MUST NOT be copied into a second buffer, a reversed copy MUST NOT be built, and no
library function that reverses a sequence may be used. In byte mode, a string of *N* bytes is
reversed with exactly ⌊*N*/2⌋ exchanges. In character mode, where units have different sizes,
a suitable method is: first, scanning forward with the rule of FR-04, reverse the bytes of each
multibyte character in place with converging indices; then reverse the whole byte sequence with
converging indices. The result is FR-06's character reversal. Other in-place methods that use
constant auxiliary storage are permitted.
*AC:* design review of the reversal function; unit tests of NFR-06. *(UR-13)*

**FR-08: Output and streaming.**
For each string, in order, the tool MUST write one result line: the 17 bytes
`Reversed string:` + TAB, then the bytes of the reversed string (FR-06), then a single LF.
Nothing else is written to standard output: no blank lines, no echo of the input, no summary.
Strings MUST be processed one at a time: as soon as a string is complete (section 1.3) and
within the limit, the tool MUST write its result line and flush standard output, before it
waits for any further input bytes. When the end of the input is reached, the tool exits with
status 0. An input with no strings (empty, or only whitespace in word mode, or only a trailing
Ctrl-Z run) produces no output and exit status 0.
*AC:* `dp-reverse words.txt` → `Reversed string:\tytivargitnA\n`, then the results `olleH`,
`654321`, `A`, `DCBA`, `EDCBA`, `racecar` in the same format, exit 0. *(UR-01, UR-08)*

**FR-09: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 16 bytes
`Enter a string:` + TAB (no LF). With prompts enabled, the tool MUST write the prompt to
standard error, and flush standard error, immediately before each attempt to read a string:
once before the first string, and once after each result line has been written. A prompt is
therefore also written before the attempt that reaches the end of the input (CONV-36): an input
with *n* strings produces *n* + 1 prompts, and an input whose *k*-th string exceeds the limit
produces *k* prompts, the last followed directly by the diagnostic of FR-05 on the same line.
Prompts never change standard output. No prompt is written if the input cannot be opened.
*AC:* `dp-reverse --prompt < words.txt` → stdout as without `--prompt`, stderr
`Enter a string:\t` eight times with no LF, exit 0; `dp-reverse -p` with empty standard input
→ stderr `Enter a string:\t`, stdout empty, exit 0. *(UR-06)*

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-reverse: <source>: <reason>` with `<reason>` from the CONV-16 table,
and exit with status 1. Results already written are kept. When standard input fails,
`<source>` is `-`.
*AC:* `dp-reverse missing.txt` → stderr `dp-reverse: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-reverse subdir` where `subdir` is a directory →
`dp-reverse: subdir: Is a directory`. *(UR-07)*

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-reverse --help` matches the user manual exactly; `dp-reverse a b --help` also prints
it. *(UR-10)*

**FR-12: Version.**
`--version` MUST write `dp-reverse (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--lines=…`, `--bytes=…`,
`--prompt=…`, `--help=…`, `--version=…`), MUST be reported with the CONV-13 messages followed
by the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08):
`--line` is unrecognized. A second operand MUST be reported as
`dp-reverse: extra operand '<second operand>'`, after the whole argument list has been scanned
(CONV-12).
*AC:* `dp-reverse words.txt lines.txt` → `dp-reverse: extra operand 'lines.txt'`;
`dp-reverse -x --help` → `dp-reverse: invalid option -- 'x'`; `dp-reverse --prompt=yes` →
`dp-reverse: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case; `dp-reverse -p - extra < words.txt` writes no
prompt. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: character boundaries and line endings | Character boundaries MUST be computed from the byte-level rule of FR-04, never from the locale, the platform's default encoding or wide-character size (reversing 16-bit UTF-16 code units, as a naive reversal on Windows or in some runtimes would, splits `🙂` into two unpaired surrogates), or the console code page. The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer and the line divider, and a `0x1A` byte is never treated as end-of-file by the I/O layer. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03), and standard output MUST be flushed after each result line (FR-08). | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance | Processing 1 000 000 words (about 10 MiB of input) MUST take under 2 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the input: only the current string is held, in a buffer of at most 400 bytes (100 characters of at most 4 bytes), and reading a string stops as soon as it is known to exceed the limit. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement; code review |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including strings far longer than the limit, NUL bytes, and invalid UTF-8. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the tokenizer and line divider, the character scan of FR-04, the reversal of FR-07, output formatting, and I/O MUST be separate units. The reversal MUST be one function that operates on the string's storage in place. | Design review |
| NFR-06 | Testability | The reversal function MUST be a pure, I/O-free unit covered by unit tests: the empty string, one unit, even and odd lengths (`ABCD`, `ABCDE`), a palindrome, 100 units, strings mixing 1-, 2-, 3-, and 4-byte characters, and invalid bytes; byte mode MUST be tested to perform exactly ⌊*N*/2⌋ exchanges. A test MUST check that reversing twice gives back the original string, in both modes. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-reverse --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-reverse: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-reverse: unrecognized option 'T'` |
| `--lines=…`, `--bytes=…`, `--prompt=…`, `--help=…`, `--version=…` | `dp-reverse: option '--NAME' doesn't allow an argument` (with the option's name) |
| A second operand `X` | `dp-reverse: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-reverse: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-reverse: F: Permission denied` |
| FILE `F` is a directory | `dp-reverse: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-reverse: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-reverse: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| The string on line `L` of source `S` has more than 100 characters | `dp-reverse: S:L: string exceeds 100 characters` |
| The same, with `-b`: more than 100 bytes | `dp-reverse: S:L: string exceeds 100 bytes` |
| Standard output cannot be written (other than a broken pipe) | `dp-reverse: write error` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-09).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-06, FR-08 … FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 03, and 06 … 10 have several steps) | FR-02 … FR-06, FR-08 … FR-14 |
| Unit test (written by the implementer) | FR-04, FR-06, FR-07, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-07, FR-08 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-reverse words.txt` | FR-01, FR-02, FR-06 (even, odd, one unit, palindrome), FR-08 |
| 02 | `dp-reverse --prompt < words.txt` | FR-09 |
| 03 | `dp-reverse utf8.txt` | FR-04, FR-06 (characters) |
| 04 | `dp-reverse -b utf8.txt` | FR-04, FR-06 (bytes) |
| 05 | `dp-reverse -l lines.txt` | FR-03 (empty line, spaces kept) |
| 06 | `dp-reverse toolong.txt` | FR-05 (results kept, CONV-34) |
| 07 | `dp-reverse -p` (empty standard input) | FR-08, FR-09 |
| 08 | `dp-reverse missing.txt` | FR-10 |
| 09 | `dp-reverse --help` | FR-11 |
| 10 | `dp-reverse words.txt lines.txt` | FR-13, FR-14 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-08 |
| UR-02 | FR-03 |
| UR-03 | FR-04, FR-06, NFR-02 |
| UR-04 | FR-04, FR-06 |
| UR-05 | FR-05, CONV-34 |
| UR-06 | FR-09, CONV-36 |
| UR-07 | FR-01, FR-10, CONV-16, CONV-26 |
| UR-08 | FR-08, NFR-02 |
| UR-09 | FR-02, FR-03, NFR-02, CONV-37 |
| UR-10 | FR-11, FR-12 |
| UR-11 | FR-13, FR-14 |
| UR-12 | NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-07, FR-13, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |

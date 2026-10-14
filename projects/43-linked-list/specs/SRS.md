# Software Requirements Specification (SRS) — dp-elephnt1, dp-elephnt2

| Field | Value |
| :-- | :-- |
| Document ID | SRS-43 |
| Project | `43-linked-list` — Singly Linked List Foundations |
| Products | `dp-elephnt1`, `dp-elephnt2` (canonical names) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-43) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-elephnt1` and `dp-elephnt2`, and
the linked structure each must be built on. It is complete and precise enough that independent
implementations in any programming language produce **byte-identical** output for every
invocation. It is the authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-elephnt1` builds a linked list of three fixed names and prints it. `dp-elephnt2` reads a
line-oriented dialog — a name, then an answer saying whether another name follows — from
standard input or one file, builds a linked list of the names in the order given, and prints it
once the dialog has ended. It can write the textbook's prompts to standard error. It reports
malformed dialogs with line numbers and unreadable files with fixed messages. Requirements that
apply to one tool name it; all others apply to both.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR, TAB | The bytes `0x0A`, `0x0D`, and `0x09` |
| Whitespace byte | One of `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D` (CONV-32) |
| Input | The bytes of the FILE operand, or of standard input, with a trailing run of `0x1A` bytes ignored (CONV-37); `dp-elephnt2` only |
| Source | The FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) (CONV-34) |
| Line, line number, line text | As defined in FR-04 |
| Name | The line text of a name line, which MUST NOT be empty (FR-06) |
| Answer | The value of the line text of an answer line: 1 (add another name) or 0 (stop) (FR-07) |
| Node | A record holding one name and a link to its successor node or the end marker (NFR-05) |
| End marker | The link value that the last node holds instead of a successor (for example a null reference or an empty optional) |
| List line | One line of the list output: `Elephant number <N> is <NAME>.` (FR-02) |
| Decimal | The plain ASCII decimal representation of a positive integer: no sign, no leading zeros, no digit grouping (CONV-06) |

### 1.4 References
- URD-43: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains both normative help texts)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §10.2 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-elephnt1` and `dp-elephnt2` are two standalone executables built from one project. Their
interfaces are the command line, standard input or the file named by the operand
(`dp-elephnt2` only), standard output, standard error, and the exit status. They belong to the
curriculum's applications-programming track (Projects 11–52) and adapt the two programs of
§10.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*, which introduces linked
lists: one that links three statically created nodes and one that builds a list from a dialog.

### 2.2 Product functions
1. `dp-elephnt1`: create three nodes (Edna, Elmer, Eloise), link them, and print the list.
2. `dp-elephnt2`: read names and answers line by line until the answer 0 or the end of the
   input, appending one node per name, then print the list.
3. `dp-elephnt2`: optionally write the textbook's prompts to standard error.
4. Both: print a list by one shared traversal; report data and file errors; display help and
   version information; detect and report usage errors.

### 2.3 Constraints
- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through NFR-05, the data structure and
  decomposition of the code.

### 2.4 Assumptions
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- `dp-elephnt2` may be used interactively, with standard input and standard error connected to
  a terminal.
- The input may contain any bytes; names are copied, not interpreted.

### 2.5 Relationship to the textbook program (informative)
**Kept:** the three names Edna, Elmer, and Eloise in that order, in three nodes linked by hand;
the list output `Elephant number N is NAME.`, numbered from 1, produced by one traversal
function that follows the links to the end marker; the dialog of `dp-elephnt2` — a name, then
`Add another? (1 == yes, 0 == no)`, repeated while the answer is 1 — with each new node
appended at the end, so the list is printed in the order the names were entered; the prompt
texts, including the tab before and after each one; and printing the list only after the
dialog has ended.

**Changed, and why:**
- **Prompts are optional and go to standard error** (CONV-36), so standard output holds only the
  list and can be redirected or compared. The section shows each prompt indented by a tab and
  followed by a tab, with a blank line before it; `dp-elephnt2 --prompt` writes exactly that
  (FR-08). The three blank lines that separated the dialog from the list on the textbook's
  screen are not written: on standard output they would only precede the list.
- **Names are whole lines.** The section describes the name only as a string typed after the
  prompt. `dp-elephnt2` defines the dialog by lines, so a name may contain spaces
  (`Babar the Elephant`), surrounding whitespace is ignored, and CRLF files read like LF files
  (FR-04, FR-06). A blank name is an error rather than an invisible list entry.
- **Answers are validated.** The section ends the list when the answer is 0. `dp-elephnt2`
  accepts exactly the integers 0 and 1 and reports anything else with its line number (FR-07),
  instead of guessing whether `2` or `yes` means "another".
- **The end of the input is defined.** Where an answer is expected it ends the list like the
  answer 0, so a keyboard user can finish with Ctrl-D (Ctrl-Z then Enter on Windows); where a
  name is expected it is `unexpected end of input`, because the textbook dialog always asks for
  a name first and after every answer 1 (FR-05, FR-10).
- **No partial list.** The dialog is validated completely before the list is printed, so a
  failed run writes nothing to standard output (FR-09, FR-10).
- **Input sources.** Besides standard input, one FILE operand may be named; a trailing Ctrl-Z is
  accepted (FR-03, FR-04).
- **No length limits.** Names of any length and lists of any length are accepted, limited only
  by memory (NFR-03, NFR-04).
- **The linked structure is a requirement.** The section's point is the data structure, not the
  output. NFR-05 makes it a design requirement, checked by review, stated without reference to
  any language mechanism.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. `dp-elephnt1`
reads no input (CONV-26). Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | `dp-elephnt2` reads lines (FR-04); line numbers and the whitespace-byte set used for trimming follow CONV-32. |
| CONV-33 | The text of an answer line uses the *integer* grammar, restricted to 0 and 1 (FR-07). |
| CONV-34 | All data errors use its format, the standard messages `invalid integer`, `value out of range`, and `unexpected end of input`, and one additional message, `empty name` (FR-10). The default consequence is refined: no list is printed (FR-09). |
| CONV-35 | Not applicable: no real number is read or written. |
| CONV-36 | `dp-elephnt2` has `-p`, `--prompt` with two prompts (FR-08). `dp-elephnt1` reads nothing and has no prompts. |
| CONV-37 | The input of `dp-elephnt2` is *text data* (FR-04). |
| CONV-38 | Not applicable: nothing is random. |

CONV-04 does not constrain the output, because no input is copied through; names are written
byte for byte as FR-06 defines them.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-elephnt1
dp-elephnt2 [-p | --prompt] [FILE]
dp-elephnt1 --help | --version
dp-elephnt2 --help | --version
```

### 3.2 Options

| Short | Long | Argument | Tool | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | `dp-elephnt2` | Write the prompts of FR-08 to standard error |
| — | `--help` | none | both | Print the help text and exit 0 |
| — | `--version` | none | both | Print the version line and exit 0 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11). `dp-elephnt1` has no `-p`.

### 3.3 Operands
`dp-elephnt1` accepts no operands. `dp-elephnt2` accepts at most one FILE operand; with no
operand, or with the operand `-`, it reads standard input. Every token after `--` is an operand.
The operand is used and echoed exactly as given (CONV-19).

### 3.4 Standard input
`dp-elephnt1` never reads standard input. `dp-elephnt2` reads it when there is no operand or the
operand is `-` (CONV-26), as raw bytes with no newline translation on any platform,
incrementally (FR-04), and stops reading after the answer 0.

### 3.5 Standard output
The list lines (FR-02), and nothing else. `dp-elephnt2` writes them only after the dialog has
ended without error (FR-09). On a usage error, a data error, or a file error, nothing is written
to standard output.

### 3.6 Standard error
Diagnostics (section 6) and, for `dp-elephnt2 --prompt`, the prompts (FR-08). Without
`--prompt`, nothing is written to standard error when a run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The list was printed (`dp-elephnt2`: the dialog ended with the answer 0 or with the end of the input where an answer was expected), or `--help` / `--version` was handled |
| 1 | `dp-elephnt2`: the input could not be opened or read (FR-11), or the dialog contained a data error (FR-10); either tool: standard output could not be written |
| 2 | Usage error (FR-14) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\t` TAB, `\r` CR, and the named files are the
fixtures in `tests/fixtures/`: `readme.txt` is `Dumbo\n1\nBabar\n0\n` (the dialog shown in the
textbook section); `herd.txt` is
`  Jumbo  \n1\nBabar the Elephant\n 01 \n\tHorton\t\n+1\nElmer\n0\n`; `no-answer.txt` is
`Dumbo\n1\nBabar\n`; `bad-answer.txt` is `Dumbo\n1\nBabar\nyes\n`; `cut.txt` is `Dumbo\n1\n`.

### 4.1 Both tools

**FR-01: The fixed list (dp-elephnt1).**
`dp-elephnt1` MUST build the list Edna → Elmer → Eloise (three nodes, linked as NFR-05 (d)
requires) and print it with the traversal of FR-02. It reads no input. Its standard output is
exactly

```text
Elephant number 1 is Edna.
Elephant number 2 is Elmer.
Elephant number 3 is Eloise.
```

and it exits with status 0.
*AC:* `dp-elephnt1` → stdout as above (84 bytes), stderr empty, exit 0. *(UR-01, UR-03)*

**FR-02: List output.**
The list MUST be printed by walking it from its first node to the end marker. For the *k*-th
node visited (*k* = 1, 2, …) the tool MUST write the bytes `Elephant number `, the decimal of
*k*, the bytes ` is `, the node's name exactly as stored, and `.` followed by LF. There is one
space on each side of `is`, no other spaces, and no header, blank line, or summary. A list
always has at least one node, so at least one line is written.
*AC:* `dp-elephnt2 < readme.txt` → stdout
`Elephant number 1 is Dumbo.\nElephant number 2 is Babar.\n`, exit 0. *(UR-03)*

### 4.2 dp-elephnt2

**FR-03: Input source (dp-elephnt2).**
If there is no operand, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-14).
*AC:* `dp-elephnt2 < readme.txt`, `dp-elephnt2 readme.txt`, and `dp-elephnt2 - < readme.txt`
write the same list. *(UR-08)*

**FR-04: Lines (dp-elephnt2).**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored; a `0x1A` byte followed by any other byte is ordinary data. The
remaining input is divided into *lines*: each LF ends a line, and if the input does not end
with LF, the bytes after the last LF form a final line. An empty input has no lines, and the
end of the input directly after an LF does not start another line. A line's *number* is 1 plus
the number of LF bytes before its first byte (CONV-32). Its *text* is its bytes without the LF,
with every leading and trailing whitespace byte removed (so a CR before the LF, spaces, and
TABs disappear; whitespace inside the text is kept).
The input MUST be read incrementally: a line is complete, and MUST be processed, as soon as its
LF has been read, without waiting for further input; the only permitted lookahead is a run of
`0x1A` bytes, which is held back until the next byte shows whether it reaches the end of the
input.
*AC:* `herd.txt` gives the names `Jumbo`, `Babar the Elephant`, `Horton`, and `Elmer`; the hidden
fixture `crlf.txt` (`readme.txt` with CRLF line endings and a final `0x1A`) gives the same list
as `readme.txt`. *(UR-04, UR-09)*

**FR-05: Dialog (dp-elephnt2).**
The tool MUST run the following loop, starting with an empty list:

1. Write prompt P1 (FR-08) and read the next line. If the input has ended, the dialog fails
   with `unexpected end of input` (FR-10).
2. The line is a name line (FR-06). Create a new node holding the name and append it at the
   end of the list.
3. Write prompt P2 and read the next line. If the input has ended, the dialog ends.
4. The line is an answer line (FR-07). If the answer is 1, continue with step 1. If it is 0,
   the dialog ends; the rest of the input is not read or validated.

When the dialog ends, the last node's link is the end marker, and the list is printed (FR-09).
*AC:* `dp-elephnt2 herd.txt` → four list lines, exit 0; `dp-elephnt2 no-answer.txt` (the input
ends where the second answer is expected) → `Elephant number 1 is Dumbo.\nElephant number 2 is
Babar.\n`, exit 0. *(UR-02, UR-05)*

**FR-06: Names (dp-elephnt2).**
A name is the text (FR-04) of a name line. It MUST NOT be empty; a blank name line (empty, or
whitespace bytes only) is a data error (FR-10). Otherwise the name is stored and later written
exactly as these bytes: it MAY contain internal spaces and TABs, bytes that are not valid
UTF-8, and `0x1A` bytes that do not end the input. There is no length limit.
*AC:* `herd.txt` keeps `Babar the Elephant` whole and writes `  Jumbo  ` as `Jumbo`; the hidden
fixture `empty-name.txt`, whose third line is spaces, a TAB, and a CR, is rejected with
`empty name` on line 3. *(UR-04, UR-06)*

**FR-07: Answers (dp-elephnt2).**
The text (FR-04) of an answer line MUST be a valid *integer* (CONV-33) — so it is one token
without internal whitespace — with the value 0 or 1. A sign and leading zeros are allowed:
`+1`, `01`, and `-0` are valid. Text that is not a valid *integer* (including the empty text of
a blank line, `yes`, `1.0`, and `1 1`) is `invalid integer`; a valid *integer* other than 0 or 1
is `value out of range` (FR-10).
*AC:* `herd.txt` accepts ` 01 ` and `+1`; `dp-elephnt2 bad-answer.txt` →
`dp-elephnt2: bad-answer.txt:4: invalid integer 'yes'`; the hidden fixture `answer-two.txt`
(`Dumbo\n2\n`) → `value out of range '2'` on line 2. *(UR-02, UR-06)*

**FR-08: Prompts (dp-elephnt2).**
With `-p` or `--prompt`, the tool MUST write these prompts to standard error, and flush
standard error before the read that follows (CONV-36):

| Prompt | Exact bytes | Written |
| :-- | :-- | :-- |
| P1 | LF, TAB, `NAME:`, TAB (8 bytes) | Before every read of a name line (step 1 of FR-05), including one that reaches the end of the input |
| P2 | LF, TAB, `Add another? (1 == yes, 0 == no)`, TAB (35 bytes) | Before every read of an answer line (step 3 of FR-05), including one that reaches the end of the input |

Nothing else is written to standard error for prompting: no LF after the user's line, and none
before the list. Without the flag, no prompt is written. Standard output is the same with and
without it.
*AC:* `dp-elephnt2 --prompt < readme.txt` → stdout as in FR-02; stderr P1 P2 P1 P2
concatenated, that is
`\n\tNAME:\t\n\tAdd another? (1 == yes, 0 == no)\t\n\tNAME:\t\n\tAdd another? (1 == yes, 0 == no)\t`,
exit 0. *(UR-07)*

**FR-09: Printing the list (dp-elephnt2).**
The list MUST be printed (FR-02) only after the dialog has ended without error: nothing is
written to standard output while the dialog runs, and nothing at all when it fails. Standard
output is flushed before the tool exits.
*AC:* `dp-elephnt2 bad-answer.txt` → stdout empty, although a name was read before the error.
*(UR-03, UR-06)*

**FR-10: Data errors (dp-elephnt2).**
At the first error in the dialog the tool MUST write one CONV-34 diagnostic,
`dp-elephnt2: <source>:<line>: <message>`, read no further input, write nothing to standard
output, and exit with status 1.

| Condition | `<line>` | `<message>` |
| :-- | :-- | :-- |
| The input ends where a name is expected (FR-05 step 1), including an empty input | the end-of-input line number (CONV-32) | `unexpected end of input` |
| A name line is blank (FR-06) | the line's number | `empty name` |
| The text of an answer line is not a valid *integer* | the line's number | `invalid integer '<text>'` |
| The text of an answer line is a valid *integer* other than 0 and 1 | the line's number | `value out of range '<text>'` |

`<text>` is the line's text (FR-04), inserted as its exact bytes (CONV-15); it is empty for a
blank answer line. A prompt already written stays written, so with `--prompt` the diagnostic
follows the last prompt on the same line of standard error.
*AC:* `dp-elephnt2 -p cut.txt` → stdout empty; stderr P1 P2 P1 followed directly by
`dp-elephnt2: cut.txt:3: unexpected end of input\n`; exit 1. `dp-elephnt2 -p` with empty
standard input → stderr P1 followed by `dp-elephnt2: -:1: unexpected end of input\n`, exit 1.
*(UR-06)*

**FR-11: File errors (dp-elephnt2).**
If the FILE operand does not exist, cannot be opened, or is a directory, the tool MUST write
`dp-elephnt2: <FILE>: <reason>` with the CONV-16 reason, write nothing to standard output and
no prompt, and exit with status 1. If a read error occurs later, the same diagnostic is written
and nothing is written to standard output. A failure of standard input is reported with
`<FILE>` = `-`.
*AC:* `dp-elephnt2 missing.txt` → `dp-elephnt2: missing.txt: No such file or directory`,
exit 1; `dp-elephnt2 subdir` → `dp-elephnt2: subdir: Is a directory`. *(UR-10)*

### 4.3 Both tools

**FR-12: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read and no prompt
is written.
*AC:* `dp-elephnt1 --help` and `dp-elephnt2 --help` match the user manual exactly;
`dp-elephnt2 a b --help` and `dp-elephnt1 extra --help` print the help. *(UR-12)*

**FR-13: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* `dp-elephnt1 --version` → `dp-elephnt1 (dialectic-playground) 1.0.0\n`. *(UR-12)*

**FR-14: Usage errors.**
Unknown options, and an argument given to an option that takes none (`--help=…`, `--version=…`,
and for `dp-elephnt2` `--prompt=…`), MUST be reported with the CONV-13 messages followed by the
CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08). `dp-elephnt1`
has no `-p` option and no operands: `dp-elephnt1 -p` is an invalid option, `dp-elephnt1
--prompt` an unrecognized option, and any operand `X` is reported as
`dp-elephnt1: extra operand 'X'`. For `dp-elephnt2`, a second operand MUST be reported as
`dp-elephnt2: extra operand '<second operand>'`. Operands are checked only after the whole
argument list has been scanned (CONV-12).
*AC:* `dp-elephnt2 a b` → `dp-elephnt2: extra operand 'b'`; `dp-elephnt2 -x --help` →
`dp-elephnt2: invalid option -- 'x'`; `dp-elephnt2 --prompt=1` →
`dp-elephnt2: option '--prompt' doesn't allow an argument`; `dp-elephnt1 extra` →
`dp-elephnt1: extra operand 'extra'`; each followed by the CONV-14 line, exit 2. *(UR-13)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case; `dp-elephnt2 -p - extra < readme.txt` writes no
prompt. *(UR-13)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line the tools generate MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: interactive line input and end of input | The input of `dp-elephnt2` MUST be read in binary mode on every platform, so CR bytes reach the line reader (where FR-04 trims them) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-04 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally, with the effect FR-05 defines. Each prompt MUST reach the terminal before the tool waits for input: standard error MUST be flushed explicitly where the platform buffers it. Standard output and standard error MUST be written in binary mode (CONV-03). Names MUST be handled as bytes, never decoded, so a name that is not valid UTF-8 (or not valid in the console's code page) is written back unchanged. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance | Each tool MUST start and exit in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware for the public fixtures. `dp-elephnt2` MUST process a dialog of 100 000 names (about 1.6 MiB) in under 2 s native (20 s interpreted). Its memory MUST grow only with the list (one node per name plus the name bytes), not with the length of the input otherwise: peak memory for that dialog MUST stay under 32 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Appending a name MUST take constant time, independent of the length of the list. | Measurement |
| NFR-04 | Robustness | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24). Lines of any length MUST be handled; an answer outside the 64-bit range is `invalid integer`, never overflowed. A broken pipe on standard output ends a tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability: linked structure | (a) There MUST be one node record type with exactly two fields: a name and a link to the successor node. (b) The names MUST be held only in such nodes, linked through those links; no built-in or library array, vector, list, or other collection may hold the names or the nodes (a buffer holding the line being read is allowed). (c) The last node's link MUST be set explicitly to an end marker (for example a null reference or an empty optional), and the traversal MUST stop only by reaching it. (d) `dp-elephnt1` MUST create its three nodes as three individually written records and link them by three explicit assignments of the link fields, not by a loop over a table of names. (e) `dp-elephnt2` MUST create one node per name at run time and append it through a reference to the current last node, without walking the list. (f) One traversal procedure, one unit of source shared by both tools, MUST receive the first node and write the list lines of FR-02, counting the nodes as it walks; it MUST NOT receive or compute the length in advance. (g) The line reader, the dialog, prompting, and the list structure MUST be separate units, and command-line handling common to both tools MUST be shared rather than duplicated. | Design review |
| NFR-06 | Testability | The traversal MUST be testable with an output stream supplied by the caller, and covered by unit tests on a one-node and a three-node list and on a list of 1000 nodes. The line reader MUST be unit-tested with the input split into reads at every byte position, including inputs with CRLF line endings, a final line without LF, and trailing `0x1A` bytes. Answer validation MUST be unit-tested with `0`, `1`, `+1`, `-0`, `01`, `2`, `-1`, `yes`, an empty text, and `9223372036854775808`. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | `dp-elephnt1` MUST NOT read any input. `dp-elephnt2` MUST read only the FILE operand or standard input. Neither tool may create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2) are each followed by `Try '<tool> --help' for more information.`,
where `<tool>` is `dp-elephnt1` or `dp-elephnt2`.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (for `dp-elephnt1`, including `-p`) | `<tool>: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` (for `dp-elephnt1`, including `--prompt`) | `<tool>: unrecognized option 'T'` |
| `--help=…` / `--version=…`; `--prompt=…` (dp-elephnt2) | `<tool>: option '--help' doesn't allow an argument` (or `'--version'`, `'--prompt'`) |
| `dp-elephnt1`: any operand `X` | `dp-elephnt1: extra operand 'X'` |
| `dp-elephnt2`: a second operand `X` | `dp-elephnt2: extra operand 'X'` |

File errors (`dp-elephnt2`, exit status 1):

| Trigger | Exact message |
| :-- | :-- |
| FILE does not exist | `dp-elephnt2: FILE: No such file or directory` |
| Access to FILE is denied | `dp-elephnt2: FILE: Permission denied` |
| FILE is a directory | `dp-elephnt2: FILE: Is a directory` |
| A component of FILE is not a directory | `dp-elephnt2: FILE: Not a directory` |
| Any other open or read failure | `dp-elephnt2: FILE: Input/output error` |
| Any of the above for standard input | the same message with `FILE` = `-` |

Data errors (`dp-elephnt2`, exit status 1; nothing is written to standard output):

| Trigger | Exact message |
| :-- | :-- |
| Input ends where a name is expected | `dp-elephnt2: SOURCE:LINE: unexpected end of input` |
| Blank name line | `dp-elephnt2: SOURCE:LINE: empty name` |
| Answer text not a valid *integer* | `dp-elephnt2: SOURCE:LINE: invalid integer 'TEXT'` |
| Answer a valid *integer* other than 0 and 1 | `dp-elephnt2: SOURCE:LINE: value out of range 'TEXT'` |

Output errors (exit status 1):

| Trigger | Exact message |
| :-- | :-- |
| Standard output cannot be written (other than a broken pipe, CONV-25) | `<tool>: write error` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-10).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-12 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 01 … 05 and 07 … 10 have several steps) | FR-02 … FR-15 |
| Unit test (written by the implementer) | FR-02, FR-04 … FR-07, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review / demonstration | FR-04 (interactive timing), NFR-02, NFR-05, NFR-08 |

Fixtures (`tests/fixtures/`): `readme.txt` is the dialog shown in the textbook section (Dumbo,
1, Babar, 0); `herd.txt` has names with surrounding and internal spaces and TABs and the answers
` 01 ` and `+1`; `no-answer.txt` ends where an answer is expected; `bad-answer.txt` answers
`yes` on line 4; `cut.txt` ends after the answer 1.

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-elephnt1` | FR-01, FR-02 |
| 02 | `dp-elephnt2 < readme.txt` | FR-02 … FR-05 |
| 03 | `dp-elephnt2 --prompt < readme.txt` | FR-08 |
| 04 | `dp-elephnt2 herd.txt` | FR-04, FR-06, FR-07 |
| 05 | `dp-elephnt2 no-answer.txt` | FR-05 (end of input in place of an answer) |
| 06 | `dp-elephnt2 bad-answer.txt` | FR-07, FR-09, FR-10 |
| 07 | `dp-elephnt2 -p cut.txt` | FR-08, FR-10 |
| 08 | `dp-elephnt2 missing.txt` | FR-11 |
| 09 | `dp-elephnt1 --help` | FR-12 |
| 10 | `dp-elephnt2 --help` | FR-12 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02 |
| UR-02 | FR-05, FR-07 |
| UR-03 | FR-02, FR-09 |
| UR-04 | FR-04, FR-06 |
| UR-05 | FR-05 |
| UR-06 | FR-06, FR-07, FR-09, FR-10, CONV-33, CONV-34 |
| UR-07 | FR-08, CONV-36 |
| UR-08 | FR-03, CONV-26 |
| UR-09 | FR-04, NFR-02, CONV-37 |
| UR-10 | FR-11, CONV-16 |
| UR-11 | NFR-05, NFR-06 |
| UR-12 | FR-12, FR-13 |
| UR-13 | FR-14, FR-15 |
| UR-14 | NFR-01, NFR-02, CONV-03 |
| UR-15 | FR-14, NFR-03, NFR-07, CLI-CONV |

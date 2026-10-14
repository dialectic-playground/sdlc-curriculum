# Software Requirements Specification (SRS) — dp-ship

| Field | Value |
| :-- | :-- |
| Document ID | SRS-52 |
| Project | `52-spacecraft` — Object-Oriented Spacecraft Domain Modeling |
| Product | `dp-ship` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-52) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-ship`, and one design requirement
on its structure (NFR-05). It is complete and precise enough that independent implementations
in any programming language produce **byte-identical** output for every invocation. It is the
authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-ship` models spacecraft, each with a name, a mass, a velocity, a trip distance, and a crew
capacity. With no operand it runs the textbook's scenario: it creates a default ship and a ship
named MightyMite, adjusts MightyMite's velocity, and reports the ships' basics and
MightyMite's trip time. With a FILE operand it runs a command script that creates ships,
adjusts their velocities, and reports on them. It reports invalid script lines with their line
numbers and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Ship | A spacecraft object with the five attributes *name*, *mass*, *velocity*, *distance*, and *capacity* (FR-02) |
| Script | The byte sequence read from the FILE operand, or from standard input when the operand is `-` |
| Source | The name used for the script in diagnostics: the FILE operand exactly as given, or `-` for standard input |
| Line | A maximal run of bytes not containing LF, as delimited by LF bytes; the bytes after the last LF form a final line if they are not empty. Line *n* is the *n*-th line, counted from 1 |
| Field | A maximal run, within one line, of bytes other than the CONV-32 whitespace bytes (`0x20`, `0x09`, `0x0B`, `0x0C`, `0x0D`) |
| Identifier (ID) | The field that names a ship within one run; compared byte for byte, case-sensitively |
| *real*, *integer* | The numeric grammars of CONV-33 |
| binary64 | The IEEE 754 double-precision format; every operation is correctly rounded to nearest, ties to even |
| `GEN(x, p)` | The number formatting rule of CONV-35 (C's `%.pg`, no negative zero) |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-52: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §11.5 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-ship` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §11.5 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*, the book's introduction to
object-oriented programming.

### 2.2 Product functions
1. Model a spacecraft as an encapsulated object with default and full construction, velocity
   adjustment clamped at 0, a basics report, and a trip time.
2. Run the textbook scenario when no operand is given.
3. Run a command script that creates, adjusts, and reports on ships.
4. Report invalid script lines and unreadable files.
5. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior, plus the object design of NFR-05, which is
  stated in language-neutral terms.
- Mass, velocity, distance, and trip time MUST be binary64 values computed as FR-03 and FR-04
  prescribe.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- A script may contain any bytes; only lines that follow FR-08 and FR-09 are valid.

### 2.5 Relationship to the textbook program (informative)
The textbook example of §11.5 is a short C++ program, the book's first look at classes. It
declares a spacecraft class with private data (name, mass, velocity, distance, capacity), a
default constructor and a constructor that sets every attribute, a member function that
adjusts the velocity without letting it fall below zero, accessors, and a function that prints
the ship's basics; its `main` runs a fixed scenario and prints the trip time as distance divided
by velocity. `dp-ship` keeps:

- the five attributes, the default values (name `???`, everything else zero), the order of the
  full constructor's parameters (mass, velocity, distance, capacity, name), and the velocity
  clamp at 0;
- the report wording and layout exactly, including `holds 1 astronauts` (no singular form) and
  the empty line after each basics report;
- the scenario: it produces the textbook's output (FR-07), with one correction below.

It changes the following, for the reasons given:

- **Explicit number formatting.** The textbook wrote numbers with the C++ stream defaults,
  which format a floating-point value like C's `%g` with six significant digits. FR-05 and
  FR-06 name this rule explicitly as `GEN(x, 6)` (CONV-35), so `63567.0` is written `63567` and
  `1234567.0` is written `1.23457e+06` in every language.
- **The trip time is correct.** The section's description gives MightyMite's trip time as
  `8.68832` hours. The quotient of its own numbers, 560989 / 64567, is 8.688478…, written
  `8.68848` by `GEN(x, 6)`; that is what `dp-ship` prints (FR-07). (8.68832 does not result
  from any velocity in the scenario: 560989 / 63567 is 8.825161….)
- **Zero velocity is guarded.** The textbook divided by the velocity unconditionally, so a ship
  at rest would have printed an infinite or undefined time. FR-04 and FR-06 report instead that
  the ship cannot make the trip at that velocity.
- **A command script.** The textbook's scenario was fixed in its source code. To make the class
  usable as a tool, `dp-ship` also runs a script of commands that correspond one to one to the
  class's operations (FR-08, FR-09). Without an operand it still runs the textbook scenario,
  and the script language can express that scenario exactly (FR-07).
- **Validated values.** The C++ constructor accepted any values. A script's mass, velocity, and
  distance must be non-negative reals and its capacity a non-negative integer (FR-09); every
  invalid line is reported with its line number (FR-10).
- **No prompts.** The textbook program read no input, so there is nothing to prompt for and the
  tool has no `--prompt` option.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV and makes **no overrides**. Option syntax follows CONV-07 …
CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Standard input is read only
when the operand is `-` (CONV-26). Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | The script is line-oriented. Lines are split into fields at the CONV-32 whitespace bytes other than LF, and lines are numbered by the CONV-32 rule (FR-08). |
| CONV-33 | MASS, VEL, DIST, and DIFF use the *real* grammar and CAP the *integer* grammar, with the range restrictions of FR-09. |
| CONV-34 | Data errors use its format, the standard messages `invalid integer`, `invalid number`, and `value out of range`, and five further messages (FR-10). |
| CONV-35 | Mass, velocity, distance, and trip time are written as `GEN(x, 6)` (FR-05, FR-06). |
| CONV-36 | Not applicable: the textbook program did not prompt, so there is no `--prompt`. |
| CONV-37 | Applies: the script is *text data* (FR-08). |
| CONV-38 | Not applicable: nothing is random. |

A ship's name is copied from the script to standard output byte for byte, as CONV-04 requires.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-ship [FILE]
dp-ship --help
dp-ship --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (`--` and scan order) follows CONV-07 … CONV-12.

### 3.3 Operands
At most one FILE operand. Without an operand the textbook scenario runs (FR-07). The operand
`-` denotes standard input (CONV-10). Every token after `--` is an operand, even if it begins
with `-`. The operand is used and echoed exactly as given (CONV-19).

### 3.4 Standard input
Read only when the operand is `-` (FR-01), to its end, as raw bytes; no newline translation of
any kind is performed on any platform.

### 3.5 Standard output
The reports written by `print` and `trip` commands (FR-05, FR-06), in script order. Nothing
else. On a usage error, or when `--help` / `--version` is handled, the output is as specified
by FR-12 … FR-15 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The scenario or the whole script was executed (including an empty script), or `--help` / `--version` was handled |
| 1 | The script could not be read (FR-11), it contained an invalid line (FR-10), or standard output could not be written |
| 2 | Usage error (FR-14) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `fleet.txt`, `clamp.txt`, and `bad.txt` are the
public fixture files in `tests/fixtures/`. `fleet.txt` creates the textbook's two ships, prints
both, adjusts MightyMite by +2000 and −1000, reports its trip, and then creates, prints, and
reports a probe `Voyager` (mass 721.9, velocity 61500.5, distance 1.2e9, capacity 0); it
contains a comment line, an empty line, and TAB separators. `clamp.txt` slows MightyMite by
100000 and reports it, then speeds it up by 0.25, and reports the trip of a default ship.
`bad.txt` is
`new s1 5000 63567 560989 4 MightyMite\nprint s1\nadjust s1 fast\ntrip s1\n`.

**FR-01: Modes and input source.**
If no operand is given, the tool MUST run the textbook scenario (FR-07); it reads no input. If
the operand is `-`, it MUST read standard input to its end; otherwise it MUST open the file
named by the operand and read it to its end as raw bytes. The script is read completely before
any command is executed. More than one operand is a usage error (FR-14).
*AC:* `dp-ship` → the scenario output of FR-07, exit 0; `dp-ship fleet.txt` and
`dp-ship - < fleet.txt` write the same output; `dp-ship -` with empty standard input → stdout
and stderr empty, exit 0. *(UR-01, UR-04)*

**FR-02: The spacecraft.**
A ship has exactly five attributes: *name* (a non-empty byte string), *mass* (kilograms),
*velocity* (kilometers per hour), and *distance* (kilometers of the trip), each a binary64
value ≥ 0, and *capacity* (astronauts), an integer 0 … 2⁶³−1. A ship MUST be creatable in two
ways: by **default construction**, which sets the name to the three bytes `???`, mass,
velocity, and distance to 0.0, and capacity to 0; and by **full construction**, which sets all
five attributes from given values, taken in the order mass, velocity, distance, capacity, name.
After construction, the velocity changes only through FR-03; no other attribute ever changes.
*AC:* a default ship's basics report is
`??? has a mass of 0\nand a velocity of 0 and holds 0 astronauts for a trip of 0 kilometers.\n\n`.
*(UR-02, UR-03)*

**FR-03: Velocity adjustment.**
Adjusting a ship's velocity by a difference *D* (a finite binary64 value of any sign) MUST
compute *v* = *velocity* + *D* as one binary64 addition. If *v* is infinite, the adjustment is
rejected (FR-10) and the ship is unchanged. Otherwise, if *v* < 0, the velocity becomes +0.0;
else it becomes *v*.
*AC:* MightyMite (velocity 63567) adjusted by 2000 and then by −1000 has velocity 64567;
adjusted by −100000 it has velocity 0, and adjusting that by 0.25 gives 0.25. *(UR-03)*

**FR-04: Trip time.**
A ship's trip time MUST be *distance* / *velocity* in hours, computed as one binary64 division.
The trip time is *undefined* when the velocity is zero (of either sign), or when the quotient
is infinite (overflow). A ship's trip time is never computed in any other way.
*AC:* distance 560989 and velocity 64567 → 8.688478634596620…; distance 0 and velocity 5 → 0;
velocity 0 → undefined; distance 1e300 and velocity 1e-320 → undefined. *(UR-03, UR-06)*

**FR-05: Basics report.**
The basics report of a ship MUST be exactly the three lines

```text
<name> has a mass of <M>
and a velocity of <V> and holds <C> astronauts for a trip of <D> kilometers.

```

(the third line is empty), where `<name>` is the name's exact bytes, `<M>`, `<V>`, and `<D>` are
`GEN(mass, 6)`, `GEN(velocity, 6)`, and `GEN(distance, 6)` (CONV-35), and `<C>` is the decimal
of the capacity. Each line ends with a single LF. There is exactly one space between words,
none at the start or end of a line, and the word `astronauts` is used for every capacity.
*AC:* `GEN` writes 5000 as `5000`, 1234567 as `1.23457e+06`, 0.00001 as `1e-05`, 123456.5 as
`123456` (exact tie, rounded to even), 999999.5 as `1e+06`, and −0 as `0`. *(UR-02, UR-05)*

**FR-06: Trip report.**
The trip report of a ship MUST be one line: `<name> requires <T> hours for trip.` where `<T>` is
`GEN(trip time, 6)`, or, when the trip time is undefined (FR-04),
`<name> cannot make the trip at a velocity of <V>.` where `<V>` is `GEN(velocity, 6)`. The line
ends with a single LF.
*AC:* `MightyMite requires 8.68848 hours for trip.`; a default ship →
`??? cannot make the trip at a velocity of 0.`; distance 1e300 at velocity 1e-320 →
`Slow cannot make the trip at a velocity of 9.99989e-321.` *(UR-05, UR-06)*

**FR-07: Textbook scenario.**
Without an operand, the tool MUST behave exactly as if it executed this script (FR-09):

```text
new s1
print s1
new s2 5000 63567 560989 4 MightyMite
print s2
adjust s2 2000
adjust s2 -1000
print s2
trip s2
```

*AC:* `dp-ship` → stdout exactly

```text
??? has a mass of 0
and a velocity of 0 and holds 0 astronauts for a trip of 0 kilometers.

MightyMite has a mass of 5000
and a velocity of 63567 and holds 4 astronauts for a trip of 560989 kilometers.

MightyMite has a mass of 5000
and a velocity of 64567 and holds 4 astronauts for a trip of 560989 kilometers.

MightyMite requires 8.68848 hours for trip.
```

stderr empty, exit 0. A file containing the script above produces the same output.
*(UR-01, UR-02)*

**FR-08: Script format.**
The script is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the script is ignored. The remaining bytes are divided into lines at LF bytes and each
line into fields (section 1.3); a CR before an LF is therefore whitespace, and CRLF scripts read
exactly like LF scripts. A line with no fields (empty, or only whitespace) and a line whose
first field begins with the byte `#` (a comment) are ignored. Every other line is a command
(FR-09), and the commands are executed one after another in line order.
*AC:* `fleet.txt`, which contains a comment, an empty line, and TABs, is executed without error;
a script `# DOS file\r\n\r\n  new\ts1  \r\nprint s1\r\n#trip s1\r\ntrip s1\r\n` followed by
two `0x1A` bytes writes the basics and trip report of a default ship, exit 0. *(UR-04, UR-08)*

**FR-09: Commands.**
The first field of a command line is the command name, compared byte for byte (lowercase).
The commands, their fields, and their effects are:

| Command | Fields after the name | Effect |
| :-- | :-- | :-- |
| `new` | `ID` | Create a ship by default construction (FR-02) and call it ID |
| `new` | `ID MASS VEL DIST CAP NAME` | Create a ship by full construction with mass MASS, velocity VEL, distance DIST, capacity CAP, and name NAME, and call it ID |
| `adjust` | `ID DIFF` | Adjust the velocity of ship ID by DIFF (FR-03) |
| `print` | `ID` | Write the basics report of ship ID (FR-05) |
| `trip` | `ID` | Write the trip report of ship ID (FR-06) |

MASS, VEL, and DIST MUST be valid *real*s (CONV-33) whose values are not less than 0 (`-0` is
allowed and means zero); CAP MUST be a valid *integer* in 0 … 2⁶³−1; DIFF MUST be a valid *real*
(any sign). NAME is any field, used as its exact bytes. ID is any field; `new` requires that no
ship of that ID exists yet, and the other commands require that one does. Ships exist until the
end of the run.
*AC:* `dp-ship fleet.txt` → the textbook ships' reports, then
`Voyager has a mass of 721.9\nand a velocity of 61500.5 and holds 0 astronauts for a trip of 1.2e+09 kilometers.\n\nVoyager requires 19512 hours for trip.\n`,
exit 0. *(UR-03, UR-04)*

**FR-10: Invalid script lines.**
For each command line, the tool MUST check, in this order, and report the first failure as a
CONV-34 diagnostic `dp-ship: <source>:<line>: <message>`, where `<line>` is the line number:

1. The command name is not one of `new`, `adjust`, `print`, `trip`: `unknown command '<name>'`.
2. There are more fields than the command's largest form allows (6 after `new`, 2 after
   `adjust`, 1 after `print` and `trip`): `extra argument '<first surplus field>'`.
3. The number of fields matches no form of the command: `missing argument for '<name>'`.
4. For `new`, a ship with that ID exists: `ship '<ID>' already exists`; for the other commands,
   none exists: `unknown ship '<ID>'`.
5. The numeric fields, from left to right: a field that is not a valid *real* →
   `invalid number '<field>'`; a MASS, VEL, or DIST below 0 → `value out of range '<field>'`; a
   CAP that is not a valid *integer* → `invalid integer '<field>'`; a CAP below 0 →
   `value out of range '<field>'`.
6. For `adjust`, the sum of FR-03 is infinite: `value out of range '<DIFF>'`.

Fields are inserted as their exact bytes (CONV-15). The tool then stops: it executes no further
command and exits with status 1. Reports already written for earlier commands are kept
(CONV-34).
*AC:* `dp-ship bad.txt` → stdout the basics report of MightyMite, stderr
`dp-ship: bad.txt:3: invalid number 'fast'\n`, exit 1. `fly s1` →
`unknown command 'fly'`; `print s9` with no ship `s9` → `unknown ship 's9'`; a second `new a` →
`ship 'a' already exists`; `print` → `missing argument for 'print'`; `new a 1 2` →
`missing argument for 'new'`; `trip a b` → `extra argument 'b'`; `new a -1 2 3 4 A` →
`value out of range '-1'`; CAP `4.5` → `invalid integer '4.5'`; VEL `inf` →
`invalid number 'inf'`; `adjust c 1e308` on a ship whose velocity is already 1e308 →
`value out of range '1e308'`. *(UR-07)*

**FR-11: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-ship: <source>: <reason>` with `<reason>` from the CONV-16 table, write
nothing to standard output, and exit with status 1. When standard input fails, `<source>` is
`-`.
*AC:* `dp-ship missing.txt` → stderr `dp-ship: missing.txt: No such file or directory\n`, stdout
empty, exit 1; `dp-ship subdir` where `subdir` is a directory → `dp-ship: subdir: Is a
directory`. *(UR-09)*

**FR-12: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-ship --help` matches the user manual exactly; `dp-ship extra --help` also prints it.
*(UR-10)*

**FR-13: Version.**
`--version` MUST write `dp-ship (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-14: Usage errors.**
Unknown options, and arguments supplied to `--help` or `--version`, MUST be reported with the
CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be
abbreviated (CONV-08). A second operand MUST be reported as
`dp-ship: extra operand '<second operand>'`, after the whole argument list has been scanned
(CONV-12).
*AC:* `dp-ship fleet.txt clamp.txt` → `dp-ship: extra operand 'clamp.txt'`; `dp-ship -x` →
`dp-ship: invalid option -- 'x'`; `dp-ship --version=2` →
`dp-ship: option '--version' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, run the
scenario, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: number formatting without stream defaults | Real numbers MUST be written by `GEN(x, 6)` exactly as CONV-35 defines it — rounding from the exact binary64 value with ties to even, the switch to exponent form at 10⁶ and below 10⁻⁴, at least two exponent digits (`1e-05`, never `1e-005` as older Windows C runtimes print), subnormal values formatted correctly, and no negative zero. A language's default conversion of a floating-point number to text (C++ streams, `toString`, `str`, `Display`) MUST NOT be relied on, because its digits differ between languages and runtimes. Reals MUST be parsed by correct rounding (CONV-33), including subnormal results. Scripts MUST be read in binary mode, so CR and `0x1A` bytes reach FR-08 unchanged. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | The scenario MUST run in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware. A script of 100 000 commands (up to 4 MiB) with 1000 ships MUST run in under 1 s native (10 s interpreted), with peak memory under 64 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or script bytes (CONV-24), including fields of any length, numbers far outside the binary64 or 64-bit range, and velocities whose trip time overflows. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability: object design | The spacecraft MUST be one abstraction — a class, a module with an opaque record type, or the language's equivalent — that **encapsulates** its five attributes: code outside the abstraction MUST NOT read or write them except through its operations. It MUST provide exactly these operations: default construction and full construction (FR-02), velocity adjustment (FR-03), trip time (FR-04), the basics report (FR-05), and one read accessor per attribute. The clamp rule and the trip-time formula MUST each appear only inside the abstraction. The script interpreter, the scenario, and the report formatting of FR-06 MUST use only these operations, and option parsing, script parsing, and I/O MUST be separate units (Principles 13, 18). | Design review |
| NFR-06 | Testability | The spacecraft abstraction MUST be covered by unit tests of both constructions, the clamp (to exactly 0, and from 0 upward), the trip time including the undefined cases, and the basics report. The `GEN` formatter MUST be unit-tested with every example of FR-05 and CONV-35. Script parsing (bytes → commands or a data error) MUST be a pure function. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-ship --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-ship: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-ship: unrecognized option 'T'` |
| `--help=…` / `--version=…` | `dp-ship: option '--help' doesn't allow an argument` (or `'--version'`) |
| A second operand `X` | `dp-ship: extra operand 'X'` |

File errors (exit status 1, nothing on standard output):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-ship: F: No such file or directory` |
| Access to FILE `F` is denied | `dp-ship: F: Permission denied` |
| FILE `F` is a directory | `dp-ship: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-ship: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-ship: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |

Data errors (exit status 1, earlier reports kept; FR-10). `S` is the source, `L` the line number:

| Trigger | Exact message |
| :-- | :-- |
| Unknown command name `N` | `dp-ship: S:L: unknown command 'N'` |
| Surplus field `X` | `dp-ship: S:L: extra argument 'X'` |
| Too few fields for command `N` | `dp-ship: S:L: missing argument for 'N'` |
| `new` with an ID `I` already in use | `dp-ship: S:L: ship 'I' already exists` |
| Another command with an unknown ID `I` | `dp-ship: S:L: unknown ship 'I'` |
| MASS, VEL, DIST, or DIFF field `X` is not a valid *real* | `dp-ship: S:L: invalid number 'X'` |
| MASS, VEL, or DIST field `X` is below 0 | `dp-ship: S:L: value out of range 'X'` |
| CAP field `X` is not a valid *integer* | `dp-ship: S:L: invalid integer 'X'` |
| CAP field `X` is below 0 | `dp-ship: S:L: value out of range 'X'` |
| `adjust` by DIFF field `X` makes the velocity infinite | `dp-ship: S:L: value out of range 'X'` |

Output errors (exit status 1):

| Trigger | Exact message |
| :-- | :-- |
| Standard output cannot be written (other than a broken pipe, CONV-25) | `dp-ship: write error` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-12, FR-14, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 04 and 07 … 10 have several steps) | FR-02 … FR-11, FR-13 … FR-15 |
| Unit test (written by the implementer) | FR-02 … FR-06, FR-08, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-ship` | FR-01, FR-02, FR-03, FR-05, FR-06, FR-07 |
| 02 | `dp-ship fleet.txt` | FR-01, FR-08, FR-09, FR-05 (exponent form) |
| 03 | `dp-ship - < fleet.txt` | FR-01 |
| 04 | `dp-ship clamp.txt` | FR-03 (clamp), FR-04, FR-06 (undefined trip time) |
| 05 | `dp-ship bad.txt` | FR-10 (reports kept, CONV-34) |
| 06 | `dp-ship missing.txt` | FR-11 |
| 07 | `dp-ship --help` | FR-12 |
| 08 | `dp-ship -` (empty standard input) | FR-01, FR-08 |
| 09 | `dp-ship fleet.txt clamp.txt` | FR-14, FR-15 |
| 10 | `dp-ship -x` | FR-14 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-07 |
| UR-02 | FR-02, FR-05, FR-07 |
| UR-03 | FR-02, FR-03, FR-04, FR-09 |
| UR-04 | FR-01, FR-08, FR-09 |
| UR-05 | FR-05, FR-06, NFR-02, CONV-35 |
| UR-06 | FR-04, FR-06 |
| UR-07 | FR-10, CONV-33, CONV-34 |
| UR-08 | FR-08, NFR-02, CONV-37 |
| UR-09 | FR-11, CONV-16 |
| UR-10 | FR-12, FR-13 |
| UR-11 | FR-14, FR-15 |
| UR-12 | NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-14, CLI-CONV |
| UR-14 | NFR-05, NFR-06 |
| UR-15 | NFR-03, NFR-07 |

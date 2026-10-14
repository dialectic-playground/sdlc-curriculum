# Software Requirements Specification (SRS) — dp-sysmon

| Field | Value |
| :-- | :-- |
| Document ID | SRS-10 |
| Project | `10-sys-monitor` — System Resource Telemetry Daemonic CLI |
| Product | `dp-sysmon` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-10) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-sysmon`. For every invocation
that replays a snapshot (`--snapshot`), it is complete and precise enough that independent
implementations in any programming language produce **byte-identical** output. For live
sampling, it defines exactly which metrics are collected, from which operating-system
sources, and how they are computed, so that implementations agree on meaning and structure.
It is the authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-sysmon` reports system telemetry — CPU utilization, memory, disk usage, and the process
list — in the spirit of `top(1)` and `ps(1)`. It works in two modes:

- **Live mode** (no `--snapshot`): it polls the operating system's performance counters
  (`/proc` on Linux, Mach/sysctl interfaces on macOS, Win32 APIs on Windows) once per
  interval, for a fixed number of samples or indefinitely as a long-running ("daemonic")
  monitor.
- **Replay mode** (`--snapshot=FILE`): it reads recorded samples from a JSON Lines file
  instead of polling. Everything downstream of collection — validation, filtering, sorting,
  unit formatting, table layout, and JSON output — is identical in both modes, and in replay
  mode it is fully deterministic.

Each sample is rendered either as a fixed-width text table or as one canonical JSON object per
line (JSON Lines). Samples can additionally be appended to a recording file (`--output`),
which can later be replayed.

Out of scope: interactive full-screen terminal interfaces (cursor control, ANSI escapes,
keyboard commands), sending signals to processes, per-thread or per-core breakdowns, network
and GPU metrics, and remote collection.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR | The bytes `0x0A` and `0x0D` |
| Sample | One point-in-time telemetry record: timestamp, host name, CPU, memory, disks, processes (section 3.9) |
| Snapshot file | A JSON Lines file containing one sample per non-blank line (section 3.8) |
| Reading | A raw observation of the operating system's cumulative counters in live mode; two consecutive readings produce one sample |
| Code point | A Unicode scalar value. Widths and truncation in this SRS count code points, not bytes and not terminal cells |
| `S(text)` | *text* with every code point in U+0000–U+001F and U+007F–U+009F replaced by `?` (FR-12) |
| `T(text, W)` | *text* if it has at most W code points; otherwise its first W−3 code points followed by `...` (FR-12) |
| `ROUND1(x)` | One-decimal rendering of a binary64 value (section 3.10) |
| `PCT(a, b)` | One-decimal percentage of two integers (section 3.10) |
| `HUMAN(n)` | Binary-unit rendering of a byte count (section 3.10) |
| Path | A dotted/indexed member name used in diagnostics, for example `cpu.percent` or `processes[3].pid`; array indexes are 0-based |
| MAXINT | 9007199254740991 (2^53 − 1), the largest value of every integer field |

### 1.4 References
- URD-10: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- RFC 8259, *The JavaScript Object Notation (JSON) Data Interchange Format*
- IEEE 754-2008, binary64 floating-point format
- JSON Lines, <https://jsonlines.org/>

## 2. Overall description

### 2.1 Product perspective
`dp-sysmon` is a standalone executable. Its interfaces are the command line, an optional
snapshot file (or standard input), an optional recording file, standard output, standard
error, the exit status, and — in live mode only — the operating system's telemetry interfaces.
It is the last of the system-level tools (Projects 00–10) and the only curriculum tool whose
primary input is the running system itself.

### 2.2 Product functions
1. Collect live telemetry on Linux, macOS, and Windows, once or repeatedly at an interval.
2. Replay recorded telemetry from a snapshot file or standard input.
3. Validate snapshot samples strictly and report the first problem with its line number.
4. Filter, sort, and limit the process list.
5. Render each sample as a fixed-width table or as canonical JSON Lines.
6. Append samples to a recording file that can itself be replayed.
7. Display help and version information, and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior and the definition of each metric.
- Live-mode values (timestamps, host names, process IDs, utilization) depend on the machine
  and the moment. They are therefore verified by integration and schema tests, not by the
  byte-exact black-box suites (section 7).

### 2.4 Assumptions
- Snapshot files are UTF-8 JSON Lines, typically produced by `dp-sysmon --format=json` or
  `--output`.
- The terminal or consumer accepts UTF-8. Table output counts code points, so East Asian
  wide characters may occupy two terminal cells while counting as one.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-sysmon [-s FILE] [-f table|json] [-k cpu|mem|pid|name] [-n N] [-m TEXT]
          [-i SECS] [-c N] [-o FILE]
dp-sysmon --help
dp-sysmon --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-s` | `--snapshot` | FILE (required, non-empty) | live mode | Replay samples from FILE; `-` means standard input |
| `-f` | `--format` | `table` or `json` | `table` | Output format of standard output |
| `-k` | `--sort` | `cpu`, `mem`, `pid`, or `name` | `cpu` | Process ordering (FR-08) |
| `-n` | `--top` | N, decimal 0–1000000 | no limit | Show at most N processes per sample (FR-09) |
| `-m` | `--filter` | TEXT (may be empty) | no filter | Keep only processes whose name contains TEXT (FR-07) |
| `-i` | `--interval` | SECS, decimal 0.1–86400 | `1` | Seconds between live samples (FR-15) |
| `-c` | `--count` | N, decimal 0–1000000 | `1` live, `0` replay | Stop after N samples; `0` means no limit (FR-06) |
| `-o` | `--output` | FILE (required, non-empty) | none | Also append each sample as a JSON line to FILE (FR-14) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, attached values, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. For example, `-kmem -n3`, `-k mem -n 3`, and `--sort=mem --top 3` are equivalent.
Every option takes a value, so bundles such as `-kpid` attach the rest of the token as the
value.

### 3.3 Operands
`dp-sysmon` accepts **no operands**.

### 3.4 Standard input
Read only when `--snapshot=-` is given (CONV-26); it is then the snapshot file.

### 3.5 Standard output
One rendered block per sample, in the selected format (sections 3.11, 3.12). Nothing else.

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every requested sample was produced, or `--help` / `--version` was handled |
| 1 | Runtime failure: a file could not be opened, read, or written; an invalid snapshot sample; a snapshot with no samples; input file is output file |
| 2 | Usage error (CONV-13, CONV-14) |

When interrupted (SIGINT, Ctrl-C) during live sampling, the tool stops without a diagnostic;
its exit status is 130 or the platform's status for termination by that signal.

### 3.8 Snapshot file format (line layer)

1. The file is a sequence of bytes split into **lines** at each LF. The bytes after the last
   LF, if any, form a final line; a file ending in LF has no empty final line. Lines are
   numbered from 1, counting every line, including blank ones.
2. One CR immediately before the LF (or at the end of the final line) is removed. CRLF files
   are therefore accepted.
3. A line consisting only of the bytes SP (`0x20`), HT (`0x09`), and CR — including an empty
   line — is **blank** and is skipped.
4. Every other line MUST be exactly one JSON text (RFC 8259): UTF-8 encoded, with optional
   JSON whitespace before and after the value, and with these additional restrictions. A line
   that violates any of them is **invalid JSON**:
   - The bytes MUST be valid UTF-8. A byte-order mark (`EF BB BF`) is not JSON whitespace and
     makes the line invalid.
   - No object may contain two members with the same name (names compared after escape
     decoding).
   - No string (member name or value) may contain a `\u` escape that encodes an unpaired
     surrogate (U+D800–U+DFFF not forming a valid pair).
   - The nesting depth MUST NOT exceed 64. A top-level array or object has depth 1, and each
     array or object nested inside another adds 1.
   - `NaN`, `Infinity`, comments, trailing commas, single-quoted strings, and any other
     extension to RFC 8259 are invalid.
5. The JSON value on the line is then validated against the sample schema (section 3.9).

### 3.9 Sample schema

A sample is a JSON object with the members below. Members not listed are **ignored** at any
level (they need only be syntactically valid JSON). The order of members in the input does not
matter.

| Path | JSON type | `null` allowed | Constraint |
| :-- | :-- | :-- | :-- |
| `timestamp` | string | no | any string (live mode writes `YYYY-MM-DDTHH:MM:SSZ`, UTC) |
| `hostname` | string | no | any string |
| `cpu` | object | no | — |
| `cpu.count` | number (integer) | yes | 1 ≤ value ≤ MAXINT; number of logical CPUs |
| `cpu.percent` | number | yes | 0 ≤ value ≤ 100; system-wide busy percentage |
| `memory` | object | no | — |
| `memory.total_bytes` | number (integer) | yes | 0 ≤ value ≤ MAXINT |
| `memory.available_bytes` | number (integer) | yes | 0 ≤ value ≤ MAXINT; if both are non-null, ≤ `memory.total_bytes` |
| `disks` | array of objects | no | may be empty |
| `disks[i].mount` | string | no | any string (mount point or drive root) |
| `disks[i].total_bytes` | number (integer) | no | 0 ≤ value ≤ MAXINT |
| `disks[i].used_bytes` | number (integer) | no | 0 ≤ value ≤ MAXINT and ≤ `disks[i].total_bytes` |
| `processes` | array of objects | no | may be empty |
| `processes[i].pid` | number (integer) | no | 0 ≤ value ≤ MAXINT; unique within the sample |
| `processes[i].name` | string | no | any string, including empty |
| `processes[i].cpu_percent` | number | yes | 0 ≤ value ≤ 1000000; percent of **one** CPU, so it may exceed 100 |
| `processes[i].rss_bytes` | number (integer) | yes | 0 ≤ value ≤ MAXINT; resident set size |

**Number interpretation.** Every JSON number is converted to the nearest IEEE 754 binary64
value (round to nearest, ties to even). An *integer* field accepts any number whose converted
value is finite, integral, and within the constraint, so `2048`, `2048.0`, and `2.048e3` are
all the integer 2048, while `1.5` is not an integer. A *percent* field accepts any number whose
converted value is finite and within the constraint; `-0` and `-0.0` equal 0 and are accepted.
Numbers whose magnitude overflows binary64 convert to infinity and are therefore out of range.
Integer arithmetic on integer fields never needs more than 64 bits when performed as specified
in section 3.10.

**Validation order.** Members are checked in exactly this order, and the **first** violation is
reported (FR-04):

1. The value is an object; otherwise `sample is not a JSON object`.
2. `timestamp`, `hostname`, `cpu`, `cpu.count`, `cpu.percent`, `memory`,
   `memory.total_bytes`, `memory.available_bytes`, then the cross-check
   `memory.available_bytes` ≤ `memory.total_bytes`.
3. `disks`; then for each element in array order: the element is an object, `mount`,
   `total_bytes`, `used_bytes`, then the cross-check `used_bytes` ≤ `total_bytes`.
4. `processes`; then for each element in array order: the element is an object, `pid`, the
   uniqueness check (the pid equals no pid of an earlier element), `name`, `cpu_percent`,
   `rss_bytes`.

For each member, the checks are, in order: present (else `missing member`), of the right JSON
type with `null` permitted only where the table says so (else `invalid type`), and within its
constraint (else `invalid value`). An array element that is not an object reports
`invalid type` with the element path, for example `disks[2]`. A container of the wrong type
(for example `"cpu": 5`) is reported before any of its members.

### 3.10 Numeric formatting

All numbers in output are plain ASCII decimal with no digit grouping, no leading `+`, and no
exponent (CONV-06).

**`ROUND1(x)`** (percent fields). Let *t* be the integer nearest to 10·*x*, computed from the
**exact** value of the binary64 *x* (not from a rounded product); when 10·*x* is exactly halfway
between two integers, choose the even one. The result is ⌊*t*/10⌋, `.`, and *t* mod 10 — always
exactly one fractional digit. Negative zero renders as `0.0`. Examples:

| Input number | binary64 exact value relative to the tie | `ROUND1` |
| :-- | :-- | :-- |
| `42.31` | — | `42.3` |
| `12.46` | — | `12.5` |
| `12.25` | exactly a tie | `12.2` |
| `33.75` | exactly a tie | `33.8` |
| `0.15` | slightly below 0.15 | `0.1` |
| `0.05` | slightly above 0.05 | `0.1` |
| `99.95` | slightly above 99.95 | `100.0` |
| `-0.0` | zero | `0.0` |

Implementations must not compute `ROUND1` as `round(x * 10) / 10` in floating point, because the
product is itself rounded (`0.15 * 10` is exactly `1.5` in binary64). A correctly rounded
fixed-point formatter (`%.1f`-style formatting that rounds the exact binary value, ties to even)
or exact decimal arithmetic satisfies the definition.

**`PCT(a, b)`** (shares of integers, `b` > 0). Let *q* and *r* be the quotient and remainder of
the integer division (1000·*a*) ÷ *b*. If 2*r* > *b*, or 2*r* = *b* and *q* is odd, add 1 to *q*.
The result is ⌊*q*/10⌋, `.`, *q* mod 10. (With *a* ≤ *b* ≤ MAXINT, 1000·*a* fits in a signed
64-bit integer.) Examples: `PCT(1, 2000)` = `0.0` (tie, even), `PCT(3, 2000)` = `0.2` (tie,
odd → up), `PCT(11, 16)` = `68.8`.

**`HUMAN(n)`** (byte counts, 0 ≤ *n* ≤ MAXINT). Units are `B`, `KiB` (1024), `MiB` (1024²),
`GiB` (1024³), `TiB` (1024⁴), and `PiB` (1024⁵).

1. If *n* < 1024, the result is the decimal *n*, a space, and `B` (for example `0 B`, `1023 B`).
2. Otherwise let *k* be the largest exponent in 1…5 with *n* ≥ 1024^*k*.
3. Let *q*, *r* be the quotient and remainder of (10·*n*) ÷ 1024^*k*. If 2*r* > 1024^*k*, or
   2*r* = 1024^*k* and *q* is odd, add 1 to *q*.
4. If *q* ≥ 10240 and *k* < 5, increase *k* by 1 and repeat step 3.
5. The result is ⌊*q*/10⌋, `.`, *q* mod 10, a space, and the unit for *k*.

Examples: `1024` → `1.0 KiB`; `1075` → `1.0 KiB`; `1126` → `1.1 KiB`; `1280` → `1.2 KiB` (tie,
even); `1536` → `1.5 KiB`; `1048575` → `1.0 MiB` (would be `1024.0 KiB`); `1073741823` →
`1.0 GiB`; `9007199254740991` → `8.0 PiB`. A `HUMAN` result never exceeds 10 characters.

### 3.11 Table format (`--format=table`)

For each sample the tool writes the **sample block** below. Before every block except the
first, it writes one empty line (a single LF). Every line ends in LF. In the layouts, `␠`
stands for one space; labels are padded with spaces to a width of 11 characters.

```text
Host:␠␠␠␠␠␠<HOST>
Time:␠␠␠␠␠␠<TIME>
CPU:␠␠␠␠␠␠␠<CPU> busy; logical CPUs: <COUNT>
Memory:␠␠␠␠<USED> used of <TOTAL> (<SHARE>); <AVAIL> available
Processes:␠<N> total; <M> shown

MOUNT                       USED       TOTAL    USE%
<disk rows>

    PID    CPU%         RSS  NAME
<process rows>
```

Summary values (a `-` stands for a value that is unknown):

| Field | Value |
| :-- | :-- |
| `<HOST>` | `S(hostname)`, or `-` if `hostname` is empty |
| `<TIME>` | `S(timestamp)`, or `-` if `timestamp` is empty |
| `<CPU>` | `ROUND1(cpu.percent)` followed by `%`, or `-` if null |
| `<COUNT>` | `cpu.count` in decimal, or `-` if null |
| `<USED>` | `HUMAN(total_bytes − available_bytes)`, or `-` if either memory field is null |
| `<TOTAL>` | `HUMAN(memory.total_bytes)`, or `-` if null |
| `<SHARE>` | `PCT(total − available, total)` followed by `%`, or `-` if either field is null or `total_bytes` is 0 |
| `<AVAIL>` | `HUMAN(memory.available_bytes)`, or `-` if null |
| `<N>` | number of processes in the sample, before filtering |
| `<M>` | number of process rows written (after FR-07 … FR-09) |

The disk header line and the process header line are exactly the literal text shown above:
`MOUNT`, 15 spaces, 2 spaces, `USED` right-aligned in 10 characters, 2 spaces, `TOTAL`
right-aligned in 10, 2 spaces, `USE%` right-aligned in 6; and `PID` right-aligned in 7, 2
spaces, `CPU%` right-aligned in 6, 2 spaces, `RSS` right-aligned in 10, 2 spaces, `NAME`. The
disk header and the process header are written even when there are no rows.

**Disk rows**, one per disk in byte-wise ascending order of the UTF-8 encoding of `mount`
(disks with equal mounts keep their input order). Each row is:
`T(S(mount), 20)` left-aligned and padded with spaces to 20 code points; 2 spaces;
`HUMAN(used_bytes)` right-aligned in 10; 2 spaces; `HUMAN(total_bytes)` right-aligned in 10;
2 spaces; `PCT(used_bytes, total_bytes)` right-aligned in 6, or `-` right-aligned in 6 when
`total_bytes` is 0.

**Process rows**, one per selected process in the order of FR-07 … FR-09. Each row is:
`pid` in decimal right-aligned in 7; 2 spaces; `ROUND1(cpu_percent)` (or `-`) right-aligned in
6; 2 spaces; `HUMAN(rss_bytes)` (or `-`) right-aligned in 10; then, only if `T(S(name), 24)` is
non-empty, 2 spaces and `T(S(name), 24)`. A process with an empty name therefore ends after the
RSS field, with no trailing spaces. "Right-aligned in *W*" means left-padded with spaces to *W*
code points; a value longer than *W* is written in full and shifts the rest of the row.

Example (one disk, two processes):

```text
Host:      alpha
Time:      2026-03-14T09:26:53Z
CPU:       37.5% busy; logical CPUs: 8
Memory:    10.0 GiB used of 16.0 GiB (62.5%); 6.0 GiB available
Processes: 8 total; 2 shown

MOUNT                       USED       TOTAL    USE%
/                       50.0 GiB   100.0 GiB    50.0

    PID    CPU%         RSS  NAME
   1203    42.3     1.5 GiB  firefox
   1350    12.5   256.0 MiB  Xorg
```

### 3.12 JSON format (`--format=json` and `--output`)

Each sample is written as exactly one line: a compact JSON object (no whitespace outside
strings) followed by LF, with members in this fixed order:

```text
{"timestamp":<str>,"hostname":<str>,"cpu":{"count":<int>,"percent":<pct>},"memory":{"total_bytes":<int>,"available_bytes":<int>},"disks":[<disk>,...],"processes":[<proc>,...]}
<disk> = {"mount":<str>,"total_bytes":<int>,"used_bytes":<int>}
<proc> = {"pid":<int>,"name":<str>,"cpu_percent":<pct>,"rss_bytes":<int>}
```

- `<int>` is the integer value in decimal (an input of `2048.0` is written `2048`), or `null`.
- `<pct>` is `ROUND1(value)` (always one fractional digit, for example `0.0`, `100.0`), or
  `null`.
- `<str>` is a JSON string: `"`, then each code point of the value, then `"`. `"` is written
  `\"`, `\` is written `\\`, U+0008 `\b`, U+000C `\f`, U+000A `\n`, U+000D `\r`, U+0009 `\t`;
  every other code point below U+0020 is written `\u00XX` with two **lowercase** hexadecimal
  digits. All other code points, including `/`, U+007F, and non-ASCII characters, are written
  as their raw UTF-8 bytes.
- Arrays are written with `,` between elements and nothing else; an empty array is `[]`.
- `disks` are in the same order as the table rows (section 3.11). `processes` contain only the
  processes selected by FR-07 … FR-09, in that order.
- Members of the input that are not part of the schema are not written.

Because the JSON output conforms to section 3.9, every JSON line `dp-sysmon` writes is a valid
snapshot line, and replaying it with the same `--sort` reproduces it byte for byte.

### 3.13 Live telemetry sources

Live mode collects the metrics below. An implementation MAY use any interface that yields the
defined quantity (for example native APIs instead of the listed utilities, or the Windows
Performance Data Helper (PDH) counters), provided the result follows these definitions. A value
that cannot be obtained is `null` (or the entry is omitted, where stated); collection never
makes the tool fail.

| Metric | Linux | macOS | Windows |
| :-- | :-- | :-- | :-- |
| `timestamp` | UTC wall-clock time of the reading, `YYYY-MM-DDTHH:MM:SSZ`, truncated to whole seconds | same | same |
| `hostname` | `uname(2)` node name | `uname(2)` node name | `GetComputerNameExW(ComputerNameDnsHostname)`; empty string if unavailable |
| `cpu.count` | number of `cpuN` lines in `/proc/stat` | `sysctl hw.logicalcpu` | `GetActiveProcessorCount(ALL_PROCESSOR_GROUPS)` |
| CPU counters | first line of `/proc/stat` (`cpu`): busy = user+nice+system+irq+softirq+steal; total = busy + idle + iowait | `host_statistics(HOST_CPU_LOAD_INFO)`: busy = user+system+nice; total = busy + idle | `GetSystemTimes`: total = kernel + user (kernel includes idle); busy = total − idle |
| `memory.total_bytes` | `MemTotal` of `/proc/meminfo` × 1024 | `sysctl hw.memsize` | `GlobalMemoryStatusEx` `ullTotalPhys` |
| `memory.available_bytes` | `MemAvailable` × 1024 (null if absent) | (free + inactive + speculative pages) × page size, from `host_statistics64(HOST_VM_INFO64)` or `vm_stat` | `ullAvailPhys` |
| `disks` | entries of `/proc/self/mounts` whose device field begins with `/`, octal escapes (`\040`) decoded, one entry per mount point (the last mount wins) | local file systems whose device begins with `/dev/`, excluding those mounted `nobrowse` (`getmntinfo(3)` or `mount(8)`) | drive roots (for example `C:\`) whose `GetDriveTypeW` is `DRIVE_FIXED` |
| disk sizes | `statvfs`: total = `f_blocks`×`f_frsize`; used = (`f_blocks`−`f_bfree`)×`f_frsize` | same as Linux | `GetDiskFreeSpaceExW`: total = `TotalNumberOfBytes`; used = total − `TotalNumberOfFreeBytes` |
| process list | every numeric directory in `/proc` | every process (`proc_listallpids` or `ps -A`) | `CreateToolhelp32Snapshot` (`TH32CS_SNAPPROCESS`) |
| `name` | `comm`: text between the first `(` and the **last** `)` of `/proc/<pid>/stat` | last path component of the executable (`proc_name`, or `ps -o comm`) | `szExeFile` of the Toolhelp entry |
| process CPU time | `utime` + `stime` (fields 14, 15 of `/proc/<pid>/stat`) ÷ `sysconf(_SC_CLK_TCK)` | user + system time (`proc_pidinfo(PROC_PIDTASKINFO)` or `ps -o time`) | `GetProcessTimes` kernel + user |
| process identity | pid + `starttime` (field 22) | pid | pid + creation time |
| `rss_bytes` | `/proc/<pid>/statm` field 2 × page size | resident size (`proc_pidinfo` or `ps -o rss` × 1024) | `WorkingSetSize` from `GetProcessMemoryInfo` |

Additional rules:

- A disk whose size query fails is omitted. A process that exits during enumeration is
  omitted. A process whose details are denied (for example a protected Windows process that
  `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` refuses) is still listed with its pid and
  name, and the denied fields are `null`.
- OS-provided names that are not valid UTF-8 (POSIX) or contain unpaired surrogates (Windows
  UTF-16) are converted with each invalid sequence replaced by U+FFFD.
- `memory.available_bytes` is clamped to `memory.total_bytes`; values above MAXINT are `null`.
- Every live sample satisfies section 3.9, so a recording made with `--output` can be replayed.

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.

**FR-01: Operating mode.**
With `--snapshot=FILE`, the tool MUST take samples from FILE (section 3.8) and MUST NOT query
the operating system for telemetry. Without it, the tool MUST sample the local system (FR-15 …
FR-18). `--interval` is validated in both modes but has no effect in replay mode: samples are
replayed without waiting.
*AC:* `dp-sysmon -s lazy.jsonl -c 1 -i 5 -f json` finishes immediately with one sample.
*(UR-01, UR-02)*

**FR-02: Option values.**
After the argument scan (CONV-12), the tool MUST check operands and then option values in this
order: operands (FR-21), `--snapshot`, `--format`, `--sort`, `--top`, `--filter`, `--interval`,
`--count`, `--output`. The first invalid value is reported as
`dp-sysmon: invalid argument '<VALUE>' for '<OPTION>'` with exit status 2 (CONV-13), where
`<OPTION>` is the option as the user wrote it. Valid values are:
- `--snapshot`, `--output`: any non-empty string.
- `--format`: exactly `table` or `json`; `--sort`: exactly `cpu`, `mem`, `pid`, or `name`
  (case-sensitive).
- `--top`: 1 or more ASCII digits, value 0–1000000. `--count`: same syntax, value 0–1000000.
  Leading zeros are allowed.
- `--filter`: any string, including the empty string.
- `--interval`: matches `[0-9]+(\.[0-9]+)?` and, read as an exact decimal, lies in
  0.1–86400 inclusive (`1.`, `.5`, `1e2`, and `0.05` are invalid).

Because values are checked after the scan, `dp-sysmon --sort=bad --help` prints the help.
*AC:* `dp-sysmon -s basic.jsonl --sort=size` → `dp-sysmon: invalid argument 'size' for
'--sort'`, exit 2. *(UR-09, UR-12)*

**FR-03: Snapshot reading.**
The tool MUST open FILE (standard input for `-`) for binary reading. If it cannot, it MUST
report `dp-sysmon: <FILE>: <reason>` with the CONV-16 reason (a directory gives
`Is a directory` on every platform) and exit 1. It MUST then process the file **one line at a
time** per section 3.8: each sample is validated, rendered, and written (FR-22) before the next
line is read. Blank lines are skipped. Memory use MUST NOT grow with the number of samples.
*AC:* `dp-sysmon --snapshot=absent.jsonl` → `dp-sysmon: absent.jsonl: No such file or
directory`, exit 1; a CRLF file with blank lines replays correctly from standard input.
*(UR-02, UR-10)*

**FR-04: Snapshot validation.**
When a non-blank line is invalid JSON (section 3.8) or violates the schema (section 3.9), the
tool MUST report the first violation as `dp-sysmon: <FILE>:<LINE>: <detail>` (section 6), stop
reading, and exit 1. Samples on earlier lines have already been written and remain written.
`<FILE>` is the operand as given (`-` for standard input); `<LINE>` is the line number.
*AC:* `dp-sysmon -s broken.jsonl -f json` → the first sample on stdout, then
`dp-sysmon: broken.jsonl:2: invalid JSON`, exit 1. *(UR-10, UR-09)*

**FR-05: Empty snapshot.**
If the snapshot reaches end of file without containing any sample, the tool MUST report
`dp-sysmon: <FILE>: no samples` and exit 1.
*AC:* a file of blank lines gives that diagnostic. *(UR-10)*

**FR-06: Sample count.**
`--count=N` with N ≥ 1 MUST stop after N samples have been written; in replay mode, no further
line is read (so problems after the N-th sample are not detected). `--count=0` means no limit:
replay continues to end of file, and live sampling continues until interrupted. The default is
1 in live mode and 0 in replay mode. In replay mode, reaching end of file before N samples is
not an error.
*AC:* `dp-sysmon -s series.jsonl --count=2` → two sample blocks; `dp-sysmon -s lazy.jsonl -c 1`
→ exit 0 although line 2 is invalid. *(UR-03, UR-04)*

**FR-07: Process filter.**
With `--filter=TEXT`, only processes whose `name` contains TEXT as a contiguous substring are
kept. The comparison folds ASCII letters only (`A`–`Z` equal `a`–`z`); every other code point
must match exactly. The empty TEXT matches every name. Filtering uses the original name, before
FR-12 sanitization and truncation.
*AC:* `--filter=SH` keeps `bash`, `sshd`, `zsh`, and `SSH-agent`. *(UR-05)*

**FR-08: Process order.**
After filtering, processes MUST be sorted by the `--sort` key:
- `cpu`: `ROUND1(cpu_percent)` descending, `null` after all numbers;
- `mem`: `rss_bytes` descending, `null` after all numbers;
- `pid`: `pid` ascending;
- `name`: byte-wise ascending order of the UTF-8 encoding of `name` (case-sensitive, so
  `SSH-agent` sorts before `bash`).
Ties are broken by `pid` ascending, which makes the order total. The `cpu` key compares the
one-decimal values that are displayed, so `12.46` and `12.5` tie.
*AC:* with `--sort=mem --top=6`, `bash` (pid 977) is shown and `zsh` (pid 2048, equal RSS) is
not. *(UR-05)*

**FR-09: Process limit.**
With `--top=N`, only the first N processes of the sorted list are kept. `--top=0` keeps none
(the summary and both headers are still written). Without `--top`, all are kept.
*AC:* `--top=6` on an 8-process sample shows 6 rows and `Processes: 8 total; 6 shown`.
*(UR-05)*

**FR-10: Table output.**
With `--format=table` (the default), each sample MUST be written exactly as specified in
section 3.11. Table output MUST contain no ANSI escape or other control sequences (CONV-06).
*AC:* public tests 01 and 03 … 06 match byte for byte. *(UR-06, UR-08)*

**FR-11: JSON output.**
With `--format=json`, each sample MUST be written as one line exactly as specified in section
3.12.
*AC:* `dp-sysmon --snapshot basic.jsonl --format=json` matches byte for byte; the unknown input
member `uptime_seconds` is not written. *(UR-07, UR-08)*

**FR-12: Text sanitization and truncation (table only).**
In table output, host name, timestamp, mount points, and process names MUST be passed through
`S()`, replacing each code point in U+0000–U+001F and U+007F–U+009F with `?`. Mount points are
then shortened with `T(·, 20)` and process names with `T(·, 24)`: a value longer than the limit
becomes its first limit−3 code points followed by `...`. Values are otherwise written verbatim
in UTF-8, including trailing spaces. JSON output is never sanitized or truncated; it escapes
per section 3.12.
*AC:* a 25-code-point name `abcdefghijklmnopqrstuvwxy` is shown as `abcdefghijklmnopqrstu...`;
a 24-code-point name is shown in full; `tab<TAB>here` is shown as `tab?here`. *(UR-06, UR-13)*

**FR-13: Units and derived values.**
Byte counts in table output MUST use `HUMAN`, percentages of integers `PCT`, and percent fields
`ROUND1` (section 3.10). Memory "used" is `total_bytes − available_bytes`.
*AC:* public test 05 shows every unit boundary in section 3.10, including `1048575` →
`1.0 MiB` and a zero-sized disk with `USE%` `-`. *(UR-06)*

**FR-14: Recording (`--output`).**
With `--output=FILE`, after the snapshot (if any) has been opened, the tool MUST open FILE for
appending, creating it if it does not exist, before reading any sample. For every sample, after
writing it to standard output, the tool MUST append the sample's JSON line (section 3.12, with
the same process selection) to FILE, regardless of `--format`. Failures:
- FILE cannot be opened: `dp-sysmon: <FILE>: <reason>` (CONV-16; a directory gives
  `Is a directory`), exit 1, nothing written to standard output.
- FILE is the same file as the snapshot input (same device and file ID — inode on POSIX,
  volume serial number and file index on Windows — including when the snapshot is standard
  input redirected from FILE): `dp-sysmon: <FILE>: input file is output file`, exit 1, before
  any sample is read. This prevents a replay from reading its own appended records forever.
- A write to FILE fails: `dp-sysmon: <FILE>: <reason>`, exit 1, after the current sample's
  standard-output block.
*AC:* recording with `-o rec.jsonl` and replaying `rec.jsonl` with the same `--sort`
reproduces the recorded lines; `dp-sysmon -s rec.jsonl -o rec.jsonl` → `dp-sysmon: rec.jsonl:
input file is output file`, exit 1. *(UR-04, UR-11)*

**FR-15: Live sampling schedule.**
In live mode, the tool MUST take a baseline reading R0 at start-up, then reading R*k* at
start + *k*·SECS on a monotonic clock (*k* = 1, 2, …), where SECS is `--interval` (default 1).
If a reading finishes late, the next one is taken immediately, without accumulating drift.
Sample *k* is computed from R*k*−1 and R*k* and is written as soon as it is computed. With the
default `--count=1`, the tool therefore produces one sample after about one interval.
*AC:* `dp-sysmon --count=3 --interval=0.2 --format=json` writes 3 lines in about 0.6 s and
exits 0. *(UR-01, UR-03)*

**FR-16: Live CPU utilization.**
`cpu.percent` MUST be 100 × Δbusy ÷ Δtotal of the CPU counters (section 3.13) between the two
readings, clamped to 0–100, or `null` when Δtotal is 0 or the counters are unavailable.
`processes[i].cpu_percent` MUST be 100 × Δ(process CPU seconds) ÷ Δ(monotonic seconds between
the readings), clamped to 0–1000000. It is `null` when the process (same pid and, where
available, same start time) was not present in the previous reading, or when its CPU time
cannot be read. Values are then rounded with `ROUND1` like replayed values.
*AC:* integration test — a busy-looping child process reports approximately 100.0.
*(UR-01, UR-14)*

**FR-17: Live process enumeration.**
The process list MUST contain every process the platform enumerates, with `pid` and `name`
always present. Processes that exit during collection are omitted; fields that cannot be read
because of permissions are `null` (section 3.13). Insufficient privileges MUST NOT cause a
diagnostic or a non-zero exit status.
*AC:* integration test — run as an unprivileged user, the list includes the tool's own pid and
exit status is 0. *(UR-01, UR-14)*

**FR-18: Live system metrics.**
`timestamp`, `hostname`, `cpu.count`, `memory`, and `disks` MUST be collected as defined in
section 3.13. Unavailable scalar values are `null` (`hostname` falls back to the empty string);
unavailable disks are omitted.
*AC:* integration test — `dp-sysmon --format=json` output replays successfully with
`dp-sysmon -s - -f json`, and `memory.total_bytes` is non-null on all three platforms.
*(UR-01, UR-14)*

**FR-19: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12.
*AC:* `dp-sysmon --help` matches the user manual exactly. *(UR-12)*

**FR-20: Version.**
`--version` MUST write `dp-sysmon (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02),
without opening any file.
*AC:* `dp-sysmon -s absent.jsonl --sort=bad --version` prints the version, exit 0. *(UR-12)*

**FR-21: Operands and malformed options.**
Any operand MUST produce `dp-sysmon: extra operand '<first operand>'` and exit status 2.
Unknown options, missing option arguments, and arguments supplied to `--help` or `--version`
MUST be reported with the CONV-13 messages and exit status 2. Long options MUST NOT be
abbreviated (CONV-08).
*AC:* `dp-sysmon -s basic.jsonl extra`, `dp-sysmon --top`, and `dp-sysmon -z` each exit 2 with
the CONV-13 message. *(UR-09, UR-12)*

**FR-22: Output discipline.**
On a usage error, nothing is written to standard output and no file is opened or created
(CONV-12). Each sample's standard-output block and its `--output` record MUST be flushed before
the next sample is read or collected, so that a consumer of a long-running monitor sees each
sample as soon as it is produced. Standard output contains only rendered samples.
*AC:* stdout is empty in every exit-2 test; in live mode with `--count=0`, each sample appears
on a pipe within one interval. *(UR-04, UR-09)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Replay-mode output MUST be byte-identical on Linux, macOS, and Windows, and every generated line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform design | Live collection MUST be isolated behind one platform-neutral interface (a "reading" of cumulative counters) with one back end per OS: Linux `/proc`, macOS Mach/sysctl (or the listed utilities), Windows Win32/PDH. Validation, selection, formatting, and rendering MUST be shared by both modes and contain no OS-specific code. | Design review |
| NFR-03 | Performance (replay) | Replaying a 50 MiB snapshot (about 1,000 samples of 300 processes) to `/dev/null` MUST take under 5 s for a natively compiled build (15 s for an interpreted runtime) on CI hardware. Peak memory MUST be bounded by a small multiple of the longest line, independent of the number of samples (FR-03). | Measurement |
| NFR-04 | Performance (live) | One live reading of a system with 1,000 processes MUST consume under 250 ms of CPU time. In `--count=0` mode, memory use MUST stay constant over time (no per-sample growth beyond the current and previous reading). | Measurement |
| NFR-05 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or snapshot content, including deeply nested, truncated, or non-UTF-8 lines (CONV-24). | Unit + black-box tests, fuzzing |
| NFR-06 | Maintainability | Option parsing, snapshot decoding/validation, live collection, process selection, number formatting, and rendering MUST be separate units. | Design review |
| NFR-07 | Testability | `ROUND1`, `PCT`, `HUMAN`, `S`, `T`, the sort comparator, and both renderers MUST be pure functions covered by unit tests; live-mode logic that turns two readings into a sample MUST be testable with synthetic readings. | Code review |
| NFR-08 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-09 | Security | The tool MUST NOT require elevated privileges, MUST NOT modify any file except the `--output` file (append only), MUST NOT read environment variables, and MUST NOT use the network. On macOS it MAY run the system utilities `ps`, `sysctl`, `vm_stat`, and `mount` by absolute path; no other subprocesses are permitted. | Inspection |
| NFR-10 | Determinism | No output may depend on locale, terminal type, or time zone (CONV-06); live timestamps are always UTC. | Inspection, CI |

## 6. Diagnostics (complete list)

### 6.1 Usage errors
Each is followed by `Try 'dp-sysmon --help' for more information.` and exit status 2.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-sysmon: invalid option -- 'x'` |
| Unknown long option token `T` | `dp-sysmon: unrecognized option 'T'` |
| Short option `x` (`s f k n m i c o`) without an argument | `dp-sysmon: option requires an argument -- 'x'` |
| Long option `--name` without an argument | `dp-sysmon: option '--name' requires an argument` |
| `--help=…` / `--version=…` | `dp-sysmon: option '--help' doesn't allow an argument` (or `'--version'`) |
| Invalid value `V` for option `O` (FR-02) | `dp-sysmon: invalid argument 'V' for 'O'` |
| Operand `X` | `dp-sysmon: extra operand 'X'` |

### 6.2 Runtime errors
Exit status 1. `<FILE>` is the path as given (`-` for standard input), `<LINE>` the line number.

| Trigger | Exact message |
| :-- | :-- |
| Snapshot or output file cannot be opened, read, or written | `dp-sysmon: <FILE>: <reason>` with a CONV-16 reason |
| Output file is the snapshot input (FR-14) | `dp-sysmon: <FILE>: input file is output file` |
| Snapshot has no samples (FR-05) | `dp-sysmon: <FILE>: no samples` |
| Line is not valid JSON under section 3.8 | `dp-sysmon: <FILE>:<LINE>: invalid JSON` |
| Line's value is not an object | `dp-sysmon: <FILE>:<LINE>: sample is not a JSON object` |
| Required member absent | `dp-sysmon: <FILE>:<LINE>: missing member '<PATH>'` |
| Member (or array element) of the wrong JSON type, or `null` where not allowed | `dp-sysmon: <FILE>:<LINE>: invalid type for '<PATH>'` |
| Number not integral (integer fields), not finite, or outside its constraint | `dp-sysmon: <FILE>:<LINE>: invalid value for '<PATH>'` |
| `memory.available_bytes` > `memory.total_bytes` | `dp-sysmon: <FILE>:<LINE>: 'memory.available_bytes' exceeds 'memory.total_bytes'` |
| `disks[i].used_bytes` > `disks[i].total_bytes` | `dp-sysmon: <FILE>:<LINE>: 'disks[i].used_bytes' exceeds 'disks[i].total_bytes'` |
| `processes[i].pid` equals an earlier pid | `dp-sysmon: <FILE>:<LINE>: duplicate value for 'processes[i].pid'` |

Deliberate extensions of CLI-CONV: CONV-16 is extended with the tool-specific reasons
`input file is output file` and `no samples`, and with the `<FILE>:<LINE>: <detail>` form for
content errors. Because there is a single input, CONV-17 (continue after a failing operand)
does not apply: the first invalid sample ends the run. CONV-04 does not apply: snapshot content
is re-rendered, not copied.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases, all in replay mode) | FR-02 … FR-04, FR-06 … FR-13, FR-19, FR-21 |
| Black-box test (hidden, `tests/private/`, 10 cases, all in replay mode) | FR-01 … FR-14, FR-20 … FR-22 |
| Integration / schema test (written by the implementer, run on all 3 OSes; never byte-compared) | FR-15 … FR-18, NFR-02, NFR-04 |
| Unit test (written by the implementer) | FR-07, FR-08, FR-12, FR-13, section 3.10, NFR-07 |
| Inspection / review | NFR-02, NFR-03, NFR-06, NFR-09, NFR-10 |

Live mode cannot be verified byte-for-byte: its timestamps, host names, PIDs, and utilization
differ on every run and machine. The minimum integration suite for live mode is:

1. `dp-sysmon --format=json` exits 0 and writes exactly one line that parses as JSON, has the
   top-level members in the order of section 3.12, and replays without error through
   `dp-sysmon --snapshot=- --format=json`.
2. `dp-sysmon --count=3 --interval=0.2 --format=json --output=rec.jsonl` writes three lines to
   standard output, appends the same three lines to `rec.jsonl`, and takes between 0.6 s and
   2 s.
3. The process list includes the tool's own process ID with a non-empty name.
4. `dp-sysmon` (table) exits 0 and its first line starts with `Host:`.

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-sysmon --snapshot=basic.jsonl` | FR-03, FR-08 (cpu ties), FR-10, FR-13 |
| 02 | `dp-sysmon --snapshot basic.jsonl --format=json` | FR-11, section 3.9 (unknown members, member order) |
| 03 | `dp-sysmon -s basic.jsonl --sort=mem --top=6` | FR-08 (mem ties), FR-09 |
| 04 | `dp-sysmon -s basic.jsonl -k name --filter=SH` | FR-07, FR-08 (name) |
| 05 | `dp-sysmon -s units.jsonl -k pid` | FR-13, section 3.10 (`HUMAN`, `PCT` boundaries and ties) |
| 06 | `dp-sysmon -s series.jsonl --count=2` | FR-06, section 3.11 (block separation) |
| 07 | `dp-sysmon -s broken.jsonl -f json` | FR-04 (streaming: earlier sample kept) |
| 08 | `dp-sysmon --snapshot=absent.jsonl` | FR-03, CONV-16 |
| 09 | `dp-sysmon -s basic.jsonl --sort=size` | FR-02 |
| 10 | `dp-sysmon --help` | FR-19 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-15 … FR-18 |
| UR-02 | FR-01, FR-03 |
| UR-03 | FR-06, FR-15 |
| UR-04 | FR-06, FR-14, FR-22 |
| UR-05 | FR-07, FR-08, FR-09 |
| UR-06 | FR-10, FR-12, FR-13, section 3.10 |
| UR-07 | FR-11, section 3.12 |
| UR-08 | NFR-01, NFR-10, FR-10, FR-11 |
| UR-09 | FR-02, FR-21, FR-22 |
| UR-10 | FR-03, FR-04, FR-05, section 3.8, section 3.9 |
| UR-11 | FR-14, section 3.12 |
| UR-12 | FR-02, FR-19, FR-20, FR-21, CLI-CONV |
| UR-13 | FR-12, NFR-05 |
| UR-14 | FR-16, FR-17, FR-18, section 3.13, NFR-02 |
| UR-15 | NFR-03, NFR-04 |
| UR-16 | NFR-08 |

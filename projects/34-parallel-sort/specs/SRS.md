# Software Requirements Specification (SRS) — dp-sort-host, dp-sort-child

| Field | Value |
| :-- | :-- |
| Document ID | SRS-34 |
| Project | `34-parallel-sort` — Distributed Parallel Sorting & Stream Merging |
| Products | `dp-sort-host`, `dp-sort-child` (canonical names) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-34) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-sort-host` and `dp-sort-child`,
the message protocol between a host and its worker, and the concurrency and deadlock-freedom
requirements their design must meet. It is complete and precise enough that independent
implementations in any programming language produce **byte-identical** output for every
invocation. It is the authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-sort-host` reads up to 100000 integers (or generates them), keeps the first half, and
hands the rest to a **worker** that runs concurrently with it. The two halves are sorted at
the same time with selection sort; the host then merges its sorted half with the worker's
sorted stream and writes the result, one integer per line. With `--trace` it also reports, in
a deterministic order, every message exchanged with the worker and every step of the merge.
`dp-sort-child` is the worker as a standalone tool: it serves one request of the worker
protocol (FR-05) on its standard input and output, so the protocol can be used and tested on
its own. Requirements that apply to one tool name it; all others apply to both.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR | The bytes `0x0A` and `0x0D` |
| Whitespace byte | One of `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D` (CONV-32) |
| Token, line number | As defined in CONV-32 |
| Input | The bytes of the FILE operand, or of standard input; a trailing run of `0x1A` bytes is ignored (CONV-37) |
| Source | The FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Value | A 64-bit signed integer, −2⁶³ … 2⁶³−1, read with the *integer* grammar (CONV-33) |
| Data set | The *N* values `dp-sort-host` sorts, in input (or generation) order: *x*₀ … *x*_{*N*−1} |
| Host part | The first *h* = ⌊*N* / 2⌋ values of the data set, sorted by the host |
| Child part | The remaining *c* = *N* − *h* values, sorted by the worker |
| Worker | The concurrent unit of execution that serves the host's request: a thread, a process, or a running `dp-sort-child` (FR-09) |
| Channel | A one-way, ordered, lossless byte stream: the *request channel* from host to worker and the *reply channel* from worker to host |
| Message | One line on a channel: the decimal of one integer followed by LF (FR-05) |
| Request | The messages the host sends: *c*, then the child part in order |
| Reply | The messages the worker sends: the child part in non-decreasing order |
| Decimal | The canonical ASCII decimal of an integer: `-` for negative values, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06) |
| Receive | The host's taking of the next reply message from the reply channel for use in the merge (FR-11); bytes may already be buffered |
| Emit | The merge's appending of a value to the output sequence (FR-11) |

### 1.4 References
- URD-34: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains both normative help texts)
- SRS-35 (`projects/35-sort-bench/specs/SRS.md`), FR-04: the selection sort used here
- SRS-08 (`projects/08-env-run/specs/SRS.md`): portable process creation, for a worker that
  is a process
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §6.6 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-sort-host` and `dp-sort-child` are two standalone executables built from one project.
Their interfaces are the command line, the file named by the operand, standard input,
standard output, standard error, and the exit status; `dp-sort-host` also has an internal
interface, the two channels to its worker, whose messages are specified (FR-05) and made
observable by `--trace` (FR-12). They belong to the curriculum's applications-programming
track (Projects 11–52) and adapt §6.6 of Johnsonbaugh & Kalin, *Applications Programming in
ANSI C*, in which a host process and a child process on a network of processors sort two
halves of an array in parallel and the host merges the results.

### 2.2 Product functions
1. `dp-sort-host`: read up to 100000 integers from a file or standard input, or generate them
   with the CONV-38 generator, and validate them all before any sorting starts.
2. `dp-sort-host`: split the data set, send the child part to a concurrent worker, sort the
   host part while the worker sorts the child part, and merge the two sorted streams.
3. `dp-sort-host`: write the merged values; with `--trace`, write the message and merge trace.
4. `dp-sort-child`: serve one request of the worker protocol on its standard streams.
5. Both: report data errors with a line number and unreadable files with fixed messages;
   display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through FR-09, FR-10, and NFR-05, the
  concurrent structure of `dp-sort-host`.
- Both parts MUST be sorted with the selection sort of FR-08, implemented by the project; a
  library sort MUST NOT be used. The merge MUST be the linear two-way merge of FR-11.

### 2.4 Assumptions
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- The host and its worker run on the same machine. Distribution over a network is out of
  scope; the channels model it.

### 2.5 Relationship to the textbook program (informative)
The textbook programs of §6.6 run on a transputer network: the host fills an array, sends the
child the size of its part and then its elements over a CSP channel, sorts its own part with
selection sort while the child sorts the other, and merges its sorted part with the elements
the child sends back. The split is *hostsize* = ⌊*N* / 2⌋ and *childsize* = *N* − *hostsize*.
This project keeps:

- the two roles and their names (host and child), the split ⌊*N* / 2⌋ / *N* − ⌊*N* / 2⌋, and
  the order of the request: the size first, then the elements;
- selection sort on both sides, run concurrently;
- the reply as a stream of sorted elements, consumed by a pipelined two-way merge that
  receives the next child element only when it needs it, and drains whichever side remains;
- the output: the merged values in non-decreasing order.

It changes the following, for the reasons given:

- **Channels.** Transputer channels do not exist on the three target platforms. The channels
  are byte streams carrying one decimal integer per line (FR-05) — pipes between threads or
  processes — so the same protocol works for a thread, for a process, and for the standalone
  `dp-sort-child`, and can be typed by hand.
- **The worker as a tool.** `dp-sort-child` serves the protocol on its standard streams, so
  the worker can be tested without the host (FR-06, FR-07). Because locating a sibling
  executable portably is hard under a test harness and an installer, `dp-sort-host` may run
  the worker as a thread, a process, or `dp-sort-child` (FR-09); the protocol and every
  observable byte are the same.
- **Data.** The textbook sorted a small fixed array. `dp-sort-host` reads integers from a file
  or standard input, or generates them with the portable generator of CONV-38 (`--random`,
  `--seed`), and validates them all before the worker starts (FR-02, FR-14).
- **Observability.** With `--trace`, the messages and merge steps are written to standard error
  in an order that depends only on the data (FR-12), so the protocol, the split, and the merge
  tie rule (FR-11) can be checked byte for byte, although the two sorts run concurrently.
- **Robustness.** Deadlock freedom is required and its conditions stated (FR-10); a worker
  that fails or breaks the protocol is reported instead of hanging or producing a wrong
  result (FR-13). The data set is limited to 100000 values (FR-02), because selection sort is
  quadratic.
- No prompts: the textbook programs read nothing from the keyboard.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Of the
conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Both tools read their input as tokens (FR-02, FR-06). |
| CONV-33 | Every value uses the *integer* grammar; the request size is further restricted to 0 … 100000 (FR-06). |
| CONV-34 | All data errors use its format, its standard messages, and one further message, `too many values` (FR-02, FR-07, FR-14). |
| CONV-35 | Not applicable: no real number is written. |
| CONV-36 | Not applicable: the tools have no prompts. |
| CONV-37 | The input of both tools is *text data* (FR-02, FR-06). |
| CONV-38 | `dp-sort-host --random` generates the data set; `--seed` with the default 1 (FR-03). |

Standard input is read as permitted by CONV-26. Neither tool copies input bytes to its output
(values are written as decimals), so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-sort-host [-t | --trace] [FILE]
dp-sort-host [-t | --trace] (-r COUNT | --random=COUNT) [--seed=SEED]
dp-sort-child [FILE]
dp-sort-host --help | --version
dp-sort-child --help | --version
```

### 3.2 Options

| Tool | Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `dp-sort-host` | `-t` | `--trace` | none | off | Write the trace of FR-12 to standard error |
| `dp-sort-host` | `-r` | `--random` | COUNT | — | Sort COUNT generated values instead of reading input (FR-03) |
| `dp-sort-host` | — | `--seed` | SEED | `1` | Initial state of the generator (FR-03, CONV-38) |
| both | — | `--help` | none | — | Print the help text and exit 0 |
| both | — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. If
`--random` or `--seed` is given more than once, the last value wins (CONV-11); only that value
is validated. `--seed` is accepted, validated, and has no further effect without `--random`.

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19). With `--random`, `dp-sort-host` accepts no operand.

### 3.4 Standard input
Read when no operand is given or the operand is `-` (and, for `dp-sort-host`, `--random` is
not given). Read as raw bytes; no newline translation of any kind is performed on any
platform.

### 3.5 Standard output
`dp-sort-host`: the merged values (FR-12). `dp-sort-child`: the reply (FR-07). Nothing else.
On a usage error, or when `--help` / `--version` is handled, the output is as specified by
FR-16 … FR-19 instead.

### 3.6 Standard error
The trace (FR-12, `dp-sort-host --trace` only) and diagnostics (section 6). Without
`--trace`, nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The data set was sorted and written (`dp-sort-host`), or the request was served (`dp-sort-child`), including the empty cases; or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-15), it contained invalid data (FR-07, FR-14), the worker failed (FR-13), or standard output could not be written |
| 2 | Usage error (FR-18) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `data.txt`, `odd.txt`, `request.txt`, `bad.txt`,
and `short.txt` are the public fixture files in `tests/fixtures/`: `data.txt` is the ten values
42, 17, −5, 8, 23, 17, 0, −12, 99, 4, one per line; `odd.txt` is
`31 8 -4\r\n15 8\t2\r\n\r\n8 -40 77\r\n3 15\r\n` (eleven values); `request.txt` is
`6\n9\n-2\n9\n0\n31\n4\n`; `bad.txt` is `5 3\n8\n4.5\n2\n`; `short.txt` is `4\n10\n20\n`.

### 4.1 dp-sort-host: the data set

**FR-01: Input source.**
Without `--random`, if no operand is given, or the operand is `-`, `dp-sort-host` MUST read
standard input; otherwise it MUST open the file named by the operand and read it as raw bytes.
With `--random`, it reads no input (FR-03). More than one operand, or any operand together
with `--random`, is a usage error (FR-18).
*AC:* `dp-sort-host data.txt` and `dp-sort-host < data.txt` write the same output. *(UR-01)*

**FR-02: Values.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32); each token
is one value, in order. Each token MUST be a valid *integer* (CONV-33); signs and leading zeros
are allowed, and values are written as their decimals (`+5`, `007`, `-0` → `5`, `7`, `0`).
Line structure has no meaning, so CRLF input reads exactly like LF input. At most 100000
values are allowed. The tokens are checked in order, and the first problem is reported
(FR-14): a token that is not a valid *integer*, or a 100001st token (whatever it contains).
The whole input MUST be read and validated before the worker is started, so a data error
produces no output and no trace. An empty input, or one with only whitespace and a trailing
Ctrl-Z run, is a data set of *N* = 0 values.
*AC:* `dp-sort-host -t < odd.txt` sorts the eleven values 31, 8, −4, 15, 8, 2, 8, −40, 77, 3,
15. *(UR-01, UR-07, UR-09)*

**FR-03: Generated values.**
With `-r COUNT`, `--random=COUNT`, the data set is COUNT values generated by the CONV-38
generator, seeded once with SEED (`--seed`, default 1): *x*ᵢ is the (*i* + 1)-th draw *r*, an
integer 0 … 32767, for *i* = 0 … COUNT − 1. No other draw is made. COUNT consists only of ASCII
digits (leading zeros allowed) and lies in 0 … 100000; SEED consists only of ASCII digits and
lies in 0 … 4294967295. Any other COUNT or SEED is an invalid option value (FR-18).
*AC:* `dp-sort-host --random=10` sorts the values 16838, 5758, 10113, 17515, 31051, 5627,
23010, 7419, 16212, 4086 and writes `4086\n5627\n5758\n7419\n10113\n16212\n16838\n17515\n23010\n31051\n`.
*(UR-05)*

**FR-04: Partition.**
The host part is *x*₀ … *x*_{*h*−1} with *h* = ⌊*N* / 2⌋, and the child part is
*x*_{*h*} … *x*_{*N*−1}, *c* = *N* − *h* values, in data-set order. The child part is
therefore never smaller than the host part: for *N* = 0 both are empty, for *N* = 1 the host
part is empty, and for odd *N* the child part has one value more.
*AC:* for `data.txt` the request is 5, then 17, 0, −12, 99, 4 (test 02); for `odd.txt` the
request has 6 values (test 03). *(UR-02)*

### 4.2 The worker protocol and dp-sort-child

**FR-05: Worker protocol.**
A request is *c* + 1 messages: first the decimal of *c*, then the decimals of the child part
in order. A reply is *c* messages: the decimals of the child part sorted in non-decreasing
order. Each message is the decimal followed by exactly one LF, with no other bytes. The sender
of a request or reply (the host, or the worker) MUST write exactly these bytes; the receiver
of a request (the worker, and `dp-sort-child`) MUST accept the more general token syntax of
FR-06. There is no other message: no greeting, acknowledgement, end marker, or size in the
reply (the host knows *c*).
*AC:* `dp-sort-child < request.txt` writes `-2\n0\n4\n9\n9\n31\n`. *(UR-03)*

**FR-06: dp-sort-child: request.**
`dp-sort-child` reads one request from the FILE operand, or from standard input when no
operand is given or the operand is `-`. The input is *text data* (CONV-37) and is read as
tokens (CONV-32). The first token is the size *c*: a valid *integer* (CONV-33) in
0 … 100000. The next *c* tokens are the values, each a valid *integer*. The tool MUST stop
reading as soon as the *c*-th value is complete — the whitespace byte that ends it has been
read, or the input has ended — and MUST NOT wait for the end of the input or read further
(apart from ordinary buffering of bytes that are already available); whatever follows the
request is ignored. For *c* = 0, nothing after the size is read.
*AC:* a file holding `2\n8\n3\nnot a number\n` gives `3\n8\n`, exit 0; `0 junk` gives no
output, exit 0; `2\r\n5\r\n-5\r\n` followed by two `0x1A` bytes gives `-5\n5\n`. *(UR-03, UR-09)*

**FR-07: dp-sort-child: reply and data errors.**
When the request is complete, `dp-sort-child` MUST sort the values with the selection sort of
FR-08, write the reply (FR-05) to standard output, flush it, and exit with status 0. Data
errors are reported with CONV-34 messages, and nothing is written to standard output:

- the size token is not a valid *integer*: `invalid integer '<token>'`; it is a valid
  *integer* outside 0 … 100000: `value out of range '<token>'`;
- a value token is not a valid *integer*: `invalid integer '<token>'`;
- the input ends before the size or before the *c*-th value: `unexpected end of input`, with
  the end-of-input line number.

*AC:* `dp-sort-child short.txt` → stdout empty, stderr
`dp-sort-child: short.txt:4: unexpected end of input\n`, exit 1; a size of `-1` on line 2 →
`dp-sort-child: <source>:2: value out of range '-1'`; `100001` →
`value out of range '100001'`; a value `x2` on line 3 → `invalid integer 'x2'`; a value
`1` followed by `0x1A` and LF → `invalid integer` (that Ctrl-Z byte is not at the end of the
input); empty standard input → `dp-sort-child: -:1: unexpected end of input`. *(UR-03, UR-07)*

**FR-08: Selection sort.**
Both parts MUST be sorted with selection sort exactly as SRS-35 FR-04 specifies: for each
position *i* from the first to the second-to-last, find the first position *m* of the smallest
element at or after *i*, and exchange the elements at *i* and *m* if *m* ≠ *i*. The host part
and the child part are sorted independently (neither sort sees the other part). The result is
the part in non-decreasing order; because equal integers are indistinguishable, the order of
operations is checked by design review and unit tests, not by the black-box tests.
*AC:* every output in the test suites is the sorted data set; unit tests per NFR-06.
*(UR-02, UR-06)*

### 4.3 dp-sort-host: concurrency, merge, and output

**FR-09: The worker.**
`dp-sort-host` MUST sort the child part in a worker that runs **concurrently** with the host
and communicates with it only through the two channels, using the protocol of FR-05. The
worker MAY be:

1. a thread (or task, goroutine, or equivalent) of the `dp-sort-host` process, connected by
   operating-system pipes or by an in-memory byte or line channel;
2. a child process running the same executable in a worker mode that is not part of the
   command-line interface, connected by pipes to its standard input and output; or
3. a child process running `dp-sort-child`, located in the same directory as the running
   `dp-sort-host` executable (never through `PATH` or the working directory), started without
   arguments and connected by pipes to its standard input and output.

Whatever the choice, the worker MUST NOT share the data set, the host part, or any result
with the host except through the channels, and its request handling and sorting MUST be the
same code that `dp-sort-child` uses (NFR-05). A worker process inherits standard error; it is
reaped before `dp-sort-host` exits. The choice is not observable: standard output, standard
error, and the exit status are the same for all three.
*AC:* all tests pass whichever worker is chosen; design review confirms concurrency and the
absence of shared state. *(UR-02, UR-03)*

**FR-10: Ordering and deadlock freedom.**
`dp-sort-host` and its worker MUST follow this order, which can never deadlock, whatever the
capacity of the channels (a pipe may hold as little as 4096 bytes):

1. The host validates the whole data set (FR-02) before it starts the worker.
2. The host writes the complete request and flushes it, then closes (or marks the end of) the
   request channel. Meanwhile the worker reads the request; it MUST NOT write any part of the
   reply before it has read the whole request, and the host MUST NOT wait for any reply
   message before it has sent the whole request.
3. Only after sending the whole request does the host sort the host part, so that the two
   sorts overlap in time.
4. The worker MUST NOT wait for the end of the request channel: it starts sorting as soon as
   the *c*-th value is complete (FR-06). It then writes the whole reply, flushes it, and ends.
5. The host merges (FR-11), receiving reply messages as the merge needs them; it receives all
   *c* of them, then waits for the worker to end (joins the thread or reaps the process).

The worker is started, and the request (at least the message `0`) sent, even when *c* = 0.
Neither side may hold a lock, buffer, or channel end that the other is waiting for; in
particular, a worker process MUST NOT inherit the host's end of either pipe, or it would never
see the end of the request channel and the host would never see the end of the reply channel.
*AC:* every test terminates well within the time limit; `dp-sort-host --trace` with empty
standard input writes only the trace line `host -> child: 0`; review of the design against
items 1 … 5. *(UR-06)*

**FR-11: Merge.**
The host merges its sorted part *H*[0 … *h*−1] with the reply as follows, emitting values in
order:

1. If *c* > 0, receive the first reply value; call the most recently received value that has
   not yet been emitted the *pending* value.
2. While some host value remains (index *i* < *h*) and a pending value exists: if
   *H*[*i*] ≤ *pending*, emit *H*[*i*] (from the host) and advance *i*; otherwise emit
   *pending* (from the child) and then, if fewer than *c* values have been received, receive
   the next one as the new pending value.
3. Emit the remaining host values in order, then the pending value and every remaining reply
   value, each received just before it is emitted.

**Tie rule:** when a host value equals the pending value, the host value is emitted first.
Exactly one reply value is received at the start of the merge and one after each emitted
child value, as long as reply values remain; the host never receives a reply value earlier.
The merge makes at most *N* − 1 comparisons and emits all *N* values, which are then in
non-decreasing order.
*AC:* for the data set 3, 5, 5, 5, 1, 5 (host part 3, 5, 5; reply 1, 5, 5) the merge emits 1
from the child, then 3, 5, 5 from the host, then 5 and 5 from the child (hidden test 02).
*(UR-02, UR-04, UR-06)*

**FR-12: Output and trace.**
`dp-sort-host` MUST write the emitted values to standard output in emission order, each as its
decimal followed by LF, with nothing else: no header, no blank lines, no summary. (They MAY be
written as they are emitted or after the merge.) With `-t`, `--trace`, it MUST also write to
standard error one line per event, in the order the events occur under FR-10 and FR-11:

| Event | Trace line |
| :-- | :-- |
| The host sends request message *m* | `host -> child: <m>` |
| The host receives reply value *v* | `child -> host: <v>` |
| The merge emits value *v* from the host part | `merge: <v> from host` |
| The merge emits value *v* from the reply | `merge: <v> from child` |

`<m>` and `<v>` are decimals; each line ends with one LF and contains exactly the spaces shown.
The trace therefore begins with the *c* + 1 `host -> child` lines, followed by the merge, in
which each `child -> host` line comes immediately before the event that FR-11 says follows
the receive. The trace is a function of the data set alone; how the bytes travel or are
buffered never changes it. The order in which standard output and standard error are written
relative to each other is not specified. Without `--trace`, nothing is written to standard
error on success.
*AC:* `dp-sort-host --trace data.txt` → stdout `-12\n-5\n0\n4\n8\n17\n17\n23\n42\n99\n`;
stderr begins `host -> child: 5\nhost -> child: 17\nhost -> child: 0\n` and continues as in
`tests/public/expected-outputs/02.stderr`; for a data set of one value 7, the trace is
`host -> child: 1\nhost -> child: 7\nchild -> host: 7\nmerge: 7 from child\n`.
*(UR-01, UR-04)*

**FR-13: Worker failure.**
If the worker cannot be started, or the reply violates FR-05 — a message that is not a
decimal followed by LF, fewer than *c* messages before the reply channel ends, a value smaller
than the value received before it — or a worker process ends with a non-zero status,
`dp-sort-host` MUST write `dp-sort-host: worker failed` to standard error and exit with
status 1. Trace lines and values already written are kept; the merged output is then
incomplete. Bytes after the *c*-th reply message are ignored. `dp-sort-host` MUST NOT hang
when the worker ends early: the end of the reply channel is detected as a failure. (A correct
implementation never fails this way; the black-box tests cannot provoke it.)
*AC:* review and unit tests of the reply reader with a truncated, an unsorted, and a malformed
reply. *(UR-06)*

### 4.4 Errors and command line

**FR-14: dp-sort-host: data errors.**
If a token is not a valid *integer* (CONV-33), including an integer outside −2⁶³ … 2⁶³−1,
`dp-sort-host` MUST write `dp-sort-host: <source>:<line>: invalid integer '<token>'`. If the
input has more than 100000 tokens and the first 100000 are valid, it MUST write
`dp-sort-host: <source>:<line>: too many values`, where `<line>` is the line number of the
100001st token. `<line>` is the token's line number (CONV-32) and `<token>` its exact bytes
(CONV-34). Because the data set is validated before the worker starts (FR-02), nothing is
written to standard output and no trace is written; the exit status is 1.
*AC:* `dp-sort-host bad.txt` → stdout empty, stderr
`dp-sort-host: bad.txt:3: invalid integer '4.5'\n`, exit 1; a token
`9223372036854775808` on line 3 → `invalid integer '9223372036854775808'`; a file of 100001
lines `1` → `dp-sort-host: <source>:100001: too many values`. *(UR-07)*

**FR-15: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `<tool>: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1, having written nothing to standard output. When standard input fails,
`<source>` is `-`.
*AC:* `dp-sort-host missing.txt` → stderr
`dp-sort-host: missing.txt: No such file or directory\n`, stdout empty, exit 1;
`dp-sort-child subdir` where `subdir` is a directory → `dp-sort-child: subdir: Is a directory`.
*(UR-08)*

**FR-16: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read and no
worker is started.
*AC:* `dp-sort-host --help` and `dp-sort-child --help` match the user manual exactly;
`dp-sort-host extra --help` also prints the help. *(UR-10)*

**FR-17: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02), where
`<tool>` is `dp-sort-host` or `dp-sort-child`.
*AC:* exact match for both tools. *(UR-10)*

**FR-18: Usage errors.**
Unknown options, a missing option argument, and arguments supplied to options that take none
(`--trace=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08).
`dp-sort-child` has no options other than `--help` and `--version`. After the whole argument
list has been scanned (CONV-12), the remaining checks are made in this order, and the first
failure is reported:

1. `dp-sort-host`: the last COUNT (FR-03), as
   `dp-sort-host: invalid argument '<COUNT>' for '<option>'` (`-r` or `--random`, as last
   written);
2. `dp-sort-host`: the last SEED (FR-03), as `dp-sort-host: invalid argument '<SEED>' for '--seed'`;
3. operands: with `--random`, the first operand; otherwise the second operand, as
   `<tool>: extra operand '<operand>'`.

*AC:* `dp-sort-host -r 5 data.txt` → `dp-sort-host: extra operand 'data.txt'`;
`dp-sort-host --random=100001` → `dp-sort-host: invalid argument '100001' for '--random'`;
`dp-sort-host --random --help` → `dp-sort-host: invalid argument '--help' for '--random'` (the
option consumes `--help` as its value); `dp-sort-host -x --help` →
`dp-sort-host: invalid option -- 'x'`; `dp-sort-child request.txt extra` →
`dp-sort-child: extra operand 'extra'`; each followed by the CONV-14 line, exit 2. *(UR-11,
UR-13)*

**FR-19: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, start a
worker, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output, traces, and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line the tools generate MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: concurrency and channels | The channels MUST carry exactly the bytes of FR-05 on every platform: pipes and standard streams MUST be in binary mode (no LF→CRLF translation on Windows, no `0x1A` end-of-file interpretation). The design MUST be deadlock-free under FR-10 for any pipe capacity (Linux typically 64 KiB, macOS 16–64 KiB, Windows anonymous pipes 4 KiB or the size requested at creation). A thread worker MUST use the platform's or language's standard threads (POSIX threads, Win32 threads, or a portable runtime abstraction) and be joined; a process worker MUST be created as SRS-08 NFR-02 describes (`posix_spawn` or `fork`+`exec` on POSIX, `CreateProcessW` with only the standard handles inherited on Windows), and MUST be reaped. A process-based design MUST work from the directory that `make all` builds into and from the installed location on all three platforms — including Windows, where a script launcher cannot be executed directly — or else the thread design MUST be used. Inputs MUST be read in binary mode; only FR-02 and FR-06 decide what CR and `0x1A` mean. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Sorting 10 000 values (`--random=10000`) MUST take under 0.5 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware, and 100 000 values under 10 s native, with peak memory under 32 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). The merge MUST be linear in *N*; memory MUST be O(*N*). With two or more processor cores, the two sorts MUST overlap in time, so the elapsed time for a large *N* is close to that of sorting *N* / 2 values once, not twice. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tools MUST NOT crash, panic, print a stack trace, or hang for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends a tool quietly (CONV-25), and also ends the worker. | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, input tokenizing and validation, partitioning, the request writer, the request reader, the selection sort, the reply reader, the merge, and trace formatting MUST be separate units. The request reader, the selection sort, and the reply writer MUST be one module (the worker) shared by `dp-sort-child` and the worker of `dp-sort-host`, so the two cannot drift apart; the host part is sorted by the same selection-sort unit. The merge MUST take the reply as a stream (a function or iterator that receives one value at a time), not as a complete array. Command-line handling common to both tools MUST be shared rather than duplicated (Principles 3, 13, 18). | Design review |
| NFR-06 | Testability | The merge MUST be unit-testable with an in-memory reply stream and an event recorder, and tested for *h* = 0, *c* = 0, all-equal values, ties across the parts, and interleaved parts, checking both the output and the exact event order of FR-12. The selection sort MUST be unit-tested as SRS-35 NFR-06 describes. The request reader MUST be unit-tested with the input split into reads at every byte position and with a request followed by unrelated data. The reply reader MUST be unit-tested with the failures of FR-13. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tools MUST read only the FILE operand or standard input, and MUST NOT create or modify any file or read environment variables. `dp-sort-host` MAY start one worker process as FR-09 allows and MUST NOT run any other program; `dp-sort-child` MUST NOT run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try '<tool> --help' for more information.`,
where `<tool>` is the tool that reported it.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `<tool>: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `<tool>: unrecognized option 'T'` |
| `dp-sort-host`: `-r` as the last argument | `dp-sort-host: option requires an argument -- 'r'` |
| `dp-sort-host`: `--random` or `--seed` as the last argument | `dp-sort-host: option '--random' requires an argument` (or `'--seed'`) |
| `--trace=…` (`dp-sort-host`), `--help=…`, `--version=…` | `<tool>: option '--trace' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| `dp-sort-host`: invalid COUNT `V` given with option `O` | `dp-sort-host: invalid argument 'V' for 'O'` |
| `dp-sort-host`: invalid SEED `V` | `dp-sort-host: invalid argument 'V' for '--seed'` |
| A second operand `X`, or (`dp-sort-host --random`) any operand `X` | `<tool>: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `<tool>: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `<tool>: F: Permission denied` |
| FILE `F` is a directory | `<tool>: F: Is a directory` |
| A component of FILE `F` is not a directory | `<tool>: F: Not a directory` |
| Any other open or read failure of FILE `F` | `<tool>: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *integer* | `<tool>: S:L: invalid integer 'K'` |
| `dp-sort-child`: the size token `K` on line `L` is a valid *integer* outside 0 … 100000 | `dp-sort-child: S:L: value out of range 'K'` |
| `dp-sort-child`: the input ends before the size or the last value; `L` is the end-of-input line number | `dp-sort-child: S:L: unexpected end of input` |
| `dp-sort-host`: the 100001st token is on line `L` | `dp-sort-host: S:L: too many values` |
| `dp-sort-host`: the worker could not be started or broke the protocol (FR-13) | `dp-sort-host: worker failed` |
| Standard output cannot be written (other than a broken pipe) | `<tool>: write error` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases; case 09 has two steps) | FR-01 … FR-07, FR-10 … FR-12, FR-14 … FR-16 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 01 and 03 … 10 have several steps) | FR-02 … FR-07, FR-10 … FR-12, FR-14 … FR-19 |
| Unit test (written by the implementer) | FR-06, FR-08, FR-11, FR-13, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review / demonstration | FR-08, FR-09, FR-10, FR-13, NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-sort-host data.txt` | FR-01, FR-02, FR-04, FR-11, FR-12 |
| 02 | `dp-sort-host --trace data.txt` | FR-04, FR-05, FR-10 … FR-12 (trace) |
| 03 | `dp-sort-host -t < odd.txt` | FR-02 (CRLF, TAB, blank line), FR-04 (odd *N*), FR-11 (ties) |
| 04 | `dp-sort-child < request.txt` | FR-05 … FR-07 |
| 05 | `dp-sort-host --random=10` | FR-03 |
| 06 | `dp-sort-host --trace` (empty standard input) | FR-02 (*N* = 0), FR-10 |
| 07 | `dp-sort-host bad.txt` | FR-14 (no output, no trace) |
| 08 | `dp-sort-child short.txt` | FR-07 (`unexpected end of input`) |
| 09 | `dp-sort-host --help`; `dp-sort-child --help` | FR-16 |
| 10 | `dp-sort-host missing.txt` | FR-15 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-12 |
| UR-02 | FR-04, FR-08, FR-09, FR-11 |
| UR-03 | FR-05, FR-06, FR-07, FR-09 |
| UR-04 | FR-11, FR-12 |
| UR-05 | FR-03, CONV-38 |
| UR-06 | FR-08, FR-10, FR-11, FR-13, NFR-02 |
| UR-07 | FR-02, FR-07, FR-14, CONV-33, CONV-34 |
| UR-08 | FR-15, CONV-16 |
| UR-09 | FR-02, FR-06, NFR-02, CONV-37 |
| UR-10 | FR-16, FR-17 |
| UR-11 | FR-18, FR-19 |
| UR-12 | NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-18, CLI-CONV |
| UR-14 | NFR-03, NFR-05, NFR-07 |

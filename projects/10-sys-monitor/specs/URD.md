# User Requirements Document (URD) — dp-sysmon

| Field | Value |
| :-- | :-- |
| Document ID | URD-10 |
| Project | `10-sys-monitor` — System Resource Telemetry Daemonic CLI |
| Product | `dp-sysmon` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-10), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-sysmon` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-10), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-sysmon` answers the questions people usually ask `top` and `ps`: how busy is this machine,
how much memory and disk is left, and which processes are responsible? It answers them the same
way on Linux, macOS, and Windows, even though each system exposes its performance counters
through completely different interfaces. It can take a single reading, run as a long-lived
monitor that emits one record per interval, and write records as JSON Lines that other tools —
and `dp-sysmon` itself — can consume later. Because recorded telemetry can be replayed exactly,
everything the tool does with the data can be tested deterministically.

### 1.3 Scope
In scope: CPU utilization, memory, disk usage, and the process list; one-shot and repeated
sampling; a readable fixed-width table and a machine-readable JSON Lines stream; filtering,
sorting, and limiting the process list; recording samples to a file; replaying recorded
samples; help, version, and clear errors.
Out of scope: interactive full-screen interfaces (cursor movement, colors, key commands),
killing or renicing processes, per-core and per-thread detail, network and GPU metrics, remote
hosts, and alerting.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Operator | Checks a machine's health by hand in a terminal on Linux, macOS, or Windows | A quick, readable overview |
| SH-2 | Automation author | Feeds telemetry into scripts, log pipelines, or dashboards | A stable machine-readable format, predictable exit statuses, streaming output |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification and a clear split between portable and OS-specific code |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior despite live data being non-deterministic |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As an operator, I want to run the tool with no arguments and see the current CPU utilization, memory, disk usage, and process list of my machine. | M | SH-1 |
| UR-02 | As an automation author, I want to replay previously recorded telemetry instead of reading the live system, so I can reprocess, reformat, or test with known data. | M | SH-2, SH-4 |
| UR-03 | As an operator, I want to choose how many samples to take and how far apart they are, so I can watch a machine for a while. | M | SH-1 |
| UR-04 | As an automation author, I want the tool to run indefinitely as a monitor, emitting each sample as soon as it is taken and optionally appending it to a log file. | S | SH-2 |
| UR-05 | As an operator, I want to sort the process list by CPU, memory, process ID, or name, show only the top N, and filter by part of a process name. | M | SH-1 |
| UR-06 | As an operator, I want sizes in human units (KiB, MiB, GiB, …) and aligned columns, so the table is easy to read. | M | SH-1 |
| UR-07 | As an automation author, I want a JSON Lines output with a fixed structure, one record per sample, so I can parse it with any JSON library. | M | SH-2 |
| UR-08 | As a grader, I want identical output bytes on Linux, macOS, and Windows for the same recorded input, so a single set of expected outputs verifies every platform. | M | SH-4 |
| UR-09 | As an automation author, I want invalid usage rejected with a clear message and a distinct exit status, never silently ignored. | M | SH-2 |
| UR-10 | As an automation author, I want a damaged or malformed recording to be reported precisely, with the line number and the offending field, rather than producing misleading output. | M | SH-2 |
| UR-11 | As an automation author, I want recordings made by the tool to be replayable by the tool without loss of the reported values. | S | SH-2 |
| UR-12 | As any user, I want built-in help and version information, and behavior that follows the curriculum's common CLI conventions. | M | SH-1, SH-3 |
| UR-13 | As an operator, I want strange process names (very long, control characters, non-ASCII) to be displayed safely without breaking the table or my terminal. | S | SH-1 |
| UR-14 | As an operator, I want the same metrics to mean the same thing on every operating system, and the tool to keep working, without errors, when I lack permission to inspect some processes. | M | SH-1, SH-3 |
| UR-15 | As an operator, I want the tool to be light: fast to start, cheap to run every second, and constant in memory when it runs for days. | S | SH-1, SH-2 |
| UR-16 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-4 |

## 4. Usage scenarios

### 4.1 Quick health check
An operator types `dp-sysmon`. About a second later the tool prints the host name, time, CPU
utilization, memory use, a table of mounted disks, and the process list sorted by CPU usage,
then exits with status 0. (UR-01, UR-06)

### 4.2 Who is eating memory?
The operator runs `dp-sysmon --sort=mem --top=5` to see the five processes with the largest
resident memory, then `dp-sysmon --filter=chrome` to see only browser processes. (UR-05)

### 4.3 Monitoring to a log
An automation author runs `dp-sysmon --count=0 --interval=10 --format=json --output=host.jsonl
> /dev/null` as a background job. Every ten seconds one JSON line is appended to `host.jsonl`;
the job runs until stopped. (UR-03, UR-04, UR-07)

### 4.4 Reprocessing a recording
Later, the author runs `dp-sysmon --snapshot=host.jsonl --sort=name --top=20` to view the
recording as tables, and `dp-sysmon --snapshot=- --format=json --filter=java < host.jsonl` to
extract Java processes for a dashboard. (UR-02, UR-05, UR-11)

### 4.5 A damaged recording
A recording was truncated by a full disk. Replaying it prints every complete sample and then
`dp-sysmon: host.jsonl:812: invalid JSON`, exiting with status 1, so the script knows the data is
incomplete and where. (UR-10)

### 4.6 A mistake
A user types `dp-sysmon --sort=memory`. The tool prints a one-line explanation and a pointer to
`--help`, writes nothing to standard output, and exits with status 2. (UR-09)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, configuration files, or third-party system services. |
| UC-4 | Must behave identically whatever the user's locale, time zone, or terminal settings. |
| UC-5 | Live telemetry is inherently non-deterministic; automated byte-exact acceptance tests must therefore use recorded telemetry. |

## 6. User acceptance criteria

The users will accept `dp-sysmon` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests (replay mode) pass in CI on all three platforms.
3. The live-mode integration checks listed in SRS-10 section 7 pass on all three platforms.
4. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Sample | One record of telemetry taken at one moment |
| Snapshot / recording | A file of samples in JSON Lines format |
| JSON Lines | A text format with one JSON value per line |
| RSS | Resident set size: the physical memory a process currently occupies |
| CPU % (process) | Share of one CPU's time a process used during the last interval; can exceed 100 on multi-core machines |
| Daemonic | Running unattended for a long time, producing output periodically |
| Exit status | The integer a process returns to its caller; 0 means success |

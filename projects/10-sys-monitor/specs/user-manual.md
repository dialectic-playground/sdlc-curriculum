# dp-sysmon — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-sysmon` 1.0.0 |
| Project | `10-sys-monitor` — System Resource Telemetry Daemonic CLI |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-10), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-sysmon** — report CPU, memory, disk, and process telemetry as a table or JSON Lines

## SYNOPSIS

```text
dp-sysmon [-s FILE] [-f table|json] [-k cpu|mem|pid|name] [-n N] [-m TEXT]
          [-i SECS] [-c N] [-o FILE]
dp-sysmon --help
dp-sysmon --version
```

## DESCRIPTION

`dp-sysmon` shows how busy a machine is and which processes are responsible, like `top` and
`ps`. Each **sample** contains the time, the host name, overall CPU utilization and the number
of logical CPUs, total and available memory, the size and usage of each disk, and the process
list with each process's CPU share and resident memory (RSS).

By default `dp-sysmon` samples the local system **live**: it takes a baseline reading, waits one
interval (one second unless you say otherwise), takes a second reading, and reports the CPU
activity between the two. With `--count` it keeps going, one sample per interval; with
`--count=0` it runs until you stop it, which makes it suitable as a long-running monitor.

With `--snapshot=FILE` it **replays** samples recorded earlier instead of reading the system. A
snapshot file is in JSON Lines format: one sample per line, exactly as `dp-sysmon --format=json`
or `--output` writes them. Everything `dp-sysmon` does with a sample — filtering, sorting,
formatting — works the same way in both modes, and replayed output is identical on every
operating system.

Each sample is written either as a **table** (the default) or as one line of **JSON**. The table
starts with a short summary, then lists the disks and the processes:

```text
Host:      alpha
Time:      2026-03-14T09:26:53Z
CPU:       37.5% busy; logical CPUs: 8
Memory:    10.0 GiB used of 16.0 GiB (62.5%); 6.0 GiB available
Processes: 8 total; 8 shown

MOUNT                       USED       TOTAL    USE%
/                       50.0 GiB   100.0 GiB    50.0
/boot                  256.0 MiB     1.0 GiB    25.0
/home                  200.0 GiB   500.0 GiB    40.0

    PID    CPU%         RSS  NAME
   1203    42.3     1.5 GiB  firefox
   1350    12.5   256.0 MiB  Xorg
   2201    12.5   100.0 MiB  python3
    412     0.1     8.0 MiB  sshd
   2048     0.1     5.0 MiB  zsh
      1     0.0    12.0 MiB  systemd
    977     0.0     5.0 MiB  bash
   3100     0.0     4.0 MiB  SSH-agent
```

Reading the table:

- **CPU** in the summary is the share of all CPUs that was busy during the interval (0–100%).
  **CPU%** of a process is its share of *one* CPU, so a multi-threaded process on a multi-core
  machine can show more than 100.
- **Memory used** is total minus available memory. Available memory is what can be given to
  programs without swapping, so it includes reclaimable caches.
- Sizes use binary units: 1 KiB = 1024 bytes, 1 MiB = 1024 KiB, and so on up to PiB, with one
  decimal place. Values below 1 KiB are shown in bytes (`512 B`).
- A `-` means the value is unknown (for example, the CPU share of a process that started during
  the interval, or the memory of a process you are not allowed to inspect).
- Disks are listed in order of their mount point. Long mount points are shortened to 20
  characters and long process names to 24, ending in `...`. Control characters in names are
  shown as `?`, so a hostile process name cannot disturb your terminal.

When several samples are shown as tables, an empty line separates them. In JSON format each
sample is one line, for example (shortened here):

```text
{"timestamp":"2026-03-14T09:26:53Z","hostname":"alpha","cpu":{"count":8,"percent":37.5},"memory":{"total_bytes":17179869184,"available_bytes":6442450944},"disks":[{"mount":"/","total_bytes":107374182400,"used_bytes":53687091200}],"processes":[{"pid":1203,"name":"firefox","cpu_percent":42.3,"rss_bytes":1610612736}]}
```

The members always appear in this order. Byte counts are whole numbers; percentages always have
one decimal place; unknown values are `null`.

## OPTIONS

**`-s FILE`, `--snapshot=FILE`**
: Replay samples from *FILE* instead of sampling the system. `-` reads standard input. Without
  this option, `dp-sysmon` samples the live system.

**`-f FORMAT`, `--format=FORMAT`**
: `table` (the default) or `json`.

**`-k KEY`, `--sort=KEY`**
: Order the process list by `cpu` (highest first; the default), `mem` (largest RSS first),
  `pid` (lowest first), or `name` (in byte order, so upper case sorts before lower case).
  Unknown values sort last. Equal values are ordered by process ID. CPU shares are compared as
  displayed, with one decimal place.

**`-n N`, `--top=N`**
: Show at most *N* processes (after filtering and sorting). *N* is 0 to 1000000; `0` shows the
  summary and disks only.

**`-m TEXT`, `--filter=TEXT`**
: Show only processes whose name contains *TEXT*. ASCII letters match regardless of case
  (`--filter=SH` matches `bash` and `SSH-agent`); other characters must match exactly.

**`-i SECS`, `--interval=SECS`**
: Seconds between live samples, from `0.1` to `86400`, written with digits and an optional
  decimal point (`0.5`, `2`, `10.25`). The default is `1`. Ignored when replaying.

**`-c N`, `--count=N`**
: Stop after *N* samples, 0 to 1000000. `0` means no limit: live sampling continues until you
  interrupt it, and replay continues to the end of the file. The default is `1` for live
  sampling and `0` (the whole file) for replay.

**`-o FILE`, `--output=FILE`**
: Also append every sample, as one JSON line, to *FILE* (created if necessary). Standard output
  still receives the `--format` output; redirect it to the null device if you only want the
  file. The recorded processes are the same ones shown (after `--filter`, `--sort`, `--top`).
  *FILE* must not be the file being replayed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-sysmon` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-kmem`, `-k mem`, `--sort=mem`, and
  `--sort mem` are equivalent.
- Long options must be spelled out in full; `--sor` is not accepted.
- If an option is given more than once, the last one wins.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was malformed. Option values are checked
  afterwards, so `dp-sysmon --sort=bad --help` still shows the help.
- `dp-sysmon` accepts no operands; a word that is not an option is an error.

## SNAPSHOT FILES

A snapshot file holds one sample per line as a JSON object. Blank lines are skipped, and lines
may end in LF or CRLF. Each sample needs these members (others are ignored):

| Member | Type | May be `null` |
| :-- | :-- | :-- |
| `timestamp`, `hostname` | string | no |
| `cpu.count` (≥ 1), `cpu.percent` (0–100) | number | yes |
| `memory.total_bytes`, `memory.available_bytes` | whole number | yes |
| `disks`: list of `{mount, total_bytes, used_bytes}` | string, whole numbers | no |
| `processes`: list of `{pid, name, cpu_percent, rss_bytes}` | whole number, string, number, whole number | `cpu_percent` and `rss_bytes` only |

Available memory may not exceed total memory, a disk's used bytes may not exceed its total,
and process IDs must be unique within a sample. Samples are processed one line at a time: if a
line is invalid, the samples before it have already been shown, and `dp-sysmon` stops with a
message that names the line and the problem. The SRS (section 3.9) gives the complete rules.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: all requested samples, the help, or the version was printed |
| 1 | A file could not be opened, read, or written; a snapshot line was invalid; the snapshot had no samples |
| 2 | Usage error: invalid option, invalid value, or an unexpected operand |

If you interrupt a running monitor with Ctrl-C, it stops without a message; shells report
status 130.

## DIAGNOSTICS

Errors are written to standard error. Usage errors are followed by a second line,
`Try 'dp-sysmon --help' for more information.`, and nothing is written to standard output:

```text
$ dp-sysmon --sort=memory
dp-sysmon: invalid argument 'memory' for '--sort'
Try 'dp-sysmon --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option | Check the option letter |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'k'` | A short option without its value | Supply a value |
| `option '--sort' requires an argument` | A long option without its value | Supply a value |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…` | Remove the `=…` |
| `invalid argument 'memory' for '--sort'` | A value outside the allowed set or range | See OPTIONS |
| `extra operand 'foo'` | A word that is not an option | Remove it |
| `FILE: No such file or directory` | The snapshot does not exist | Check the path |
| `FILE: Is a directory` | A directory was given as snapshot or output | Name a file |
| `FILE: Permission denied` | The file cannot be read or written | Check permissions |
| `FILE: input file is output file` | `--output` names the snapshot being replayed | Record to a different file |
| `FILE: no samples` | The snapshot is empty or has only blank lines | Check the recording |
| `FILE:LINE: invalid JSON` | The line is not a single valid JSON value (or is not UTF-8, repeats a member name, or nests deeper than 64 levels) | Repair or remove the line |
| `FILE:LINE: sample is not a JSON object` | The line holds an array, string, or number | Each line must be an object |
| `FILE:LINE: missing member 'processes[0].name'` | A required member is absent | Add it |
| `FILE:LINE: invalid type for 'hostname'` | A member has the wrong type, or is `null` where not allowed | Fix the type |
| `FILE:LINE: invalid value for 'cpu.percent'` | A number is out of range, or a whole number has a fraction | Fix the value |
| `FILE:LINE: 'memory.available_bytes' exceeds 'memory.total_bytes'` | Inconsistent memory figures | Fix the values |
| `FILE:LINE: 'disks[1].used_bytes' exceeds 'disks[1].total_bytes'` | Inconsistent disk figures | Fix the values |
| `FILE:LINE: duplicate value for 'processes[2].pid'` | Two processes share one pid | Remove the duplicate |

All messages start with `dp-sysmon: `. In replay mode a message about a line is reported for the
first problem only, checking members in the order of the table in SNAPSHOT FILES.

## EXAMPLES

Show the current state of the machine:

```sh
dp-sysmon
```

The five processes using the most memory, sampled over half a second:

```sh
dp-sysmon --sort=mem --top=5 --interval=0.5
```

Watch the browser every two seconds until Ctrl-C:

```sh
dp-sysmon --filter=firefox --count=0 --interval=2
```

Record one sample per minute for a day, without printing anything:

```sh
dp-sysmon --count=1440 --interval=60 --format=json --output=day.jsonl > /dev/null
```

Replay the recording as tables, alphabetically, ten processes per sample:

```sh
dp-sysmon --snapshot=day.jsonl --sort=name --top=10
```

Replay from standard input and keep only Java processes, as JSON:

```text
$ dp-sysmon -s - -f json -m java -k pid < day.jsonl > java.jsonl
```

Show only the first sample of a recording:

```text
$ dp-sysmon --snapshot=day.jsonl --count=1 --top=0
Host:      alpha
Time:      2026-03-14T09:26:53Z
CPU:       37.5% busy; logical CPUs: 8
Memory:    10.0 GiB used of 16.0 GiB (62.5%); 6.0 GiB available
Processes: 8 total; 0 shown

MOUNT                       USED       TOTAL    USE%
/                       50.0 GiB   100.0 GiB    50.0

    PID    CPU%         RSS  NAME
```

Show the version:

```text
$ dp-sysmon --version
dp-sysmon (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-sysmon --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-sysmon [OPTION]...
Report CPU, memory, disk, and process telemetry as a table or JSON Lines.

Without --snapshot, samples the local system every --interval seconds.
With --snapshot, replays recorded samples (JSON Lines, one sample per
line) from FILE instead; FILE '-' means standard input.

Options:
  -s, --snapshot=FILE   replay samples from FILE instead of polling the system
  -f, --format=FORMAT   output format: table (default) or json
  -k, --sort=KEY        order processes by cpu (default), mem, pid, or name
  -n, --top=N           show at most N processes (0-1000000)
  -m, --filter=TEXT     show only processes whose name contains TEXT
                        (ASCII letters match case-insensitively)
  -i, --interval=SECS   seconds between live samples (0.1-86400, default 1)
  -c, --count=N         stop after N samples (0-1000000, 0 = no limit;
                        default 1 when live, 0 when replaying)
  -o, --output=FILE     also append each sample as a JSON line to FILE
      --help            display this help and exit
      --version         output version information and exit
```

## VERSION OUTPUT

```text
dp-sysmon (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-sysmon` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`) and
the time zone (`TZ`): live timestamps are always in UTC.

## PLATFORM NOTES

- **Linux:** data comes from `/proc` (`/proc/stat`, `/proc/meminfo`, `/proc/self/mounts`,
  `/proc/<pid>/stat`, `/proc/<pid>/statm`). Disks are the mounted file systems backed by a
  device path; pseudo file systems such as `proc` and `tmpfs` are not listed. Process names are
  the kernel's short command names (at most 15 bytes).
- **macOS:** CPU and memory come from the Mach and `sysctl` interfaces; disks are the local,
  browsable volumes under `/dev/`. On APFS several volumes share one container, so their sizes
  overlap. Process names are the executable's file name.
- **Windows:** data comes from the Win32 APIs (`GetSystemTimes`, `GlobalMemoryStatusEx`,
  Toolhelp process snapshots). Disks are fixed drives, shown as `C:\` and so on. Memory and CPU
  time of protected system processes are shown as `-` (`null`) unless you run with elevated
  rights; the tool never requires them. Output uses LF line endings, not CRLF. In PowerShell
  5.1, prefer `dp-sysmon -o FILE` over `>` redirection, which re-encodes output as UTF-16.
- **All platforms:** CPU percentages are measured over the interval, so the first sample
  appears one interval after start-up. Processes that start during an interval have no CPU
  share yet (`-`). Widths in the table count characters, so names containing East Asian wide
  characters can look wider than their column.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`top(1)`, `ps(1)`, `vmstat(8)`, `df(1)`, `proc(5)`; Windows Task Manager and `typeperf`;
JSON Lines (<https://jsonlines.org/>).

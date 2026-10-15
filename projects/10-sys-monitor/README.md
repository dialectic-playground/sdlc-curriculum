<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 10 — System Resource Telemetry Daemonic CLI (`dp-sysmon`)](#project-10--system-resource-telemetry-daemonic-cli-dp-sysmon)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 10 — System Resource Telemetry Daemonic CLI (`dp-sysmon`)

> Report CPU, memory, disk, and process telemetry like `top` and `ps` — once, at an interval,
> or indefinitely as a monitor — on Linux, macOS, and Windows, as a fixed-width table or as
> canonical JSON Lines that can be recorded and replayed byte for byte.

## Purpose

Every earlier project transformed input that the tests control. This one reads the running
system, whose state changes every millisecond and is exposed through entirely different
interfaces on each platform: `/proc` text files on Linux, Mach and `sysctl` calls on macOS, and
Win32 APIs or Performance Counters (PDH) on Windows. The project teaches how to keep such a tool
portable and testable: hide each operating system behind a small "reading" interface, compute
rates from two readings of cumulative counters, and make everything after collection — strict
input validation, sorting, unit formatting, layout, and serialization — a deterministic pipeline
that can be fed recorded data (`--snapshot`) and verified byte for byte.

## Operational scope

| In scope                                                                                         | Out of scope                                      |
| :----------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| Live sampling of CPU %, logical CPU count, memory, disks, and processes on Linux, macOS, Windows | Interactive full-screen TUI, colors, key commands |
| One-shot, N-sample, and unlimited ("daemonic") sampling with `--interval`, `--count`             | Killing or renicing processes                     |
| Replay of JSON Lines recordings from a file or stdin (`--snapshot`) with strict validation       | Per-core, per-thread, network, GPU metrics        |
| Table and canonical JSON Lines output; `--sort`, `--top`, `--filter`                             | Remote hosts, alerting, configuration files       |
| Appending samples to a recording (`--output`)                                                    | Elevated-privilege collection                     |

## Learning objectives

1. Design a platform abstraction: one interface, three back ends (`/proc`, Mach/sysctl, Win32),
   with no OS-specific code in the shared pipeline (NFR-02).
2. Compute rates correctly from cumulative counters sampled over a monotonic-clock interval,
   including process identity across samples and permission-denied processes (FR-15 … FR-17).
3. Separate non-deterministic collection from deterministic processing so that the whole
   pipeline is testable with fixtures (record/replay).
4. Validate untrusted structured input strictly — JSON edge cases (duplicate keys, lone
   surrogates, deep nesting, non-finite numbers), schema checks in a defined order, precise
   diagnostics with line numbers — while streaming in constant memory.
5. Specify and implement exact numeric formatting: round-half-even on exact binary values,
   integer-only percentage and binary-unit arithmetic without overflow.
6. Produce a canonical, round-trippable serialization (fixed member order, escaping, number
   format) and a fixed-width text layout that is byte-identical on every OS.

## What is provided

| Path                   | Contents                                                                                                                                         |
| :--------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-16)                                                                                                                |
| `specs/SRS.md`         | System requirements (FR-01 … FR-22, NFR-01 … NFR-10), snapshot schema, numeric formatting, table and JSON layouts, live telemetry sources per OS |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                                                          |
| `tests/public/`        | 10 visible black-box tests (replay mode) with exact expected outputs                                                                             |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                                                                             |
| `tests/fixtures/`      | Snapshot recordings shared by both suites                                                                                                        |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                              |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`. The HLD must show the
   platform abstraction and where each OS back end plugs in.
2. An implementation of `dp-sysmon`, with unit tests for the pure functions (SRS NFR-07) and
   the live-mode integration tests listed in SRS section 7, running on all three platforms.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-sysmon into BIN_DIR
make test           # unit + integration tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

Try it by hand:

```sh
dp-sysmon --sort=mem --top=10                     # live, one sample
dp-sysmon -c 5 -i 0.5 -f json -o rec.jsonl        # five samples, recorded
dp-sysmon --snapshot=rec.jsonl --sort=name -n 5   # replay the recording
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, the live-mode integration checks of SRS section 7 pass on all three, `make lint`
is clean, and every RTM row is _Verified_.

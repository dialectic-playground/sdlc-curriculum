"""Reference implementation of dp-sort-host (projects/34-parallel-sort/specs/SRS.md).

The worker runs concurrently in a thread and speaks the dp-sort-child protocol over a pair of
OS pipes (FR-09). The host sends the whole request and closes its end, sorts its own part
while the worker sorts, then merges the two sorted streams, receiving a worker value only when
the merge needs it (FR-11), and writes the --trace lines in that order (FR-12).
"""

from __future__ import annotations

import os
import threading

from . import common
from ._parallel_sort_worker import MAX_VALUES, selection_sort, serve
from .common import (AnsiRand, DataError, Option, UsageError, data_failure, file_failure,
                     handle_action, parse_args, parse_count, parse_int_token, parse_seed,
                     read_all, strip_eof_marker, tokenize, usage_failure)

TOOL = "dp-sort-host"
HELP_TEXT = """\
Usage: dp-sort-host [OPTION]... [FILE]
Sort integers with a concurrent worker and merge the two sorted halves.

With no FILE, or when FILE is -, read standard input.  Up to 100000 integers,
separated by whitespace, are read.  The first half is sorted here and the rest
by a worker running at the same time; the merged result is written one
integer per line.

Options:
  -r, --random=COUNT   sort COUNT pseudo-random integers 0-32767 (0-100000)
                         instead of reading input
      --seed=SEED      seed the pseudo-random generator (0-4294967295,
                         default 1)
  -t, --trace          write the messages exchanged with the worker and each
                         merge step to standard error
      --help           display this help and exit
      --version        output version information and exit
"""

OPTIONS: list[Option] = [
    Option("random", short="r", long="random", takes_value=True),
    Option("seed", long="seed", takes_value=True),
    Option("trace", short="t", long="trace"),
]


class WorkerFailure(Exception):
    """The worker could not be started, or its reply broke the protocol (FR-13)."""


def read_values(source: str) -> list[int]:
    """FR-02: every token of the input, validated before the worker starts."""
    data = strip_eof_marker(read_all(source))
    values = []
    for index, token in enumerate(tokenize(data)):
        if index == MAX_VALUES:
            raise DataError(source, token.line, "too many values")
        values.append(parse_int_token(token, source))
    return values


class Tracer:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def __call__(self, line: str) -> None:
        if self.enabled:
            common.err.write(line.encode() + b"\n")


class Worker:
    """A concurrent worker serving one dp-sort-child request over two pipes."""

    def __init__(self) -> None:
        request_read, request_write = os.pipe()
        reply_read, reply_write = os.pipe()
        self.request = os.fdopen(request_write, "wb")
        self.reply = os.fdopen(reply_read, "rb")
        worker_in = os.fdopen(request_read, "rb")
        worker_out = os.fdopen(reply_write, "wb")
        self.failed = False

        def run() -> None:
            try:
                serve(worker_in, worker_out, "-")
            except (DataError, OSError):
                self.failed = True
            finally:
                worker_in.close()
                worker_out.close()

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def send(self, line: bytes) -> None:
        self.request.write(line)

    def finish_request(self) -> None:
        self.request.close()

    def receive(self) -> int:
        line = self.reply.readline()
        if not line.endswith(b"\n"):
            raise WorkerFailure()
        try:
            value = int(line[:-1].decode("ascii"))
        except ValueError:
            raise WorkerFailure() from None
        if b"%d\n" % value != line:
            raise WorkerFailure()
        return value

    def close(self) -> None:
        self.thread.join()
        self.reply.close()
        if self.failed:
            raise WorkerFailure()


def parallel_sort(values: list[int], trace: Tracer) -> list[int]:
    host_size = len(values) // 2
    own, delegated = values[:host_size], values[host_size:]
    worker = Worker()
    try:
        # FR-10: the whole request is sent, and the channel closed, before the host sorts.
        for message in [len(delegated), *delegated]:
            trace(f"host -> child: {message}")
            worker.send(b"%d\n" % message)
        worker.finish_request()
        selection_sort(own)

        merged: list[int] = []
        remaining = len(delegated)
        pending: int | None = None

        def receive() -> int | None:
            nonlocal remaining
            if remaining == 0:
                return None
            remaining -= 1
            value = worker.receive()
            trace(f"child -> host: {value}")
            if pending is not None and value < pending:
                raise WorkerFailure()  # the reply must be non-decreasing
            return value

        pending = receive()
        index = 0
        while index < len(own) or pending is not None:
            if pending is None or (index < len(own) and own[index] <= pending):
                merged.append(own[index])
                trace(f"merge: {own[index]} from host")
                index += 1
            else:
                merged.append(pending)
                trace(f"merge: {pending} from child")
                pending = receive()
    finally:
        worker.finish_request()
    worker.close()
    return merged


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        random_count = None
        if "random" in parsed.values:
            random_count = parse_count(str(parsed.values["random"]), parsed.spelled["random"],
                                       0, MAX_VALUES)
        seed = parse_seed(parsed)
        allowed_operands = 0 if random_count is not None else 1
        if len(parsed.operands) > allowed_operands:
            raise UsageError(f"extra operand '{parsed.operands[allowed_operands]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    if random_count is not None:
        generator = AnsiRand(seed)
        values = [generator.next() for _ in range(random_count)]
    else:
        source = parsed.operands[0] if parsed.operands else "-"
        try:
            values = read_values(source)
        except DataError as error:
            return data_failure(TOOL, error)
        except OSError as error:
            file_failure(TOOL, source, error)
            return 1

    trace = Tracer(bool(parsed.values.get("trace")))
    try:
        merged = parallel_sort(values, trace)
    except (WorkerFailure, OSError):
        common.diagnose(TOOL, "worker failed")
        return 1
    common.write(b"".join(b"%d\n" % value for value in merged))
    return 0

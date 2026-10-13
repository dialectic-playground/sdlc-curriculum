"""Best-effort live telemetry for dp-sysmon (SRS section 3.11, FR-15 .. FR-18).

A :class:`Reading` is a raw point-in-time observation of cumulative counters. Two consecutive
readings make one :class:`Sample` (:func:`make_sample`): CPU percentages are computed from the
counter deltas over the elapsed monotonic time. Every value that cannot be obtained is
``None`` (JSON ``null``); collection itself never fails.

Platform back ends (standard library only):

* Linux: ``/proc/stat``, ``/proc/meminfo``, ``/proc/self/mounts`` + ``statvfs``,
  ``/proc/<pid>/stat`` and ``/proc/<pid>/statm``.
* macOS: ``host_statistics`` (ctypes) for CPU ticks, ``sysctl``, ``vm_stat``, ``mount`` +
  ``statvfs``, and ``ps`` for processes.
* Windows: ``GetSystemTimes``, ``GlobalMemoryStatusEx``, ``GetLogicalDriveStringsW`` +
  ``GetDiskFreeSpaceExW``, Toolhelp32 process enumeration with ``GetProcessTimes`` and
  ``K32GetProcessMemoryInfo`` (ctypes).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field

from ._sysmon_model import (MAX_INTEGER, MAX_PROCESS_PERCENT, Disk, Process, Sample,
                            round1_tenths)


@dataclass
class ProcessReading:
    name: str
    identity: object                # start time where available, to detect PID reuse
    cpu_seconds: float | None       # cumulative user + system CPU time
    rss_bytes: int | None


@dataclass
class Reading:
    monotonic: float
    wall: float
    hostname: str = ""
    cpu_count: int | None = None
    cpu_ticks: tuple[float, float] | None = None   # (busy, total), cumulative
    memory_total: int | None = None
    memory_available: int | None = None
    disks: list[Disk] = field(default_factory=list)
    processes: dict[int, ProcessReading] = field(default_factory=dict)


def _clamp_bytes(value: int | None) -> int | None:
    if value is None or value < 0:
        return None
    return min(value, MAX_INTEGER)


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", "replace")


def _statvfs_disk(mount: str) -> Disk | None:
    try:
        info = os.statvfs(mount)  # type: ignore[attr-defined]
    except OSError:
        return None
    total = info.f_blocks * info.f_frsize
    used = (info.f_blocks - info.f_bfree) * info.f_frsize
    if total > MAX_INTEGER or used < 0 or used > total:
        return None
    return Disk(mount, total, used)


# --- Linux -------------------------------------------------------------------------------


def _unescape_mount(field_text: str) -> str:
    """Decode the octal escapes (\\040 etc.) used in /proc/self/mounts."""
    raw = field_text.encode("utf-8", "surrogateescape")
    out = bytearray()
    index = 0
    while index < len(raw):
        if raw[index:index + 1] == b"\\" and raw[index + 1:index + 4].isdigit():
            out.append(int(raw[index + 1:index + 4], 8) & 0xFF)
            index += 4
        else:
            out.append(raw[index])
            index += 1
    return _decode(bytes(out))


def _read_linux(reading: Reading) -> None:
    try:
        with open("/proc/stat", "rb") as handle:
            lines = handle.read().splitlines()
        cpus = 0
        for line in lines:
            if line.startswith(b"cpu "):
                values = [int(v) for v in line.split()[1:9]]
                values += [0] * (8 - len(values))
                total = sum(values)
                idle = values[3] + values[4]
                reading.cpu_ticks = (float(total - idle), float(total))
            elif line.startswith(b"cpu") and line[3:4].isdigit():
                cpus += 1
        reading.cpu_count = cpus or None
    except (OSError, ValueError):
        pass

    try:
        meminfo: dict[bytes, int] = {}
        with open("/proc/meminfo", "rb") as handle:
            for line in handle:
                key, _, rest = line.partition(b":")
                parts = rest.split()
                if parts:
                    meminfo[key] = int(parts[0]) * 1024
        reading.memory_total = _clamp_bytes(meminfo.get(b"MemTotal"))
        reading.memory_available = _clamp_bytes(meminfo.get(b"MemAvailable"))
    except (OSError, ValueError):
        pass

    try:
        mounts: dict[str, None] = {}
        with open("/proc/self/mounts", "rb") as handle:
            for line in handle:
                fields = line.split()
                if len(fields) >= 2 and fields[0].startswith(b"/"):
                    mount = _unescape_mount(os.fsdecode(fields[1]))
                    mounts.pop(mount, None)
                    mounts[mount] = None
        for mount in mounts:
            disk = _statvfs_disk(mount)
            if disk is not None:
                reading.disks.append(disk)
    except OSError:
        pass

    ticks = os.sysconf("SC_CLK_TCK")
    page = os.sysconf("SC_PAGE_SIZE")
    try:
        entries = [e for e in os.listdir("/proc") if e.isdigit()]
    except OSError:
        entries = []
    for entry in entries:
        pid = int(entry)
        try:
            with open(f"/proc/{entry}/stat", "rb") as handle:
                stat = handle.read()
        except OSError:
            continue  # vanished or unreadable: omitted (FR-17)
        open_paren, close_paren = stat.find(b"("), stat.rfind(b")")
        if open_paren < 0 or close_paren < open_paren:
            continue
        name = _decode(stat[open_paren + 1:close_paren])
        rest = stat[close_paren + 1:].split()
        cpu_seconds: float | None = None
        identity: object = None
        try:
            cpu_seconds = (int(rest[11]) + int(rest[12])) / ticks
            identity = int(rest[19])
        except (IndexError, ValueError):
            pass
        rss: int | None = None
        try:
            with open(f"/proc/{entry}/statm", "rb") as handle:
                rss = _clamp_bytes(int(handle.read().split()[1]) * page)
        except (OSError, IndexError, ValueError):
            pass
        reading.processes[pid] = ProcessReading(name, identity, cpu_seconds, rss)


# --- macOS -------------------------------------------------------------------------------


def _command(*argv: str) -> str | None:
    try:
        completed = subprocess.run(list(argv), capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return _decode(completed.stdout)


def _darwin_cpu_ticks() -> tuple[float, float] | None:
    try:
        import ctypes
        libc = ctypes.CDLL("/usr/lib/libSystem.dylib")
        libc.mach_host_self.restype = ctypes.c_uint32
        host = libc.mach_host_self()
        info = (ctypes.c_uint32 * 4)()     # user, system, idle, nice
        count = ctypes.c_uint32(4)
        host_cpu_load_info = 3
        if libc.host_statistics(ctypes.c_uint32(host), host_cpu_load_info, info,
                                ctypes.byref(count)) != 0:
            return None
        user, system, idle, nice = (float(v) for v in info)
        total = user + system + idle + nice
        return (total - idle, total)
    except (OSError, AttributeError, ValueError):
        return None


def _parse_cputime(text: str) -> float | None:
    """Parse ps TIME values such as ``0:01.23``, ``1:02:03.45``, or ``2-01:02:03``."""
    try:
        days = 0
        if "-" in text:
            day_text, text = text.split("-", 1)
            days = int(day_text)
        seconds = 0.0
        for part in text.split(":"):
            seconds = seconds * 60 + float(part)
        return days * 86400 + seconds
    except ValueError:
        return None


def _read_darwin(reading: Reading) -> None:
    reading.cpu_ticks = _darwin_cpu_ticks()
    cpus = _command("/usr/sbin/sysctl", "-n", "hw.logicalcpu")
    if cpus and cpus.strip().isdigit() and int(cpus) >= 1:
        reading.cpu_count = int(cpus)
    memsize = _command("/usr/sbin/sysctl", "-n", "hw.memsize")
    if memsize and memsize.strip().isdigit():
        reading.memory_total = _clamp_bytes(int(memsize))
    vm_stat = _command("/usr/bin/vm_stat")
    if vm_stat:
        page_size, pages = 4096, {}
        for line in vm_stat.splitlines():
            if "page size of" in line:
                digits = "".join(c for c in line.split("page size of")[1] if c.isdigit())
                page_size = int(digits or "4096")
            key, _, value = line.partition(":")
            value = value.strip().rstrip(".")
            if value.isdigit():
                pages[key.strip()] = int(value)
        try:
            free = (pages["Pages free"] + pages["Pages inactive"]
                    + pages.get("Pages speculative", 0))
            reading.memory_available = _clamp_bytes(free * page_size)
        except KeyError:
            pass
        if (reading.memory_total is not None and reading.memory_available is not None
                and reading.memory_available > reading.memory_total):
            reading.memory_available = reading.memory_total
    mount_text = _command("/sbin/mount")
    for line in (mount_text or "").splitlines():
        device, separator, rest = line.partition(" on ")
        options_at = rest.rfind(" (")
        if not separator or options_at < 0 or not device.startswith("/dev/"):
            continue
        if "nobrowse" in rest[options_at:]:
            continue
        disk = _statvfs_disk(rest[:options_at])
        if disk is not None:
            reading.disks.append(disk)
    ps_text = _command("/bin/ps", "-A", "-o", "pid=", "-o", "rss=", "-o", "time=",
                       "-o", "comm=")
    for line in (ps_text or "").splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        rss = int(parts[1]) * 1024 if parts[1].isdigit() else None
        name = parts[3].rsplit("/", 1)[-1]
        reading.processes[int(parts[0])] = ProcessReading(
            name, None, _parse_cputime(parts[2]), _clamp_bytes(rss))


# --- Windows -----------------------------------------------------------------------------


def _read_windows(reading: Reading) -> None:  # pragma: no cover - exercised on Windows CI
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class FILETIME(ctypes.Structure):
        _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]

        def value(self) -> int:
            return (self.high << 32) | self.low

    idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
    if kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        total = kernel.value() + user.value()          # kernel time includes idle time
        reading.cpu_ticks = (float(total - idle.value()), float(total))

    try:
        kernel32.GetActiveProcessorCount.restype = wintypes.DWORD
        count = kernel32.GetActiveProcessorCount(wintypes.WORD(0xFFFF))
        reading.cpu_count = int(count) or None
    except AttributeError:
        reading.cpu_count = os.cpu_count()

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD),
                    ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                    ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                    ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                    ("ullAvailExtendedVirtual", ctypes.c_uint64)]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        reading.memory_total = _clamp_bytes(status.ullTotalPhys)
        reading.memory_available = _clamp_bytes(status.ullAvailPhys)

    buffer = ctypes.create_unicode_buffer(512)
    length = kernel32.GetLogicalDriveStringsW(len(buffer), buffer)
    roots = [r for r in buffer[:length].split("\0") if r]
    drive_fixed = 3
    for root in sorted(roots, key=lambda r: r.encode("utf-8")):
        if kernel32.GetDriveTypeW(root) != drive_fixed:
            continue
        free_to_caller = ctypes.c_uint64()
        total_bytes = ctypes.c_uint64()
        total_free = ctypes.c_uint64()
        if kernel32.GetDiskFreeSpaceExW(root, ctypes.byref(free_to_caller),
                                        ctypes.byref(total_bytes), ctypes.byref(total_free)):
            total = total_bytes.value
            used = total - total_free.value
            if 0 <= used <= total <= MAX_INTEGER:
                reading.disks.append(Disk(root, total, used))

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_void_p),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.OpenProcess.restype = wintypes.HANDLE
    snapshot = kernel32.CreateToolhelp32Snapshot(wintypes.DWORD(2), wintypes.DWORD(0))
    invalid_handle = wintypes.HANDLE(-1).value
    if not snapshot or snapshot == invalid_handle:
        return
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        more = kernel32.Process32FirstW(wintypes.HANDLE(snapshot), ctypes.byref(entry))
        while more:
            pid = int(entry.th32ProcessID)
            name = entry.szExeFile
            cpu_seconds: float | None = None
            identity: object = None
            rss: int | None = None
            handle = kernel32.OpenProcess(wintypes.DWORD(0x1000), False, wintypes.DWORD(pid))
            if handle:
                try:
                    creation, exited, k_time, u_time = (FILETIME(), FILETIME(), FILETIME(),
                                                        FILETIME())
                    if kernel32.GetProcessTimes(wintypes.HANDLE(handle), ctypes.byref(creation),
                                                ctypes.byref(exited), ctypes.byref(k_time),
                                                ctypes.byref(u_time)):
                        cpu_seconds = (k_time.value() + u_time.value()) / 1e7
                        identity = creation.value()
                    counters = PROCESS_MEMORY_COUNTERS()
                    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
                    if kernel32.K32GetProcessMemoryInfo(wintypes.HANDLE(handle),
                                                        ctypes.byref(counters), counters.cb):
                        rss = _clamp_bytes(int(counters.WorkingSetSize))
                finally:
                    kernel32.CloseHandle(wintypes.HANDLE(handle))
            reading.processes[pid] = ProcessReading(name, identity, cpu_seconds, rss)
            more = kernel32.Process32NextW(wintypes.HANDLE(snapshot), ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(wintypes.HANDLE(snapshot))


def _windows_hostname() -> str:  # pragma: no cover - exercised on Windows CI
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL("kernel32")
    size = wintypes.DWORD(0)
    computer_name_dns_hostname = 1
    kernel32.GetComputerNameExW(computer_name_dns_hostname, None, ctypes.byref(size))
    buffer = ctypes.create_unicode_buffer(size.value + 1)
    if kernel32.GetComputerNameExW(computer_name_dns_hostname, buffer, ctypes.byref(size)):
        return buffer.value
    return ""


# --- public API --------------------------------------------------------------------------


def read() -> Reading:
    """Take one raw reading of the local system."""
    reading = Reading(monotonic=time.monotonic(), wall=time.time())
    try:
        if os.name == "nt":
            reading.hostname = _windows_hostname()
            _read_windows(reading)
        else:
            reading.hostname = platform.node()
            if sys.platform == "darwin":
                _read_darwin(reading)
            elif os.path.isdir("/proc"):
                _read_linux(reading)
    except Exception:  # noqa: BLE001 - best effort: keep whatever was collected (FR-15)
        pass
    if reading.cpu_count is None:
        reading.cpu_count = os.cpu_count()
    return reading


def make_sample(previous: Reading, current: Reading) -> Sample:
    """Combine two consecutive readings into one sample (FR-16)."""
    cpu_tenths = None
    if previous.cpu_ticks is not None and current.cpu_ticks is not None:
        busy = current.cpu_ticks[0] - previous.cpu_ticks[0]
        total = current.cpu_ticks[1] - previous.cpu_ticks[1]
        if total > 0:
            cpu_tenths = round1_tenths(min(max(busy / total * 100.0, 0.0), 100.0))

    elapsed = current.monotonic - previous.monotonic
    processes = []
    for pid, proc in current.processes.items():
        if pid > MAX_INTEGER:
            continue
        before = previous.processes.get(pid)
        tenths = None
        if (before is not None and before.identity == proc.identity and elapsed > 0
                and before.cpu_seconds is not None and proc.cpu_seconds is not None):
            percent = max(proc.cpu_seconds - before.cpu_seconds, 0.0) / elapsed * 100.0
            tenths = round1_tenths(min(percent, MAX_PROCESS_PERCENT))
        processes.append(Process(pid, proc.name, tenths, proc.rss_bytes))

    available = current.memory_available
    if current.memory_total is not None and available is not None:
        available = min(available, current.memory_total)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(current.wall))
    return Sample(stamp, current.hostname, current.cpu_count, cpu_tenths,
                  current.memory_total, available,
                  tuple(current.disks), tuple(processes))

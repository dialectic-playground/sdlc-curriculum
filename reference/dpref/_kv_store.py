"""Storage engine shared by dp-kv's CLI and HTTP front ends (projects/09-kv-store SRS).

Responsibilities:

* the canonical on-disk document (SRS section 5.1): parsing, validation, and serialization;
* key and value rules (SRS FR-03, FR-04);
* sidecar locking on ``PATH.lock`` (flock / LockFileEx; SRS FR-20, NFR-04);
* atomic replacement of the store through ``PATH.tmp`` + fsync + rename (SRS FR-21).
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import stat
import time
from typing import Callable, Iterator, TypeVar

from .common import file_error_reason

FORMAT_NAME = "dp-kv"
FORMAT_VERSION = 1
MAX_KEY_LENGTH = 256
MAX_VALUE_BYTES = 65536
LOCK_TIMEOUT_SECONDS = 5.0
LOCK_POLL_SECONDS = 0.025
INVALID_STORE_REASON = "not a valid dp-kv store file"
LOCKED_REASON = "store is locked"

_KEY_PATTERN = re.compile(r"[A-Za-z0-9._:-]{1,%d}" % MAX_KEY_LENGTH, re.ASCII)
_SHORT_ESCAPES = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n",
                  "\r": "\\r", "\t": "\\t"}

T = TypeVar("T")
Data = dict[str, str]


class StoreError(Exception):
    """A runtime failure tied to a path. ``str(error)`` is ``<path>: <reason>``."""

    def __init__(self, path: str, reason: str, kind: str = "io"):
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason
        self.kind = kind  # "io", "invalid", or "locked"


# --- key and value rules ------------------------------------------------------------------

def is_valid_key(key: str) -> bool:
    return _KEY_PATTERN.fullmatch(key) is not None


def is_valid_prefix(prefix: str) -> bool:
    return prefix == "" or is_valid_key(prefix)


def value_problem(value: str) -> str | None:
    """Return ``"utf8"`` or ``"length"`` if ``value`` is not storable, else None."""
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError:  # lone surrogates: undecodable argv bytes or JSON \ud800
        return "utf8"
    return "length" if len(encoded) > MAX_VALUE_BYTES else None


# --- canonical document --------------------------------------------------------------------

def json_string(text: str) -> str:
    """Encode ``text`` as a JSON string literal using the SRS 5.1 escaping rules."""
    pieces = ['"']
    for char in text:
        if char in _SHORT_ESCAPES:
            pieces.append(_SHORT_ESCAPES[char])
        elif char < " ":
            pieces.append("\\u%04x" % ord(char))
        else:
            pieces.append(char)
    pieces.append('"')
    return "".join(pieces)


def sorted_keys(data: Data) -> list[str]:
    return sorted(data, key=lambda k: k.encode("utf-8"))


def encode_document(data: Data) -> bytes:
    """Serialize a store to its canonical bytes (SRS 5.1)."""
    lines = ["{", f'  "format": "{FORMAT_NAME}",', f'  "version": {FORMAT_VERSION},']
    if not data:
        lines.append('  "data": {}')
    else:
        lines.append('  "data": {')
        keys = sorted_keys(data)
        for index, key in enumerate(keys):
            comma = "," if index < len(keys) - 1 else ""
            lines.append(f"    {json_string(key)}: {json_string(data[key])}{comma}")
        lines.append("  }")
    lines.append("}")
    return ("\n".join(lines) + "\n").encode("utf-8")


class _InvalidJson(Exception):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise _InvalidJson("duplicate member name")
        result[name] = value
    return result


def _reject_constant(name: str) -> object:
    raise _InvalidJson(f"non-standard constant {name}")


def parse_json(raw: bytes) -> object:
    """Parse strict RFC 8259 JSON from UTF-8 bytes (SRS 5.2). Raises ValueError."""
    try:
        text = raw.decode("utf-8")
        return json.loads(text, object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError, _InvalidJson, RecursionError) as error:
        raise ValueError(str(error)) from None


def parse_document(raw: bytes) -> Data | None:
    """Return the data of a valid dp-kv document (SRS 5.2), or None if it is invalid."""
    try:
        document = parse_json(raw)
    except ValueError:
        return None
    if not isinstance(document, dict) or set(document) != {"format", "version", "data"}:
        return None
    if document["format"] != FORMAT_NAME:
        return None
    version = document["version"]
    if type(version) is not int or version != FORMAT_VERSION:
        return None
    data = document["data"]
    if not isinstance(data, dict):
        return None
    for key, value in data.items():
        if not is_valid_key(key) or not isinstance(value, str) or value_problem(value):
            return None
    return data  # type: ignore[return-value]


# --- locking (SRS FR-20, NFR-04) -----------------------------------------------------------

if os.name == "nt":
    import ctypes
    import msvcrt
    from ctypes import wintypes

    class _Overlapped(ctypes.Structure):
        _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                    ("Offset", wintypes.DWORD), ("OffsetHigh", wintypes.DWORD),
                    ("hEvent", wintypes.HANDLE)]

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _LockFileEx = _kernel32.LockFileEx
    _LockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                            wintypes.DWORD, ctypes.POINTER(_Overlapped)]
    _LockFileEx.restype = wintypes.BOOL
    _UnlockFileEx = _kernel32.UnlockFileEx
    _UnlockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                              ctypes.POINTER(_Overlapped)]
    _UnlockFileEx.restype = wintypes.BOOL
    _LOCKFILE_FAIL_IMMEDIATELY = 0x1
    _LOCKFILE_EXCLUSIVE_LOCK = 0x2
    _ERROR_LOCK_VIOLATION = 33
    _ERROR_IO_PENDING = 997

    def _try_lock(fd: int, exclusive: bool) -> bool:
        """LockFileEx on byte 0 (length 1) of the lock file, without waiting."""
        flags = _LOCKFILE_FAIL_IMMEDIATELY | (_LOCKFILE_EXCLUSIVE_LOCK if exclusive else 0)
        overlapped = _Overlapped()
        if _LockFileEx(msvcrt.get_osfhandle(fd), flags, 0, 1, 0, ctypes.byref(overlapped)):
            return True
        code = ctypes.get_last_error()
        if code in (_ERROR_LOCK_VIOLATION, _ERROR_IO_PENDING):
            return False
        raise ctypes.WinError(code)

    def _unlock(fd: int) -> None:
        overlapped = _Overlapped()
        _UnlockFileEx(msvcrt.get_osfhandle(fd), 0, 1, 0, ctypes.byref(overlapped))
else:
    import fcntl

    def _try_lock(fd: int, exclusive: bool) -> bool:
        """flock(2) on the whole lock file, without waiting."""
        try:
            fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


@contextlib.contextmanager
def _locked(lock_path: str, exclusive: bool, store_path: str) -> Iterator[None]:
    """Hold a shared or exclusive lock on ``lock_path`` (created if absent).

    Raises OSError if the lock file cannot be opened, or StoreError(kind="locked") naming
    ``store_path`` if the lock is not granted within LOCK_TIMEOUT_SECONDS.
    """
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o666)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while not _try_lock(fd, exclusive):
            if time.monotonic() >= deadline:
                raise StoreError(store_path, LOCKED_REASON, "locked")
            time.sleep(LOCK_POLL_SECONDS)
        try:
            yield
        finally:
            _unlock(fd)
    finally:
        os.close(fd)


# --- the store -----------------------------------------------------------------------------

class Store:
    """A dp-kv store file at ``path`` with its sidecar ``path.lock`` and ``path.tmp``."""

    def __init__(self, path: str):
        self.path = path
        self.lock_path = path + ".lock"
        self.temp_path = path + ".tmp"

    def read(self) -> Data:
        """Return the store's data under a shared lock (SRS FR-16, FR-20)."""
        try:
            with _locked(self.lock_path, False, self.path):
                return self._load()
        except StoreError:
            raise
        except (FileNotFoundError, NotADirectoryError):
            return {}  # the directory does not exist, so neither does the store (FR-16)
        except OSError as error:
            raise StoreError(self.lock_path, file_error_reason(error, self.lock_path)) from None

    def update(self, mutate: Callable[[Data], tuple[bool, T]]) -> T:
        """Read-modify-write under an exclusive lock (SRS FR-20, FR-21).

        ``mutate`` edits the data in place and returns ``(changed, result)``; the store is
        rewritten only when ``changed`` is true.
        """
        try:
            with _locked(self.lock_path, True, self.path):
                data = self._load()
                changed, result = mutate(data)
                if changed:
                    self._save(data)
                return result
        except StoreError:
            raise
        except OSError as error:
            raise StoreError(self.lock_path, file_error_reason(error, self.lock_path)) from None

    def _load(self) -> Data:
        if os.path.isdir(self.path):
            raise StoreError(self.path, "Is a directory")
        try:
            with open(self.path, "rb") as handle:
                raw = handle.read()
        except FileNotFoundError:
            return {}
        except OSError as error:
            raise StoreError(self.path, file_error_reason(error, self.path)) from None
        data = parse_document(raw)
        if data is None:
            raise StoreError(self.path, INVALID_STORE_REASON, "invalid")
        return data

    def _save(self, data: Data) -> None:
        payload = encode_document(data)
        try:
            fd = os.open(self.temp_path,
                         os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_BINARY", 0),
                         0o666)
            try:
                view = memoryview(payload)
                while view:
                    view = view[os.write(fd, view):]
                os.fsync(fd)
            finally:
                os.close(fd)
            self._copy_mode()
            os.replace(self.temp_path, self.path)
        except OSError as error:
            with contextlib.suppress(OSError):
                os.remove(self.temp_path)
            raise StoreError(self.path, file_error_reason(error, self.path)) from None
        self._sync_directory()

    def _copy_mode(self) -> None:
        """POSIX: keep the permission bits of the store being replaced (SRS FR-21)."""
        if os.name == "nt":
            return
        try:
            mode = stat.S_IMODE(os.stat(self.path).st_mode)
        except FileNotFoundError:
            return
        os.chmod(self.temp_path, mode)

    def _sync_directory(self) -> None:
        """POSIX: fsync the containing directory so the rename itself is durable."""
        if os.name == "nt":
            return
        directory = os.path.dirname(self.path) or "."
        with contextlib.suppress(OSError):
            fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)

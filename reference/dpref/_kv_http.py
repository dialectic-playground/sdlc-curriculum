"""HTTP/REST front end of dp-kv (``dp-kv serve``; projects/09-kv-store SRS section 6).

Built on :mod:`http.server`. Every request opens the store, takes the appropriate lock, and
releases it before the response is sent, so the CLI and the server can share a store.
"""

from __future__ import annotations

import ipaddress
import os
import signal
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, unquote

from ._kv_store import (
    MAX_VALUE_BYTES,
    Data,
    Store,
    StoreError,
    is_valid_key,
    is_valid_prefix,
    json_string,
    parse_json,
    sorted_keys,
    value_problem,
)

MAX_BODY_BYTES = 524288
REQUEST_TIMEOUT_SECONDS = 10
COLLECTION = "/v1/keys"
ITEM_PREFIX = "/v1/keys/"
HEALTH = "/v1/health"
ALLOW = {HEALTH: "GET", COLLECTION: "GET", ITEM_PREFIX: "GET, PUT, DELETE"}

ERRORS = {  # code -> (status, message); key_not_found and store_* append detail
    "bad_request": (400, "malformed HTTP request"),
    "invalid_key": (400, "invalid key"),
    "invalid_prefix": (400, "invalid prefix"),
    "invalid_json": (400, "request body is not valid JSON"),
    "invalid_body": (
        400,
        (
            "request body must be a JSON object with exactly one member, "
            '"value", whose value is a string'
        ),
    ),
    "key_not_found": (404, "key not found: "),
    "not_found": (404, "resource not found"),
    "method_not_allowed": (405, "method not allowed"),
    "length_required": (411, "Content-Length header required"),
    "payload_too_large": (
        413,
        f"request body too large (maximum {MAX_BODY_BYTES} bytes)",
    ),
    "value_too_long": (413, f"value too long (maximum {MAX_VALUE_BYTES} bytes)"),
    "store_error": (500, ""),
    "store_locked": (503, ""),
}


class ApiError(Exception):
    def __init__(self, code: str, detail: str = "", allow: str | None = None):
        status, message = ERRORS[code]
        super().__init__(message + detail)
        self.code = code
        self.status = status
        self.message = message + detail
        self.allow = allow


def compact_json(value: object) -> str:
    """Compact JSON with the store's string escaping (SRS 6.2 rule 2)."""
    if isinstance(value, str):
        return json_string(value)
    if isinstance(value, list):
        return "[" + ",".join(compact_json(item) for item in value) + "]"
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(f"{json_string(k)}:{compact_json(v)}" for k, v in value.items())
            + "}"
        )
    raise TypeError(type(value))


class KvRequestHandler(BaseHTTPRequestHandler):
    timeout = REQUEST_TIMEOUT_SECONDS
    store: Store  # set on the subclass created by make_server

    # Any method name dispatches to the router, so unknown methods get 405, not 501.
    def __getattr__(self, name: str):
        if name.startswith("do_"):
            return self._dispatch
        raise AttributeError(name)

    def log_message(self, format: str, *args: object) -> None:
        """No per-request logging (SRS FR-33)."""

    def version_string(self) -> str:
        return "dp-kv/1.0.0"

    def send_error(
        self, code: int, message: str | None = None, explain: str | None = None
    ) -> None:
        """Protocol-level failures detected by http.server (bad request line, etc.)."""
        _, text = ERRORS["bad_request"]
        self._respond(code, {"error": {"code": "bad_request", "message": text}}, {})

    # --- routing ------------------------------------------------------------------------

    def _dispatch(self) -> None:
        try:
            status, body, headers = self._route()
        except ApiError as error:
            status = error.status
            body = {"error": {"code": error.code, "message": error.message}}
            headers = {"Allow": error.allow} if error.allow else {}
        self._respond(status, body, headers)

    def _route(self) -> tuple[int, object | None, dict[str, str]]:
        path, _, query = self.path.partition("?")
        if path == HEALTH:
            self._require(HEALTH, ("GET",))
            return 200, {"status": "ok"}, {}
        if path == COLLECTION:
            self._require(COLLECTION, ("GET",))
            return self._list(query)
        if path.startswith(ITEM_PREFIX):
            self._require(ITEM_PREFIX, ("GET", "PUT", "DELETE"))
            try:
                key = unquote(path[len(ITEM_PREFIX) :], errors="strict")
            except UnicodeDecodeError:
                raise ApiError("invalid_key") from None
            if not is_valid_key(key):
                raise ApiError("invalid_key")
            handler = {"GET": self._get, "PUT": self._put, "DELETE": self._delete}
            return handler[self.command](key)
        raise ApiError("not_found")

    def _require(self, route: str, methods: tuple[str, ...]) -> None:
        if self.command not in methods:
            raise ApiError("method_not_allowed", allow=ALLOW[route])

    # --- operations ---------------------------------------------------------------------

    def _list(self, query: str) -> tuple[int, object, dict[str, str]]:
        prefix = ""
        for name, value in parse_qsl(query, keep_blank_values=True, errors="replace"):
            if name == "prefix":
                prefix = value
        if not is_valid_prefix(prefix):
            raise ApiError("invalid_prefix")
        data = self._call(self.store.read)
        return 200, {"keys": [k for k in sorted_keys(data) if k.startswith(prefix)]}, {}

    def _get(self, key: str) -> tuple[int, object, dict[str, str]]:
        data = self._call(self.store.read)
        if key not in data:
            raise ApiError("key_not_found", key)
        return 200, {"key": key, "value": data[key]}, {}

    def _put(self, key: str) -> tuple[int, object, dict[str, str]]:
        value = self._read_value()

        def assign(data: Data) -> tuple[bool, bool]:
            created = key not in data
            data[key] = value
            return True, created

        created = self._call(lambda: self.store.update(assign))
        headers = {"Location": ITEM_PREFIX + key} if created else {}
        return (201 if created else 200), {"key": key, "value": value}, headers

    def _delete(self, key: str) -> tuple[int, None, dict[str, str]]:
        def remove(data: Data) -> tuple[bool, bool]:
            if key not in data:
                return False, False
            del data[key]
            return True, True

        if not self._call(lambda: self.store.update(remove)):
            raise ApiError("key_not_found", key)
        return 204, None, {}

    def _read_value(self) -> str:
        length_header = self.headers.get("Content-Length")
        if (
            length_header is None
            or not length_header.isascii()
            or not length_header.isdigit()
        ):
            raise ApiError("length_required")
        length = int(length_header)
        if length > MAX_BODY_BYTES:
            raise ApiError("payload_too_large")
        raw = self.rfile.read(length)
        try:
            document = parse_json(raw)
        except ValueError:
            raise ApiError("invalid_json") from None
        if (
            not isinstance(document, dict)
            or set(document) != {"value"}
            or not isinstance(document["value"], str)
        ):
            raise ApiError("invalid_body")
        value = document["value"]
        problem = value_problem(value)
        if problem == "utf8":
            raise ApiError("invalid_body")
        if problem == "length":
            raise ApiError("value_too_long")
        return value

    @staticmethod
    def _call(operation):  # type: ignore[no-untyped-def]
        try:
            return operation()
        except StoreError as error:
            raise ApiError(
                "store_locked" if error.kind == "locked" else "store_error", str(error)
            ) from None

    # --- response -----------------------------------------------------------------------

    def _respond(
        self, status: int, body: object | None, headers: dict[str, str]
    ) -> None:
        payload = b"" if body is None else (compact_json(body) + "\n").encode("utf-8")
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD" and payload:
            self.wfile.write(payload)
        self.close_connection = True


class KvServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != "nt"  # Windows SO_REUSEADDR allows port hijacking

    def server_bind(self) -> None:
        if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def is_valid_host(host: str) -> bool:
    """HOST must be a numeric IPv4 or IPv6 address without a zone identifier (SRS FR-22)."""
    if "%" in host:
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def listen_reason(error: OSError) -> str:
    import errno

    if error.errno in (errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", -1)):
        return "Address already in use"
    if isinstance(error, PermissionError) or error.errno in (
        errno.EACCES,
        getattr(errno, "WSAEACCES", -1),
    ):
        return "Permission denied"
    return "Address not available"


def make_server(store: Store, host: str, port: int) -> KvServer:
    handler = type("BoundKvRequestHandler", (KvRequestHandler,), {"store": store})
    family = (
        socket.AF_INET6 if ipaddress.ip_address(host).version == 6 else socket.AF_INET
    )
    server_class = type("BoundKvServer", (KvServer,), {"address_family": family})
    return server_class((host, port), handler)


def authority(host: str, port: int) -> str:
    """``HOST:PORT``, with an IPv6 HOST in brackets (RFC 3986)."""
    return f"[{host}]:{port}" if ":" in host else f"{host}:{port}"


def serve(store: Store, host: str, port: int, announce) -> int:  # type: ignore[no-untyped-def]
    """Run the server until SIGINT/SIGTERM (Ctrl+C / Ctrl+Break on Windows). Returns 0.

    Raises OSError (with a fixed reason via :func:`listen_reason`) if binding fails.
    """
    server = make_server(store, host, port)
    announce(f"listening on http://{authority(host, server.server_address[1])}")
    stop = threading.Event()

    def request_stop(signum, frame):  # type: ignore[no-untyped-def]
        stop.set()

    previous = {}
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        if hasattr(signal, name):
            previous[name] = signal.signal(getattr(signal, name), request_stop)
    worker = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True
    )
    worker.start()
    try:
        while not stop.wait(0.2):
            pass
    finally:
        server.shutdown()
        server.server_close()
        for name, handler in previous.items():
            signal.signal(getattr(signal, name), handler)
    sys.stdout.flush()
    return 0

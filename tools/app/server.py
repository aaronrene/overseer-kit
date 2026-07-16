"""Stdlib loopback HTTP server for ``overseer app`` (§Q0.9)."""

from __future__ import annotations

import json
import mimetypes
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlparse

from cli.context import CliContext
from tools.app.auth import constant_time_equal, generate_csrf_token, generate_session_credential
from tools.app.bind import is_loopback_peer
from tools.app.cors import allowed_origins, origin_allowed
from tools.app.engine import (
    handle_docs_handover,
    handle_docs_roadmap,
    handle_gates,
    handle_governance_sync,
    handle_health,
    handle_honesty_status,
    handle_ledger_append,
    handle_ledger_show,
    handle_ledger_verify,
    handle_review_freeze,
    handle_status,
)
from tools.app.envelope import ApiEnvelope, auth_refusal

STATIC_ROOT = Path(__file__).resolve().parent / "static"
MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

RouteHandler = Callable[[BaseHTTPRequestHandler, dict | None], ApiEnvelope]


@dataclass(frozen=True)
class AppServerConfig:
    """Runtime configuration for the local app server."""

    repo_root: Path
    bind: str
    port: int
    session_credential: str
    csrf_token: str
    ctx: CliContext


class AppHTTPServer(ThreadingHTTPServer):
    """Threading HTTP server carrying frozen app configuration."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: AppServerConfig) -> None:
        self.app_config = config
        super().__init__((config.bind, config.port), AppRequestHandler)


class AppRequestHandler(BaseHTTPRequestHandler):
    """Serve static UI assets and the closed ``api/*`` surface."""

    server_version = "OverseerApp/1.0"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        if self.server.app_config.ctx.output.verbose:
            super().log_message(format, *args)

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch()

    def do_OPTIONS(self) -> None:  # noqa: N802
        if not self._peer_ok():
            self._send_auth_refusal(auth_refusal(http_status=403, error="peer"))
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self._write_cors_headers()
        self.end_headers()

    def _dispatch(self) -> None:
        config = self.server.app_config
        if not self._peer_ok():
            self._send_auth_refusal(auth_refusal(http_status=403, error="peer"))
            return

        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            if not self._auth_ok(require_csrf=self.command in MUTATING_METHODS):
                return
            if not self._origin_ok():
                self._send_auth_refusal(auth_refusal(http_status=403, error="origin"))
                return
            body = self._read_json_body() if self.command in MUTATING_METHODS else None
            if body is _READ_ERROR:
                return
            envelope = self._route_api(path, body, query=parse_qs(parsed.query))
            self._send_envelope(envelope)
            return

        if self.command != "GET":
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)
            return

        if path in {"/", "/index.html"}:
            self._serve_static(STATIC_ROOT / "index.html")
            return
        if path.startswith("/assets/"):
            rel = path.removeprefix("/assets/")
            self._serve_static(STATIC_ROOT / "assets" / rel)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def _route_api(self, path: str, body: dict | None, *, query: dict[str, list[str]]) -> ApiEnvelope:
        config = self.server.app_config
        ctx = config.ctx
        repo_arg = str(config.repo_root)

        routes: dict[tuple[str, str], RouteHandler] = {
            ("GET", "/api/health"): lambda _h, _b: handle_health(
                port=config.port,
                bind=config.bind,
                repo_root=config.repo_root,
            ),
            ("GET", "/api/status"): lambda _h, _b: handle_status(ctx, repo_arg=repo_arg),
            ("GET", "/api/gates"): lambda _h, _b: handle_gates(ctx, repo_arg=repo_arg),
            ("GET", "/api/docs/roadmap"): lambda _h, _b: handle_docs_roadmap(ctx, repo_arg=repo_arg),
            ("GET", "/api/docs/handover"): lambda _h, _b: handle_docs_handover(ctx, repo_arg=repo_arg),
            ("GET", "/api/ledger/show"): lambda _h, _b: handle_ledger_show(
                ctx,
                repo_arg=repo_arg,
                last=_parse_last_query(query),
            ),
            ("POST", "/api/review/freeze"): lambda _h, b: handle_review_freeze(ctx, b or {}, repo_arg=repo_arg),
            ("POST", "/api/governance-sync"): lambda _h, b: handle_governance_sync(ctx, b or {}, repo_arg=repo_arg),
            ("POST", "/api/ledger/verify"): lambda _h, b: handle_ledger_verify(ctx, b or {}, repo_arg=repo_arg),
            ("POST", "/api/ledger/append"): lambda _h, b: handle_ledger_append(ctx, b or {}, repo_arg=repo_arg),
            ("POST", "/api/honesty-status"): lambda _h, b: handle_honesty_status(ctx, b or {}, repo_arg=repo_arg),
        }

        handler = routes.get((self.command, path))
        if handler is None:
            return auth_refusal(http_status=404, error="not_found")
        return handler(self, body)

    def _peer_ok(self) -> bool:
        host = self.client_address[0]
        return is_loopback_peer(host)

    def _auth_ok(self, *, require_csrf: bool) -> bool:
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            self._send_auth_refusal(auth_refusal(http_status=401, error="auth"))
            return False
        token = auth_header.removeprefix("Bearer ").strip()
        if not constant_time_equal(token, self.server.app_config.session_credential):
            self._send_auth_refusal(auth_refusal(http_status=401, error="auth"))
            return False
        if require_csrf:
            csrf = self.headers.get("X-Overseer-CSRF", "")
            if not constant_time_equal(csrf, self.server.app_config.csrf_token):
                self._send_auth_refusal(auth_refusal(http_status=403, error="csrf"))
                return False
        return True

    def _origin_ok(self) -> bool:
        return origin_allowed(self.headers.get("Origin"), self.server.app_config.port)

    def _read_json_body(self) -> dict | None | object:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_envelope(auth_refusal(http_status=400, error="bad_json"))
            return _READ_ERROR
        if not isinstance(parsed, dict):
            self._send_envelope(auth_refusal(http_status=400, error="bad_json"))
            return _READ_ERROR
        return parsed

    def _send_envelope(self, envelope: ApiEnvelope) -> None:
        self.send_response(envelope.http_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = envelope.to_json_bytes()
        self.send_header("Content-Length", str(len(body)))
        self._write_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_auth_refusal(self, envelope: ApiEnvelope) -> None:
        self.send_response(envelope.http_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = envelope.to_json_bytes()
        self.send_header("Content-Length", str(len(body)))
        self._write_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _write_cors_headers(self) -> None:
        origin = self.headers.get("Origin")
        port = self.server.app_config.port
        if origin and origin in allowed_origins(port):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Overseer-CSRF")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _serve_static(self, path: Path) -> None:
        try:
            resolved = path.resolve()
            if not str(resolved).startswith(str(STATIC_ROOT.resolve())):
                self.send_error(HTTPStatus.FORBIDDEN)
                return
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if not resolved.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type, _ = mimetypes.guess_type(str(resolved))
        content = resolved.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self._write_cors_headers()
        self.end_headers()
        self.wfile.write(content)


_READ_ERROR = object()


def _parse_last_query(query: dict[str, list[str]]) -> int | None:
    values = query.get("last")
    if not values:
        return None
    try:
        parsed = int(values[0])
    except ValueError:
        return None
    return parsed if parsed > 0 else None


@dataclass
class AppServerHandle:
    """Running server handle for tests and CLI."""

    config: AppServerConfig
    httpd: AppHTTPServer
    thread: threading.Thread

    @property
    def base_url(self) -> str:
        host = "127.0.0.1" if self.config.bind in {"127.0.0.1", "localhost"} else "[::1]"
        return f"http://{host}:{self.config.port}"

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=5)


def start_app_server(config: AppServerConfig) -> AppServerHandle:
    """Bind and start the app server in a background thread."""
    httpd = AppHTTPServer(config)
    thread = threading.Thread(target=httpd.serve_forever, name="overseer-app", daemon=True)
    thread.start()
    return AppServerHandle(config=config, httpd=httpd, thread=thread)


def build_server_config(
    *,
    repo_root: Path,
    bind: str,
    port: int,
    ctx: CliContext,
    session_credential: str | None = None,
    csrf_token: str | None = None,
) -> AppServerConfig:
    """Construct server configuration with optional fixed credentials for tests."""
    return AppServerConfig(
        repo_root=repo_root.resolve(),
        bind=bind,
        port=port,
        session_credential=session_credential or generate_session_credential(),
        csrf_token=csrf_token or generate_csrf_token(),
        ctx=ctx,
    )


def run_app_server(
    *,
    repo_root: Path,
    bind: str,
    port: int,
    ctx: CliContext,
    on_ready: Callable[[AppServerConfig, str], None] | None = None,
) -> int:
    """Start the server and block until shutdown. Returns process exit code."""
    session = generate_session_credential()
    csrf = generate_csrf_token()
    config = build_server_config(
        repo_root=repo_root,
        bind=bind,
        port=port,
        ctx=ctx,
        session_credential=session,
        csrf_token=csrf,
    )
    if on_ready is not None:
        on_ready(config, f"{config.bind}:{config.port}")
    handle = start_app_server(config)
    try:
        handle.thread.join()
    except KeyboardInterrupt:
        handle.shutdown()
    return 0

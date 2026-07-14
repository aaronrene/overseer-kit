"""Stdlib HTTP read-only server for hosted governance dashboard (§HGD.5, §HGD.10)."""

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

from tools.hosted_dashboard.auth import constant_time_equal
from tools.hosted_dashboard.bind import is_loopback_peer
from tools.hosted_dashboard.config import HostedDashboardConfig
from tools.hosted_dashboard.cors import origin_allowed
from tools.hosted_dashboard.envelope import ApiEnvelope, failure
from tools.hosted_dashboard.handlers import DashboardService, is_track_q_act_path, match_repo_route

STATIC_ROOT = Path(__file__).resolve().parent / "static"
MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
ALLOWED_API_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class HostedServerConfig:
    """Runtime configuration for the hosted dashboard server."""

    bind: str
    port: int
    viewer_token: str
    upstream_token: str | None
    dashboard: HostedDashboardConfig
    service: DashboardService
    require_loopback_peer: bool = True
    write_scope_refused: bool = False


class HostedHTTPServer(ThreadingHTTPServer):
    """Threading HTTP server carrying hosted dashboard configuration."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: HostedServerConfig) -> None:
        self.hosted_config = config
        super().__init__((config.bind, config.port), HostedRequestHandler)


class HostedRequestHandler(BaseHTTPRequestHandler):
    """Serve static UI and closed GET-only ``api/*`` surface."""

    server_version = "OverseerHostedDashboard/1.0"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_HEAD(self) -> None:  # noqa: N802
        self._dispatch(head_only=True)

    def do_POST(self) -> None:  # noqa: N802
        self._reject_mutating()

    def do_PUT(self) -> None:  # noqa: N802
        self._reject_mutating()

    def do_PATCH(self) -> None:  # noqa: N802
        self._reject_mutating()

    def do_DELETE(self) -> None:  # noqa: N802
        self._reject_mutating()

    def do_OPTIONS(self) -> None:  # noqa: N802
        if not self._peer_ok():
            self._send_envelope(failure(error="peer", http_status=403))
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self._write_cors_headers()
        self.end_headers()

    def _reject_mutating(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._send_envelope(failure(error="method_not_allowed", http_status=405))
            return
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

    def _dispatch(self, *, head_only: bool = False) -> None:
        config = self.server.hosted_config
        if not self._peer_ok():
            self._send_envelope(failure(error="peer", http_status=403))
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.startswith("/api/"):
            if not self._origin_ok():
                self._send_envelope(failure(error="origin", http_status=403))
                return
            if path != "/api/health" and not self._viewer_auth_ok():
                return
            if config.write_scope_refused and path != "/api/health":
                self._send_envelope(failure(error="write_scope_refused", http_status=403))
                return
            envelope = self._route_api(path, query)
            self._send_envelope(envelope, head_only=head_only)
            return

        if self.command not in {"GET", "HEAD"}:
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)
            return

        if path in {"/", "/index.html"}:
            self._serve_static(STATIC_ROOT / "index.html", head_only=head_only)
            return
        if path.startswith("/assets/"):
            rel = path.removeprefix("/assets/")
            self._serve_static(STATIC_ROOT / "assets" / rel, head_only=head_only)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def _route_api(self, path: str, query: dict[str, list[str]]) -> ApiEnvelope:
        if is_track_q_act_path(path):
            return failure(error="not_found", http_status=404)

        service = self.server.hosted_config.service
        if path == "/api/health":
            return service.health()
        if path == "/api/org/summary":
            return service.org_summary(query)

        matched = match_repo_route(path)
        if matched is not None:
            owner, repo, action = matched
            if action == "roadmap":
                return service.roadmap(owner, repo, query)
            if action == "handover":
                return service.handover(owner, repo, query)
            if action == "gates":
                return service.gates(owner, repo, query)
            if action == "config-marker":
                return service.config_marker(owner, repo, query)

        return failure(error="not_found", http_status=404)

    def _peer_ok(self) -> bool:
        config = self.server.hosted_config
        if not config.require_loopback_peer:
            return True
        return is_loopback_peer(self.client_address[0])

    def _viewer_auth_ok(self) -> bool:
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            self._send_envelope(failure(error="auth", http_status=401))
            return False
        token = auth_header.removeprefix("Bearer ").strip()
        if not constant_time_equal(token, self.server.hosted_config.viewer_token):
            self._send_envelope(failure(error="auth", http_status=401))
            return False
        return True

    def _origin_ok(self) -> bool:
        return origin_allowed(
            self.headers.get("Origin"),
            self.server.hosted_config.dashboard.cors_origins,
        )

    def _send_envelope(self, envelope: ApiEnvelope, *, head_only: bool = False) -> None:
        self.send_response(envelope.http_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = envelope.to_json_bytes()
        self.send_header("Content-Length", str(len(body)))
        self._write_cors_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _write_cors_headers(self) -> None:
        origin = self.headers.get("Origin")
        allowed = self.server.hosted_config.dashboard.cors_origins
        if origin and origin in allowed:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")

    def _serve_static(self, path: Path, *, head_only: bool = False) -> None:
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
        self.end_headers()
        if not head_only:
            self.wfile.write(content)


@dataclass
class HostedServerHandle:
    """Running server handle for tests and CLI."""

    config: HostedServerConfig
    httpd: HostedHTTPServer
    thread: threading.Thread

    @property
    def base_url(self) -> str:
        host = "127.0.0.1" if self.config.bind in {"127.0.0.1", "localhost"} else self.config.bind
        if host == "::1":
            host = "[::1]"
        return f"http://{host}:{self.config.port}"

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=5)


def start_hosted_server(config: HostedServerConfig) -> HostedServerHandle:
    """Bind and start the hosted dashboard server in a background thread."""
    httpd = HostedHTTPServer(config)
    thread = threading.Thread(target=httpd.serve_forever, name="overseer-hosted-dashboard", daemon=True)
    thread.start()
    return HostedServerHandle(config=config, httpd=httpd, thread=thread)


def run_hosted_server(
    config: HostedServerConfig,
    *,
    on_ready: Callable[[HostedServerConfig, str], None] | None = None,
) -> int:
    """Start the server and block until shutdown. Returns process exit code ``0``."""
    if on_ready is not None:
        on_ready(config, f"{config.bind}:{config.port}")
    handle = start_hosted_server(config)
    try:
        handle.thread.join()
    except KeyboardInterrupt:
        handle.shutdown()
    return 0

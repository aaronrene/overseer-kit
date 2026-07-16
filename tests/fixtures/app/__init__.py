"""Fixture helpers for Track Q / Q1 app tests."""

from __future__ import annotations

import json
import shutil
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from cli.context import CliContext
from cli.kit_root import kit_root
from cli.output import OutputContext
from tests.support import FIXTURES, HONESTY, git_status_runner, run_cli, seed_freeze_repo
from tools.app.server import AppServerHandle, build_server_config, start_app_server


def free_port() -> int:
    """Return an ephemeral loopback port for tests."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def seed_app_repo(tmp_path: Path, *, config_name: str = "config-git-only.yaml") -> None:
    """Initialize a minimal repo suitable for app handler tests."""
    code = run_cli(
        ["init", "--from-config", str(FIXTURES / config_name), "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=git_status_runner(),
    )
    assert code == 0
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "ROADMAP.md").write_text("# Roadmap fixture\n", encoding="utf-8")
    (docs / "OVERSEER-HANDOVER.md").write_text("# Handover fixture\n", encoding="utf-8")


def seed_app_e2e_repo(tmp_path: Path) -> Path:
    """Seed a repo with freeze review + honesty modules enabled for e2e flows."""
    artifact = seed_freeze_repo(tmp_path)
    for rel in ("artifacts", "entries"):
        src = HONESTY / rel
        dest = tmp_path / rel
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    config_path = tmp_path / ".overseer" / "config.yaml"
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    honesty_cfg = yaml.safe_load((HONESTY / "config-honesty-enabled.yaml").read_text(encoding="utf-8"))
    cfg["honesty"] = honesty_cfg["honesty"]
    cfg["modules"] = honesty_cfg["modules"]
    config_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return artifact


class AppHttpClient:
    """Minimal HTTP client for the local app server."""

    def __init__(self, base_url: str, session: str, csrf: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.csrf = csrf

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        origin: str | None = None,
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}{path}"
        req_headers = dict(headers or {})
        if origin is not None:
            req_headers["Origin"] = origin
        data = None
        if body is not None:
            req_headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return response.status, payload
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            return exc.code, payload

    def get(self, path: str, **kwargs: Any) -> tuple[int, dict[str, Any]]:
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {self.session}")
        return self.request("GET", path, headers=headers, **kwargs)

    def post(self, path: str, body: dict[str, Any] | None = None, **kwargs: Any) -> tuple[int, dict[str, Any]]:
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {self.session}")
        headers.setdefault("X-Overseer-CSRF", self.csrf)
        return self.request("POST", path, body=body or {}, headers=headers, **kwargs)


def start_test_app(
    repo_root: Path,
    *,
    port: int | None = None,
    runner=None,
    review_provider_factory=None,
) -> tuple[AppServerHandle, AppHttpClient]:
    """Start an app server against ``repo_root`` and return handle + client."""
    chosen = port or free_port()
    ctx = CliContext.create(
        cwd=repo_root,
        kit=kit_root(),
        runner=runner or git_status_runner(),
        output=OutputContext(),
        review_provider_factory=review_provider_factory,
    )
    config = build_server_config(
        repo_root=repo_root,
        bind="127.0.0.1",
        port=chosen,
        ctx=ctx,
        session_credential="test-session-credential",
        csrf_token="test-csrf-token",
    )
    handle = start_app_server(config)
    client = AppHttpClient(handle.base_url, config.session_credential, config.csrf_token)
    return handle, client

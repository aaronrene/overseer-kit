"""``ok hosted-dashboard`` command (§HGD.10.1)."""

from __future__ import annotations

import os
import sys
import webbrowser
from argparse import Namespace
from pathlib import Path

import yaml

from cli.context import CliContext
from cli.paths import PathEscapeError, resolve_repo_root
from tools.hosted_dashboard.adapters.github import GitHubAdapters
from tools.hosted_dashboard.auth import generate_viewer_token
from tools.hosted_dashboard.bind import DEFAULT_PORT, port_is_available, validate_bind_address
from tools.hosted_dashboard.config import (
    HostedDashboardConfigError,
    default_hosted_dashboard_config,
    parse_hosted_dashboard_config,
)
from tools.hosted_dashboard.handlers import DashboardService
from tools.hosted_dashboard.http_client import UpstreamClient
from tools.hosted_dashboard.scopes import refuse_write_scopes
from tools.hosted_dashboard.server import HostedServerConfig, run_hosted_server

VIEWER_TOKEN_ENV = "OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN"
UPSTREAM_TOKEN_ENV = "OVERSEER_HOSTED_DASHBOARD_TOKEN"
# Documented synonym
UPSTREAM_TOKEN_SYNONYM = "OVERSEER_HOSTED_DASHBOARD_GITHUB_TOKEN"


def _load_dashboard_config(config_path: Path | None) -> tuple[object, Path | None]:
    if config_path is None:
        return default_hosted_dashboard_config(), None
    if not config_path.is_file():
        raise HostedDashboardConfigError(f"config file missing: {config_path}")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise HostedDashboardConfigError("config root must be a mapping")
    return parse_hosted_dashboard_config(raw.get("hosted_dashboard"), path=str(config_path)), config_path


def _resolve_config_path(args: Namespace, ctx: CliContext) -> Path | None:
    if getattr(args, "config", None):
        return Path(args.config).expanduser().resolve()
    # Prefer cwd .overseer/config.yaml when present.
    candidate = (ctx.cwd / ".overseer" / "config.yaml").resolve()
    if candidate.is_file():
        return candidate
    # Also try --repo root if provided.
    if getattr(args, "repo", None):
        try:
            repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="hosted-dashboard")
        except PathEscapeError:
            return None
        alt = repo_root / ".overseer" / "config.yaml"
        if alt.is_file():
            return alt.resolve()
    return None


def _print_startup_banner(bind: str, port: int, viewer_token: str, *, ephemeral: bool) -> None:
    host = "127.0.0.1" if bind in {"127.0.0.1", "localhost"} else bind
    if host == "::1":
        host = "[::1]"
    url = f"http://{host}:{port}/"
    print("ok hosted-dashboard listening", file=sys.stderr)
    print(f"url: {url}", file=sys.stderr)
    print(f"mode: hosted-read-only", file=sys.stderr)
    label = "viewer_token (ephemeral — copy once)" if ephemeral else "viewer_token"
    print(f"{label}: {viewer_token}", file=sys.stderr)


def run_hosted_dashboard(args: Namespace, ctx: CliContext) -> int:
    """Start the hosted governance dashboard preview server."""
    port = int(args.port) if args.port is not None else DEFAULT_PORT
    if port < 1 or port > 65535:
        ctx.output.error("refused: port must be between 1 and 65535")
        return 1

    try:
        config_path = _resolve_config_path(args, ctx)
        dashboard, _ = _load_dashboard_config(config_path)
    except HostedDashboardConfigError as exc:
        ctx.output.error(f"refused: {exc}")
        return 2

    bind = validate_bind_address(args.bind, allow_non_loopback=dashboard.allow_non_loopback)
    if bind is None:
        ctx.output.error(
            "refused: non-loopback bind requires hosted_dashboard.allow_non_loopback: true"
        )
        return 2

    if not port_is_available(bind, port):
        ctx.output.error(f"refused: port {port} is already in use")
        return 2

    # Optional introspection of write scopes via env JSON list (operator/tests).
    scopes_env = os.environ.get("OVERSEER_HOSTED_DASHBOARD_SCOPES")
    advertised_scopes = None
    if scopes_env:
        advertised_scopes = [s.strip() for s in scopes_env.split(",") if s.strip()]
    write_refused = refuse_write_scopes(advertised_scopes) is not None
    if write_refused and os.environ.get("OVERSEER_HOSTED_DASHBOARD_REFUSE_ON_WRITE_SCOPE", "1") == "1":
        ctx.output.error("refused: write_scope_refused")
        return 2

    upstream = os.environ.get(UPSTREAM_TOKEN_ENV) or os.environ.get(UPSTREAM_TOKEN_SYNONYM)
    viewer = os.environ.get(VIEWER_TOKEN_ENV)
    ephemeral = False
    if not viewer:
        viewer = generate_viewer_token()
        ephemeral = True

    client = UpstreamClient(
        token=upstream,
        extra_allowed_hosts=dashboard.musehub_hosts,
    )
    adapters = GitHubAdapters(
        client,
        checks_advisory=dashboard.sources.github_checks_advisory,
        enumeration_cap=dashboard.enumeration_cap,
        max_doc_bytes=dashboard.max_doc_bytes,
    )
    service = DashboardService(adapters, dashboard)
    server_config = HostedServerConfig(
        bind=bind,
        port=port,
        viewer_token=viewer,
        upstream_token=upstream,
        dashboard=dashboard,
        service=service,
        require_loopback_peer=bind in {"127.0.0.1", "localhost", "::1"},
        write_scope_refused=write_refused,
    )

    open_browser = bool(args.open)

    def on_ready(config: HostedServerConfig, _addr: str) -> None:
        _print_startup_banner(config.bind, config.port, config.viewer_token, ephemeral=ephemeral)
        if open_browser:
            host = "127.0.0.1" if config.bind in {"127.0.0.1", "localhost"} else config.bind
            if host == "::1":
                host = "[::1]"
            webbrowser.open(f"http://{host}:{config.port}/")

    return run_hosted_server(server_config, on_ready=on_ready)

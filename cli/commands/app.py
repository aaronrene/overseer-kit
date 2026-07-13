"""``overseer app`` command (§Q0.4)."""

from __future__ import annotations

import sys
import webbrowser
from argparse import Namespace
from pathlib import Path

from cli.context import CliContext
from cli.paths import PathEscapeError, resolve_repo_root
from tools.app.bind import DEFAULT_PORT, port_is_available, validate_bind_address
from tools.app.server import run_app_server


def _print_startup_banner(config_bind: str, port: int, session: str, csrf: str) -> None:
    host = "127.0.0.1" if config_bind in {"127.0.0.1", "localhost"} else "[::1]"
    url = f"http://{host}:{port}/"
    print("ok app listening", file=sys.stderr)
    print(f"url: {url}", file=sys.stderr)
    print(f"session_credential: {session}", file=sys.stderr)
    print(f"csrf_token: {csrf}", file=sys.stderr)


def run_app(args: Namespace, ctx: CliContext) -> int:
    """Start the local loopback web UI."""
    try:
        repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="app")
    except PathEscapeError:
        ctx.output.error("refused: repo path outside allowed root")
        return 4

    if not (repo_root / ".overseer").is_dir():
        ctx.output.error("not initialized — run ok init first")
        return 2

    bind = validate_bind_address(args.bind)
    if bind is None:
        ctx.output.error("refused: bind address must be loopback (127.0.0.1, localhost, or ::1)")
        return 2

    port = int(args.port)
    if port < 1 or port > 65535:
        ctx.output.error("refused: port must be between 1 and 65535")
        return 2

    if not port_is_available(bind, port):
        ctx.output.error(f"refused: port {port} is already in use")
        return 2

    open_browser = bool(args.open)
    captured: dict[str, str] = {}

    def on_ready(config, _addr: str) -> None:
        captured["session"] = config.session_credential
        captured["csrf"] = config.csrf_token
        _print_startup_banner(bind, port, config.session_credential, config.csrf_token)
        if open_browser:
            host = "127.0.0.1" if bind in {"127.0.0.1", "localhost"} else "[::1]"
            webbrowser.open(f"http://{host}:{port}/")

    return run_app_server(repo_root=repo_root, bind=bind, port=port, ctx=ctx, on_ready=on_ready)

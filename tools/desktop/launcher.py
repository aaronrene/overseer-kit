"""Desktop launcher that invokes the canonical ``ok app`` entrypoint."""

from __future__ import annotations

import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from cli.kit_root import kit_root
from tools.app.bind import DEFAULT_PORT
from tools.desktop.banner import StartupBanner, parse_startup_stderr
from tools.desktop.constants import (
    CANONICAL_LAUNCHER,
    CANONICAL_SUBCOMMAND,
    DEFAULT_BIND,
    KIT_ROOT_ENV,
    REPO_ROOT_ENV,
    STARTUP_TIMEOUT_SECONDS,
)


def resolve_kit_root(explicit: Path | None = None) -> Path:
    """Resolve the kit checkout root for dev or bundled desktop runs."""
    if explicit is not None:
        return explicit.resolve()
    env = os.environ.get(KIT_ROOT_ENV)
    if env:
        return Path(env).resolve()
    return kit_root()


def resolve_repo_root(*, kit: Path, explicit: Path | None = None, cwd: Path | None = None) -> Path:
    """Resolve the governance repo root the desktop shell should bind."""
    if explicit is not None:
        return explicit.resolve()
    env = os.environ.get(REPO_ROOT_ENV)
    if env:
        return Path(env).resolve()
    if cwd is not None:
        return cwd.resolve()
    return kit.resolve()


def build_launch_argv(
    *,
    kit_root_path: Path,
    repo_root: Path,
    port: int = DEFAULT_PORT,
    bind: str = DEFAULT_BIND,
) -> list[str]:
    """Build argv for the canonical POSIX shim → ``ok app`` (§Q2a / §Q0.13)."""
    ok_shim = kit_root_path / "cli" / CANONICAL_LAUNCHER
    if not ok_shim.is_file():
        raise FileNotFoundError(f"missing canonical launcher: {ok_shim}")
    return [
        str(ok_shim),
        CANONICAL_SUBCOMMAND,
        "--repo",
        str(repo_root),
        "--port",
        str(port),
        "--bind",
        bind,
    ]


@dataclass
class DesktopLauncher:
    """Spawn ``ok app`` and capture the one-time startup banner."""

    kit_root_path: Path
    repo_root: Path
    port: int = DEFAULT_PORT
    bind: str = DEFAULT_BIND
    timeout_seconds: float = STARTUP_TIMEOUT_SECONDS

    _process: subprocess.Popen[str] | None = None
    _stderr_lines: list[str] = None  # type: ignore[assignment]
    _stderr_thread: threading.Thread | None = None

    def __post_init__(self) -> None:
        self.kit_root_path = self.kit_root_path.resolve()
        self.repo_root = self.repo_root.resolve()
        self._stderr_lines = []

    @property
    def argv(self) -> list[str]:
        return build_launch_argv(
            kit_root_path=self.kit_root_path,
            repo_root=self.repo_root,
            port=self.port,
            bind=self.bind,
        )

    def start(self) -> StartupBanner:
        """Start ``ok app`` and block until the startup banner is complete."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.kit_root_path) + (
            f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else ""
        )
        self._process = subprocess.Popen(
            self.argv,
            cwd=self.kit_root_path,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert self._process.stderr is not None

        def _reader() -> None:
            for line in self._process.stderr:  # type: ignore[union-attr]
                self._stderr_lines.append(line)

        self._stderr_thread = threading.Thread(target=_reader, name="ok-app-stderr", daemon=True)
        self._stderr_thread.start()

        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            banner = parse_startup_stderr(self._stderr_lines)
            if banner is not None:
                self._wait_until_healthy(banner)
                return banner
            if self._process.poll() is not None:
                break
            time.sleep(0.05)

        code = self._process.poll()
        tail = "".join(self._stderr_lines[-20:])
        raise RuntimeError(f"ok app failed to start (exit={code}): {tail}")

    def stop(self) -> None:
        """Terminate the background ``ok app`` process."""
        if self._process is None:
            return
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=5)
        if self._stderr_thread is not None:
            self._stderr_thread.join(timeout=2)
        self._process = None

    def _wait_until_healthy(self, banner: StartupBanner) -> None:
        health_url = banner.url.rstrip("/") + "/api/health"
        request = urllib.request.Request(
            health_url,
            headers={"Authorization": f"Bearer {banner.session_credential}"},
        )
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(request, timeout=1) as response:
                    if response.status == 200:
                        return
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.05)
        raise RuntimeError(f"health check timed out for {health_url}")

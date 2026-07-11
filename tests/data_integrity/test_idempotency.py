"""Data-integrity tests for idempotency and atomic writes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cli.digest import FootprintRecord, compute_footprint_digest, sha256_hex
from cli.footprint import resolve_footprint
from cli.kit_root import kit_root
from cli.version_lock import read_version_lock
from tests.support import load_fixture_config, run_cli


def test_init_twice_identical_lock(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    lock1 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    lock2 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock1.installed_at == lock2.installed_at
    assert lock1.footprint_digest == lock2.footprint_digest


def test_footprint_digest_matches_reference(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    from adapters.config import load_config

    config = load_config(tmp_path / ".overseer" / "config.yaml")
    rendered = resolve_footprint(config, kit=kit_root())
    records = []
    for item in rendered:
        on_disk = (tmp_path / item.destination).read_bytes()
        records.append(FootprintRecord(item.destination, sha256_hex(on_disk)))
    expected = compute_footprint_digest(records)
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock.footprint_digest == expected


def test_write_failure_leaves_lock_unchanged(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    before = read_version_lock(tmp_path / ".overseer" / "version.lock")
    calls = {"n": 0}

    def flaky_write(path: Path, data: bytes, *, destination: str) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            from cli.atomic import WriteFailure

            raise WriteFailure(path, OSError("simulated failure"))
        from cli.footprint_writes import write_footprint_bytes as real

        real(path, data, destination=destination)

    with patch("cli.commands.init.write_footprint_bytes", side_effect=flaky_write):
        code = run_cli(
            ["init", "--regime", "git-only", "--non-interactive", "--force"],
            cwd=tmp_path,
        )
    assert code == 5
    after = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert after.footprint_digest == before.footprint_digest


def test_dry_run_writes_zero_bytes(tmp_path: Path) -> None:
    before = set(tmp_path.rglob("*"))
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive", "--dry-run"],
        cwd=tmp_path,
    )
    after = set(tmp_path.rglob("*"))
    assert before == after

"""Unit tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries
from tools.footprint_coverage import check_footprint_coverage
from tools.handover_compact import compact_handover_change_log
from tools.optional_feature_tips import build_optional_feature_tips
from tools.verification_evidence_gate import build_verification_evidence_gate
from tests.support import FIXTURES, KIT_ROOT, load_fixture_config, write_config


def _lock(entries: list[FootprintEntry]):
    return build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )


def test_coverage_empty_lock_not_applicable(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_footprint_coverage(tmp_path, config, lock=_lock([]), rendered=[])
    assert report.ok
    assert report.state == "not_applicable"


def test_coverage_missing_from_lock(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    from cli.footprint import resolve_footprint

    files = resolve_footprint(config, kit=KIT_ROOT)
    lock = _lock(
        [
            FootprintEntry(
                path=files[0].destination,
                source=files[0].source,
                sha256="0" * 64,
                origin=ORIGIN_KIT,
            )
        ]
    )
    report = check_footprint_coverage(tmp_path, config, lock=lock, rendered=files, kit=KIT_ROOT)
    assert not report.ok
    assert report.state == "missing_from_lock"
    assert report.remediation == "ok sync"
    assert len(report.missing) == len(files) - 1


def test_coverage_all_dests_ok(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    from cli.footprint import resolve_footprint

    files = resolve_footprint(config, kit=KIT_ROOT)
    entries = [
        FootprintEntry(path=f.destination, source=f.source, sha256="0" * 64, origin=ORIGIN_KIT)
        for f in files
    ]
    report = check_footprint_coverage(
        tmp_path, config, lock=_lock(entries), rendered=files, kit=KIT_ROOT
    )
    assert report.ok
    assert report.state == "ok"


def test_session_bookends_default_off(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    assert config.session_bookends.enabled is False


def test_session_bookends_unknown_key(tmp_path: Path) -> None:
    dest = tmp_path / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = (FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8")
    dest.write_text(text + "\nsession_bookends:\n  enabled: false\n  extra: true\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown session_bookends"):
        load_config(dest)


def test_session_bookends_enabled_non_bool(tmp_path: Path) -> None:
    dest = tmp_path / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = (FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8")
    dest.write_text(text + "\nsession_bookends:\n  enabled: not-a-bool\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="must be a boolean"):
        load_config(dest)


def test_compact_keep_too_low(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    write_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    handover.write_text(
        "<!-- overseer:anchor:change-log -->\n"
        "- **2026-01-01** — one\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    from cli.main import main
    from cli.context import CliContext
    from cli.output import OutputContext
    from tests.support import make_runner

    ctx = CliContext.create(
        runner=make_runner({}),
        cwd=tmp_path,
        kit=KIT_ROOT,
        output=OutputContext(json_mode=False),
    )
    import os

    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        code = main(["handover-compact", "--keep", "4"], ctx=ctx)
    finally:
        os.chdir(old)
    assert code == 2


def test_compact_missing_anchor(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    handover.write_text("# no anchor\n", encoding="utf-8")
    report = compact_handover_change_log(config, tmp_path, keep=15, write=False)
    assert not report.ok
    assert report.reason == "change_log_anchor_missing"


def test_compact_no_op_when_within_keep(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    handover.write_text(
        "<!-- overseer:anchor:change-log -->\n"
        "- **2026-01-01** — one\n"
        "- **2026-01-02** — two\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    report = compact_handover_change_log(config, tmp_path, keep=15, write=False)
    assert report.ok
    assert report.compacted == 0


def test_verification_gate_skips_when_honesty_off(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = build_verification_evidence_gate(config, tmp_path)
    assert report.skipped
    assert report.ok


def test_verification_gate_skips_active_auto_todo(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    config_path = tmp_path / ".overseer" / "config.yaml"
    text = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        text
        + "\nhonesty:\n  enabled: true\n  ledger: .overseer/honesty/VERDICT-LEDGER.jsonl\n"
        + "  require_verification_evidence: warn\n",
        encoding="utf-8",
    )
    config = load_config(config_path)
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "ROADMAP.md").write_text(
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        "| **LT-b Loop tightening build** | Auto | **TODO** | build |\n",
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "## NEXT SESSION — LT-b\n\n| | |\n| **ID** | **LT-b** |\n",
        encoding="utf-8",
    )
    report = build_verification_evidence_gate(config, tmp_path)
    assert report.skipped


def test_optional_feature_tips_default_off(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    tips = build_optional_feature_tips(config)
    assert len(tips) == 2
    assert any("session_bookends off" in tip for tip in tips)
    assert any("honesty off" in tip for tip in tips)


def test_optional_feature_tips_empty_when_enabled(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    config_path = tmp_path / ".overseer" / "config.yaml"
    text = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        text
        + "\nsession_bookends:\n  enabled: true\n"
        + "honesty:\n  enabled: true\n  ledger: .overseer/honesty/VERDICT-LEDGER.jsonl\n"
        + "  require_independent_second_reviewer: warn\n",
        encoding="utf-8",
    )
    config = load_config(config_path)
    assert build_optional_feature_tips(config) == []

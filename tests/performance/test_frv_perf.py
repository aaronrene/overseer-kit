"""Performance tests for FRV (§FRV.12)."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.config import load_config
from tests.support import write_config
from tools.freeze_authorization.resolve import freeze_authorization_state


def test_authorization_state_bounded(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir()
    art = docs / "PHASE-FRV.md"
    art.write_text(
        "```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    start = time.perf_counter()
    for _ in range(20):
        freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config)
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0

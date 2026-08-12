"""Stress — large handover with fence at end (§ONS.12)."""

from __future__ import annotations

import time
from pathlib import Path

from tools.print_next.extract import CurrentNextResult, extract_current_next

MARKER = "STRESS-FENCE-BODY-UNIQUE-TOKEN"
PERF_BOUND_S = 2.0


def test_stress_large_handover_fence_at_end(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    path = docs / "OVERSEER-HANDOVER.md"
    done_rows = "\n".join(f"| **DONE-{i}** | Auto | **DONE** | filler |" for i in range(200))
    filler = ("x" * 1024 + "\n") * (1550)  # ≥1.5 MiB of padding before fence
    body = (
        f"# Handover\n\n## Queue\n\n{done_rows}\n\n{filler}\n"
        f"### Paste-ready prompt — stress\n\n```text\n{MARKER}\nModel: Auto\n```\n"
    )
    path.write_text(body, encoding="utf-8")
    assert path.stat().st_size >= int(1.5 * 1024 * 1024)

    start = time.perf_counter()
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    elapsed = time.perf_counter() - start
    assert isinstance(result, CurrentNextResult)
    assert MARKER in result.fence
    assert "Model: Auto" in result.fence
    assert elapsed < PERF_BOUND_S

"""Performance tests for workspace check-next (§MR.10 performance)."""

from __future__ import annotations

import time
from pathlib import Path

from tools.workspace.check_next import check_next
from tools.workspace.manifest import load_manifest_file
from tests.fixtures.workspace import build_two_repo_constellation


def test_check_next_five_member_under_two_seconds(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, with_musehub=True, with_brain=True)
    # Add two more optional absent members via manifest edit
    import yaml

    data = yaml.safe_load(fx["manifest"].read_text(encoding="utf-8"))
    data["members"].extend(
        [
            {
                "id": "edge2",
                "role": "edge",
                "root": "${EDGE2_ROOT}",
                "regime": None,
                "required": False,
                "relay": False,
            },
            {
                "id": "kit",
                "role": "kit",
                "root": "${KIT_ROOT}",
                "regime": None,
                "required": False,
                "relay": False,
            },
        ]
    )
    fx["manifest"].write_text(yaml.safe_dump(data), encoding="utf-8")
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    start = time.perf_counter()
    result = check_next(manifest)
    elapsed = time.perf_counter() - start
    assert result.exit_code == 0
    assert elapsed < 2.0

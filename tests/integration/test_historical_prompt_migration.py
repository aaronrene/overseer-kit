"""BornFree-sized history remains evidence until a separate accepted write."""
import json

import yaml

from cli import product_migration as migration
from cli.v1_io import digest
from tests.integration.test_legacy_migration_compat import (
    legacy, command, plan, apply, publish, healthy, snapshot)


def histories(root):
    expected = []
    for index, (path, size) in enumerate((
            ("docs/FIXTURE-ROADMAP.md", 768_855),
            ("docs/FIXTURE-HANDOVER.md", 831_973))):
        blocks = []
        for number in range(index * 69, (index + 1) * 69):
            # Large enough that the review plan also exceeds the config bound.
            prompt = f"Model: historical label\nHistorical task {number % 71}.\n" + "Evidence only. " * 100 + "\n"
            expected.append(prompt)
            blocks.append("### Paste-ready prompt — historical\n\n```text\n" + prompt + "```\n")
        body = ("# Preserved history\r\n" + "".join(blocks)).encode()
        body += b"\n" + b"x" * (size - len(body) - 1)
        assert len(body) == size
        (root / path).write_bytes(body)
    return expected


def test_many_historical_prompts_large_documents_and_separate_next_write(legacy):
    expected = histories(legacy)
    policy = legacy / ".overseer/policy/owner.yaml"
    policy.parent.mkdir(parents=True)
    policy.write_bytes(b"# owner policy\nrelease: blocked\n")
    policy.chmod(0o600)
    original = snapshot(legacy)
    config_before = (legacy / migration.CONFIG).read_bytes()
    lock_before = yaml.safe_load((legacy / migration.LOCK).read_bytes())
    document = plan(legacy)
    proposed = document["plan"]
    drafts = proposed["legacy_prompt_drafts"]
    assert len(drafts) == 138 and len({row["sha256"] for row in drafts}) == 71
    assert sorted(row["text"] for row in drafts) == sorted(expected)
    assert all(row["sha256"] == digest(row["text"].encode()) for row in drafts)
    assert any("138 blocks / 71 distinct; none selected or activated" in d for d in proposed["diagnostics"])
    assert len(json.dumps(document)) > 131_072
    protected = {"docs/FIXTURE-ROADMAP.md", "docs/FIXTURE-HANDOVER.md",
                 "docs/FIXTURE-COORDINATION.md", ".overseer/policy/owner.yaml",
                 ".overseer/honesty/VERDICT-LEDGER.jsonl"}
    assert not protected & {row["path"] for row in proposed["assets"]}
    after_preview = snapshot(legacy)
    after_preview.pop(".overseer/local/plan.json")
    assert after_preview == original
    result = apply(legacy, document)
    assert result.returncode == 0, result.stderr + result.stdout
    migrated = yaml.safe_load((legacy / migration.CONFIG).read_bytes())
    assert migrated == proposed["normalized_config"]
    for name in ("vcs", "thresholds", "freeze_contract", "honesty", "session_bookends"):
        assert migrated[name] == yaml.safe_load(config_before)[name]
    lock = yaml.safe_load((legacy / migration.LOCK).read_bytes())
    assert {row["path"] for row in lock["footprint"]} >= {row["path"] for row in lock_before["footprint"]}
    assert all(snapshot(legacy)[path] == original[path] for path in protected)
    assert not (legacy / migration.NEXT).exists()
    refused = command(legacy, "next", "--json")
    assert refused.returncode == 2 and not refused.stdout
    # An operator-supplied new prompt is the only publication source.
    publish(legacy)
    state = healthy(legacy)
    assert state["footprint_integrity"]["ok"] and state["footprint_coverage"]["ok"]
    next_text = command(legacy, "next").stdout
    assert "Historical task" not in next_text
    assert all(snapshot(legacy)[path] == original[path] for path in protected)


def test_historical_document_changed_after_preview_refuses_without_writes(legacy):
    histories(legacy)
    document = plan(legacy)
    with (legacy / "docs/FIXTURE-ROADMAP.md").open("ab") as stream:
        stream.write(b"\nOwner work after preview.\n")
    before = snapshot(legacy)
    result = apply(legacy, document)
    assert result.returncode == 2
    assert snapshot(legacy) == before
    assert not (legacy / migration.NEXT).exists()


def test_existing_next_is_not_replaced_by_history(legacy):
    assert apply(legacy, plan(legacy)).returncode == 0
    publish(legacy)
    saved = (legacy / migration.NEXT).read_bytes()
    histories(legacy)
    document = plan(legacy)
    assert len(document["plan"]["legacy_prompt_drafts"]) == 138
    assert apply(legacy, document).returncode == 0
    assert (legacy / migration.NEXT).read_bytes() == saved

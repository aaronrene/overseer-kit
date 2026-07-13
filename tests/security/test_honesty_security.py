"""Security tests for honesty module path discipline."""

from __future__ import annotations

import json

from tests.support import load_honesty_config, load_honesty_entry, run_cli, seed_honesty_repo
from cli.kit_root import kit_root
from tests.support import git_status_runner
from tools.honesty.ledger import show_entries
from tools.honesty.status import HonestyStatusOptions, run_honesty_status


def test_path_escape_artifact_refused(repo_root) -> None:
    config = load_honesty_config(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="../outside.txt"),
    )
    assert result.exit_code == 4


def test_path_escape_append_file_refused(repo_root) -> None:
    config = load_honesty_config(repo_root)
    outside = repo_root.parent / "escaped.json"
    outside.write_text("{}", encoding="utf-8")
    from tools.honesty.ledger import parse_append_body

    body, code, _ = parse_append_body(
        repo_root=repo_root,
        file_path=str(outside),
        stdin_text=None,
    )
    assert code == 4


def test_roles_file_content_cannot_inject_roles(repo_root) -> None:
    config = load_honesty_config(repo_root)
    roles = repo_root / "roles.yaml"
    roles.write_text("roles:\n  hacker: admin\n", encoding="utf-8")
    cfg = repo_root / ".overseer" / "config.yaml"
    import yaml

    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["roles_file"] = "roles.yaml"
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    from adapters.config import load_config

    config = load_config(cfg)
    body = load_honesty_entry(repo_root, "verdict-producer.json")
    from tools.honesty.ledger import append_entry
    from tools.honesty.types import LedgerAppendOptions

    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 23


def test_evidence_notes_injection_not_executed(tmp_path) -> None:
    seed_honesty_repo(tmp_path)
    artifact_hash = __import__("tests.support", fromlist=["honesty_artifact_hash"]).honesty_artifact_hash(tmp_path)
    payload = {
        "actor_role": "verifier",
        "actor_session_id": "v1",
        "artifact_sha256": artifact_hash,
        "passed": True,
        "evidence": {
            "reexecuted": ["verify-step:x"],
            "notes": "$(rm -rf /); __import__('os').system('echo pwned')",
        },
    }
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    code = run_cli(
        ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 0
    show = show_entries(config=load_honesty_config(tmp_path), repo_root=tmp_path, last_n=5)
    joined = "\n".join(show.stdout_lines)
    assert "__import__('os').system" in joined
    assert "rm -rf" in joined

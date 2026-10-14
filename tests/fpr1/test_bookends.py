"""Canonical Cursor fixture events; no claim of actual host lifecycle delivery."""
import io
import json
import shlex
import shutil
import subprocess

import pytest

from cli import product_bookends as bookends
from cli.v1_io import LIMIT, Refusal
from tests.v1.conftest import command, seed, write_action


@pytest.fixture
def bookend_repo(tmp_path):
    root = seed(tmp_path / "fixture with spaces and 'quote'")
    result = command("-C", root, "init", "--hooks")
    assert result.returncode == 0, result.stderr
    write_action(root, "Canonical fixture instruction.\n")
    return root


def invoke(root, event="sessionStart", payload="{}", **kwargs):
    return command(cwd=root, executable=root / bookends.EVENT_PATHS[event], input=payload, **kwargs)


def snapshot(root):
    return {str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode,
                                         path.stat().st_mtime_ns)
            for path in root.rglob("*") if path.is_file()}


def test_both_bookends_equal_manual_canonical_reader_and_write_nothing(bookend_repo):
    root = bookend_repo
    # A former active HANDOVER fence must never become an alternate authority.
    (root / "docs/OVERSEER-HANDOVER.md").write_text(
        "# Summary\n\n### Paste-ready prompt\n```text\nFOREIGN LEGACY ACTION\n```\n")
    before = snapshot(root)
    manual = command("-C", root, "next")
    assert manual.returncode == 0, manual.stderr
    for event in bookends.EVENT_PATHS:
        result = invoke(root, event, json.dumps({"workspace_roots": [str(root)],
                                                "lane": "product", "event": event}))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload == {"additional_context": manual.stdout,
                           "followup_message": manual.stdout}
        assert "FOREIGN LEGACY ACTION" not in result.stdout
    assert snapshot(root) == before


@pytest.mark.parametrize("payload,reason", [
    ("[]", "hook_input_invalid"),
    ("null", "hook_input_invalid"),
    ("{", "hook_input_invalid"),
    ('{"lane":"product","lane":"other"}', "hook_duplicate_key"),
    ('{"nested":{"x":1,"x":2}}', "hook_duplicate_key"),
    ('{"value":NaN}', "hook_input_invalid"),
    ('{"workspace_roots":null}', "hook_workspace_mismatch"),
    ('{"workspace_roots":false}', "hook_workspace_mismatch"),
    ('{"workspace_roots":""}', "hook_workspace_mismatch"),
    ('{"workspace_roots":{}}', "hook_workspace_mismatch"),
    ('{"workspace_roots":[false]}', "hook_workspace_mismatch"),
    ('{"workspace_roots":["."]}', "hook_workspace_mismatch"),
    ('{"workspace_root":"/"}', "hook_workspace_mismatch"),
    ('{"repo_root":"."}', "hook_workspace_mismatch"),
    ('{"lane":"security"}', "hook_lane_mismatch"),
    ('{"lane":null}', "hook_lane_mismatch"),
    ('{"repo_id":"foreign"}', "hook_identity_mismatch"),
    ('{"hook_event_name":"stop"}', "hook_event_mismatch"),
    ('{"event_name":"sessionEnd"}', "hook_event_mismatch"),
])
def test_event_assertions_refuse_without_action_text(bookend_repo, payload, reason):
    root = bookend_repo
    before = snapshot(root)
    result = invoke(root, payload=payload)
    assert result.returncode == 2 and not result.stdout
    assert reason in result.stderr
    assert snapshot(root) == before


def test_oversized_and_invalid_utf8_events_refuse(bookend_repo):
    root = bookend_repo
    for raw, reason in ((b" " * (LIMIT + 1), "hook_input_too_large"),
                        (b'{"lane":"\xff"}', "hook_input_invalid")):
        result = subprocess.run([str(root / bookends.EVENT_PATHS["sessionStart"])],
                                cwd=root, input=raw, capture_output=True, timeout=20)
        assert result.returncode == 2 and not result.stdout
        assert reason.encode() in result.stderr


@pytest.mark.parametrize("event", ["sessionStart", "stop"])
def test_stale_next_refuses_both_bookends_then_accepts_exact_closing_commit(bookend_repo, event):
    root = bookend_repo
    subprocess.run(["/usr/bin/git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                    "commit", "--allow-empty", "-m", "advance source"], check=True, capture_output=True)
    stale = invoke(root, event)
    assert stale.returncode == 2 and not stale.stdout
    assert "next_stale_head" in stale.stderr
    # Explicit publication against the new revision; no hook performed a repair.
    state = command("-C", root, "status", "--json")
    report = json.loads(state.stdout)
    from cli.v1_io import digest
    (root / "prompt.txt").write_text("Explicit successor after advance.\n")
    written = command("-C", root, "next-write", "--repo-id", report["repository"]["id"],
                      "--branch", "main", "--lane", "product", "--model", "GPT-6 Astra",
                      "--action-id", "SUCCESSOR", "--action-kind", "implement",
                      "--expect-next", digest((root / "docs/NEXT.md").read_bytes()),
                      "--prompt-file", "prompt.txt")
    assert written.returncode == 0, written.stderr
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", "docs/NEXT.md"], check=True, capture_output=True)
    subprocess.run(["/usr/bin/git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                    "commit", "-m", "publish exact NEXT"], check=True, capture_output=True)
    current = invoke(root, event)
    assert current.returncode == 0, current.stderr
    assert "Explicit successor after advance." in current.stdout


def test_generated_commands_handle_spaces_and_do_not_overwrite_host_instructions(tmp_path):
    root = seed(tmp_path / "space and 'quote'")
    (root / "AGENTS.md").write_text("Existing Codex instructions.\n")
    skill = root / ".claude/skills/print-next/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Existing Claude instructions.\n")
    result = command("-C", root, "init", "--hooks")
    assert result.returncode == 0, result.stderr
    assert (root / "AGENTS.md").read_text() == "Existing Codex instructions.\n"
    assert skill.read_text() == "Existing Claude instructions.\n"
    manifest = json.loads((root / ".cursor/hooks.json").read_bytes())
    assert set(manifest["hooks"]) == {"sessionStart", "stop"}
    for event in manifest["hooks"]:
        invocation = manifest["hooks"][event][0]["command"]
        assert shlex.split(invocation) == [str(root / bookends.EVENT_PATHS[event])]
        process = subprocess.run(["/bin/sh", "-c", invocation], cwd=root,
                                 input="{}", text=True, capture_output=True, timeout=20)
        assert process.returncode == 0, process.stderr
    guidance = (root / ".overseer/instructions/bookends.md").read_text()
    exact_command = guidance.split("```sh\n", 1)[1].split("\n```", 1)[0]
    assert shlex.split(exact_command) == [str(root / ".overseer/bin/ok"), "-C", str(root), "next"]
    assert "instruction-triggered" in guidance and "after" in guidance


def test_copied_or_edited_hook_cannot_become_owned_by_filename(bookend_repo, tmp_path):
    root = bookend_repo
    other = seed(tmp_path / "other")
    initialized = command("-C", other, "init", "--hooks")
    assert initialized.returncode == 0, initialized.stderr
    source = root / bookends.EVENT_PATHS["sessionStart"]
    shutil.copyfile(other / bookends.EVENT_PATHS["sessionStart"], source)
    # Direct internal transport entry still verifies the bytes at its claimed path.
    refused = command("-C", root, "hook", "--hook-path", source, input="{}",
                      executable=root / ".overseer/bin/ok")
    assert refused.returncode == 2 and not refused.stdout
    assert "hook_binding_mismatch" in refused.stderr


def test_source_dispatcher_cannot_skip_bound_hook_transport(bookend_repo):
    root = bookend_repo
    result = command("-C", root, "hook", "--hook-path",
                     root / bookends.EVENT_PATHS["sessionStart"], input="{}")
    assert result.returncode == 2 and not result.stdout
    assert "hook_requires_bound_launcher" in result.stderr


def test_event_field_conflict_and_repeated_roots_are_ambiguous(bookend_repo):
    root = bookend_repo
    for payload in ({"event": "sessionStart", "event_name": "stop"},
                    {"workspace_roots": [str(root), str(root)]}):
        result = invoke(root, payload=json.dumps(payload))
        assert result.returncode == 2 and not result.stdout


def test_event_read_bounds_text_stream_and_does_not_accept_surrogates():
    assert bookends.read_event(io.StringIO("{}")) == b"{}"
    with pytest.raises(Refusal, match="hook_input_too_large"):
        bookends.read_event(io.StringIO("é" * LIMIT))
    with pytest.raises(Refusal, match="hook_input_invalid"):
        bookends.read_event(io.StringIO("\ud800"))


def test_legacy_bound_adapter_remains_readable(bookend_repo):
    root = bookend_repo
    for event, relative in bookends.EVENT_PATHS.items():
        (root / relative).write_bytes(bookends.hook_script(root))
        result = invoke(root, event)
        assert result.returncode == 0, result.stderr
        assert "Canonical fixture instruction." in result.stdout

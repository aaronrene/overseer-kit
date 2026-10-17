"""FPR-6 change/preservation checks; does not rerun product or host tests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from cli import v1
import yaml

EVIDENCE = ROOT / "docs/validation/fpr6-automatic"
OPENING = json.loads((EVIDENCE / "opening.json").read_text())
BASE = OPENING["head"]
CHANGES = {
    ".overseer/config.yaml", ".overseer/version.lock", "cli/product_bookends.py",
    "docs/NEXT.md", "docs/ROADMAP.md", "docs/OVERSEER-HANDOVER.md",
    "docs/decisions/FPR-6-AUTOMATIC-COMPLETION-PLAN.md",
    "docs/decisions/FPR-OPS-1-CLIENT-CHANGE-REQUEST.md",
}
ADDITIONS = {
    "docs/decisions/FPR-6-AUTOMATIC-DEPENDENCIES.md",
    "docs/validation/FPR-6-AUTOMATIC-COMPLETION.md",
    "tests/fpr6/test_bookend_lane_types.py",
}


def git(*args):
    return subprocess.check_output(["/usr/bin/git", "-C", str(ROOT), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--postcommit", action="store_true")
    args = parser.parse_args()
    assert str(ROOT.resolve()) == OPENING["physical_root"]
    assert git("rev-parse", "--show-toplevel").decode().strip() == str(ROOT)
    assert git("branch", "--show-current").decode().strip() == OPENING["branch"]
    head = git("rev-parse", "HEAD").decode().strip()
    if args.postcommit:
        assert git("show", "-s", "--format=%P", head).decode().strip() == BASE
        assert not git("status", "--porcelain")
    else:
        assert head == BASE
    changed = git("diff", "--name-only", BASE).decode().splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").decode().splitlines()
    assert all(p in CHANGES | ADDITIONS or p.startswith("docs/validation/fpr6-automatic/")
               for p in changed + untracked), changed + untracked
    assert not git("diff", "--name-only", BASE, "--", "docs/reviews", "docs/releases",
                   "tests/historical", "desktop", "requirements*", ".cursor", ".claude")
    # This preserves all original tests and prior evidence, not just selected files.
    old = git("ls-tree", "-r", "--name-only", BASE, "--", "tests", "docs/validation").decode().splitlines()
    assert not git("diff", "--name-only", BASE, "--", *old)
    for p, digest in OPENING["hooks"].items():
        assert sha((ROOT / p).read_bytes()) == digest, p
    config = yaml.safe_load((ROOT / ".overseer/config.yaml").read_bytes())
    original = yaml.safe_load(git("show", BASE + ":.overseer/config.yaml"))
    runtime = config.pop("runtime")
    original.pop("runtime")
    assert config == original
    assert runtime == v1.runtime() == json.loads((EVIDENCE / "source-after.json").read_text())["runtime"]
    before_lock = yaml.safe_load(git("show", BASE + ":.overseer/version.lock"))
    lock = yaml.safe_load((ROOT / ".overseer/version.lock").read_bytes())
    before_rows = {r["path"]: r for r in before_lock.pop("footprint")}
    rows = {r["path"]: r for r in lock.pop("footprint")}
    assert before_lock == lock and before_rows.keys() == rows.keys()
    delta = [p for p in rows if rows[p] != before_rows[p]]
    assert delta == ["docs/OVERSEER-HANDOVER.md", "docs/ROADMAP.md"]
    for p in delta:
        assert rows[p]["sha256"] == "sha256:" + sha((ROOT / p).read_bytes())
        assert {k:v for k,v in rows[p].items() if k != "sha256"} == {
            k:v for k,v in before_rows[p].items() if k != "sha256"}
    # One exact production delta; accepted hooks/response and all other runtime files retained.
    original_source = git("show", BASE + ":cli/product_bookends.py")
    expected = original_source.replace(
        b'if payload["lane"] not in config[\'docs\'][\'lanes\'] or (',
        b'if not isinstance(payload["lane"], str) or payload["lane"] not in config[\'docs\'][\'lanes\'] or (')
    assert (ROOT / "cli/product_bookends.py").read_bytes() == expected != original_source
    cmd = [str(ROOT / ".overseer/bin/ok"), "-C", str(ROOT), "status", "--json"]
    process = subprocess.run(cmd, capture_output=True, text=True, check=True)
    state = json.loads(process.stdout)
    assert state["ok"] and state["repository"] == OPENING["repository"]
    assert state["next"]["action_id"] == "OVERSEER-FPR6-CAPABILITY-DEPENDENCY-1"
    assert state["next"]["action_kind"] == "stop" and state["next"]["lane"] == "product"
    assert state["next"]["base_head"] == BASE
    assert state["prompt"] == (EVIDENCE / "next-prompt.txt").read_text()
    assert state["next_sha256"] == "225811f44bffc75881847588fbb933eace532ee45175b99488227eb7ba630731"
    # Check local links in the newly written reports without any network access.
    for name in ("docs/decisions/FPR-6-AUTOMATIC-DEPENDENCIES.md",
                 "docs/validation/FPR-6-AUTOMATIC-COMPLETION.md"):
        path = ROOT / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            assert (path.parent / target.split("#", 1)[0]).exists(), (name, target)
    inventory = EVIDENCE / "ARTIFACTS.json"
    if args.postcommit:
        for name, digest in json.loads(inventory.read_text()).items():
            assert sha((EVIDENCE / name).read_bytes()) == digest, name
    subprocess.run(["/usr/bin/git", "-C", str(ROOT), "diff", "--check", BASE], check=True)
    print(json.dumps(dict(ok=True,postcommit=args.postcommit,head=head,parent=BASE,
        bound_status=True,runtime=runtime,action=state["next"],next_sha256=state["next_sha256"],
        original_test_and_evidence_paths_preserved=len(old),existing_hooks_preserved=True,
        non_runtime_settings_preserved=True,only_lock_rows_changed=delta,
        tracked_changes=changed,new_files=untracked), indent=2))


if __name__ == "__main__":
    main()

"""Run bounded transport checks offline into a fresh evidence/fixture location."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from cli import v1

OWNED = ("tools/hosted_dashboard/http_client.py", "cli/product_service.py", "tools/close_ritual/pr_land.py", "tests/fpr5/test_transport_repairs.py", "tests/fpr3/test_engines.py")


def snapshot():
    return {
        "head": subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "branch": subprocess.check_output(["/usr/bin/git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "runtime": v1.runtime(),
        "owned_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in OWNED},
        "worktree_status": subprocess.check_output(["/usr/bin/git", "status", "--short"], cwd=ROOT, text=True),
    }


label = sys.argv[1]
out = Path(__file__).resolve().parent / label
out.mkdir()
fixtures = Path(tempfile.mkdtemp(prefix="overseer-fpr5-transport-", dir="/private/tmp"))
args = [str(ROOT / ".venv/bin/python"), "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp=" + str(fixtures / "fixtures"), "--junitxml=" + str(out / "results.xml"), *(sys.argv[2:] or ["tests/fpr5/test_transport_repairs.py"])]
env = {"PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_OPTIONAL_LOCKS": "0"}
record = {"argv": args, "cwd": str(ROOT), "environment_overrides": env, "fixtures": str(fixtures), "before": snapshot(), "python": sys.version, "boundary": "Synthetic HTTP and fake gh only; pytest loopback fixtures may bind locally when selected. No external provider."}
(out / "command.json").write_text(json.dumps(record, indent=2) + "\n")
with (out / "results.log").open("w") as stream:
    result = subprocess.run(args, cwd=ROOT, env=dict(os.environ, **env), stdout=stream, stderr=subprocess.STDOUT)
record.update(exit_code=result.returncode, after=snapshot())
record["artifacts"] = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in ("results.log", "results.xml") if (out / name).exists()}
(out / "command.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"exit_code": result.returncode, "evidence": str(out), "fixtures": str(fixtures)}, indent=2))
raise SystemExit(result.returncode)

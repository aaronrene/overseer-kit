#!/usr/bin/env python3
"""Offline, disposable source-installation evidence; not a package installer.

Run with the bound worktree's .venv/bin/python -I -B. Source is read only from
that worktree's Git objects; only the new --output directory is mutated.
"""
import argparse
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import venv

CURRENT = "348e0f323a3b17cd5022a1bfd56fa09a6831c51f"
PREVIOUS = "333f81e9bf847dcd418b305b931b1279da3c7ade"
RUNTIME = ("cli/__init__.py", "cli/bootstrap.py", "cli/main.py", "cli/ok",
           "cli/overseer", "cli/v1.py", "cli/v1_io.py", "cli/digest.py", "VERSION")
LIVING = ("docs/ROADMAP.md", "docs/OVERSEER-HANDOVER.md")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(root):
    """Bytes, symlink targets, modes and mtimes, including Git files/directories."""
    result = {}
    for p in sorted(root.rglob("*")):
        s = p.lstat()
        payload = (os.readlink(p) if p.is_symlink() else
                   sha(p.read_bytes()) if p.is_file() else None)
        result[str(p.relative_to(root))] = [s.st_mode, s.st_mtime_ns, payload]
    return result


def tree(root):
    return {name: [value[0], value[2]] for name, value in fingerprint(root).items()
            if not (root / name).is_dir()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    assert Path(sys.prefix).resolve() == source / ".venv", "use source-local venv"
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    output = output.resolve()
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GIT_", "PYTHON")) and k != "VIRTUAL_ENV"}
    env.update(PATH="/usr/bin:/bin", GIT_CONFIG_GLOBAL="/dev/null",
               GIT_CONFIG_NOSYSTEM="1", GIT_OPTIONAL_LOCKS="0",
               PYTHONDONTWRITEBYTECODE="1", LC_ALL="C")
    commands = []
    checks = []
    report = {"source": str(source), "output": str(output),
              "python": sys.version, "current_commit": CURRENT,
              "previous_commit": PREVIOUS, "checks": checks,
              "previous_limitations": "Known R1/R2 findings remain; operability only."}

    def run(argv, cwd=source, expected=0, error=None):
        p = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                           capture_output=True, text=True, timeout=30)
        commands.append({"argv": list(map(str, argv)), "cwd": str(cwd),
                         "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr})
        (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        assert p.returncode == expected, commands[-1]
        if error:
            assert error in p.stderr and not p.stdout, commands[-1]
        return p.stdout

    def git(root, *argv):
        return run(["/usr/bin/git", "-c", "core.hooksPath=/dev/null",
                    "-c", "core.fsmonitor=false", "-C", root, *argv]).strip()

    def checked(name):
        checks.append(name)
        print("PASS", name, flush=True)

    def unchanged(root, operation, name):
        before = fingerprint(root)
        result = operation()
        assert fingerprint(root) == before, name
        checked(name)
        return result

    assert Path(git(source, "rev-parse", "--show-toplevel")).resolve() == source
    assert git(source, "rev-parse", CURRENT + "^{commit}") == CURRENT
    assert git(source, "rev-parse", PREVIOUS + "^{commit}") == PREVIOUS
    assert git(source, "rev-parse", CURRENT + "^") == PREVIOUS
    archives = {}
    report["builds"] = {}
    for label, commit in (("current", CURRENT), ("previous", PREVIOUS)):
        destination = output / (label + "-source")
        destination.mkdir()
        archive = subprocess.run(["/usr/bin/git", "-C", str(source), "archive",
                                  "--format=tar", commit], env=env,
                                 check=True, capture_output=True, timeout=30).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(destination, filter="data")
        archives[label] = destination
        report["builds"][label] = {
            "commit": commit, "archive_sha256": sha(archive),
            "source_files": len(tree(destination)),
            "source_manifest_sha256": sha(json.dumps(tree(destination), sort_keys=True).encode()),
            "runtime_sha256": sha(b"".join(p.encode() + b"\0" +
                (destination / p).read_bytes() + b"\0" for p in RUNTIME)),
        }
    checked("current and previous source exported solely from bound Git objects")

    active = output / "installation"
    alternate = output / "other-installation"
    active.mkdir()
    alternate.mkdir()
    site = source / ".venv/lib" / ("python%d.%d" % sys.version_info[:2]) / "site-packages"
    distribution = importlib.metadata.distribution("PyYAML")
    dependency_files = {}
    for item in distribution.files:
        relative = Path(item)
        if "__pycache__" in relative.parts or relative.suffix in (".pyc", ".pth"):
            continue
        original = Path(distribution.locate_file(item)).resolve(strict=True)
        assert original.is_relative_to(site) and not relative.is_absolute()
        assert ".." not in relative.parts and not relative.name.startswith("__editable__")
        dependency_files[str(relative)] = sha(original.read_bytes())
    report["offline_dependency"] = {"name": "PyYAML", "version": distribution.version,
                                    "files_sha256": dependency_files}

    def environment(root):
        venv.EnvBuilder(with_pip=False, symlinks=True).create(root / ".venv")
        target = root / ".venv/lib" / ("python%d.%d" % sys.version_info[:2]) / "site-packages"
        for relative, digest in dependency_files.items():
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(site / relative, path)
            assert sha(path.read_bytes()) == digest
        assert (root / ".venv/bin/python3").is_symlink()
        assert not list(target.glob("*.pth"))
        probe = json.loads(run([root / ".venv/bin/python3", "-I", "-B", "-c",
            "import json, sys, yaml; print(json.dumps({'prefix': sys.prefix, "
            "'yaml': yaml.__file__, 'version': yaml.__version__}))"]))
        assert Path(probe["prefix"]).resolve() == root / ".venv"
        assert Path(probe["yaml"]).is_relative_to(target)
        return probe

    def install(label, root):
        # Deliberate maintenance at a fixed root; no concurrent process or rebind.
        for child in root.iterdir():
            if child.name != ".venv":
                if child.is_dir() and not child.is_symlink():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        shutil.copytree(archives[label], root, dirs_exist_ok=True, symlinks=True)
        actual = {p: v for p, v in tree(root).items() if not p.startswith(".venv/")}
        assert actual == tree(archives[label]), label
        checked(label + " exact committed source installed at " + root.name)

    install("current", active)
    install("current", alternate)
    report["environments"] = [environment(active), environment(alternate)]
    venv_before = fingerprint(active / ".venv")
    checked("fresh conventional symlinked venvs use local offline PyYAML only")

    def seed(name):
        root = output / name
        root.mkdir()
        git(root, "init", "-b", "main")
        git(root, "config", "user.name", "Disposable Fixture")
        git(root, "config", "user.email", "fixture@example.invalid")
        git(root, "commit", "--allow-empty", "-m", "seed")
        (root / "docs").mkdir()
        for path in LIVING:
            (root / path).write_text("Owner living document: " + path + "\n")
        return root

    repo = seed("consumer-fixture")
    other = seed("other-fixture")
    living = {p: fingerprint(repo)[p] for p in LIVING}
    ok = active / "cli/ok"
    bound = repo / ".overseer/bin/ok"
    run([ok, "-C", repo, "init", "--repo-name", "offline-rollback-fixture"])
    state = json.loads(run([bound, "-C", repo, "status", "--json"]))
    identity = state["repository"]
    assert identity["root"] == str(repo)
    report["fixture_identity"] = identity
    assert {p: fingerprint(repo)[p] for p in LIVING} == living
    unchanged(repo, lambda: run([ok, "-C", repo, "init"]), "repeat init preserves UUID and files")
    checked("clean init preserves preexisting living documents")

    def expectations(s):
        values = dict(repo_id=identity["id"], branch="main", lane="product",
                      model="GPT-6 Astra", action_id=s["next"]["action_id"],
                      action_kind=s["next"]["action_kind"], expect_next=s["next_sha256"])
        return [v for key, value in values.items() for v in ("--" + key.replace("_", "-"), value)]

    def reads(label):
        s = json.loads(run([bound, "-C", repo, "status", "--json"]))
        assert s["repository"] == identity
        assert s["runtime"]["root"] == str(active)
        assert s["runtime"]["sha256"] == report["builds"][label]["runtime_sha256"]
        def operation():
            run([bound, "next", *expectations(s)], cwd=repo)
            run([ok, "-C", repo, "next", *expectations(s)])
            run([bound, "-C", repo, "status", "--json", *expectations(s)])
        unchanged(repo, operation, label + " bound/cwd/explicit reads preserve bytes modes mtimes and Git")
        return s

    state = reads("current")
    alias = output / "physical-alias"
    alias.symlink_to(repo, target_is_directory=True)
    alias_state = json.loads(unchanged(repo,
        lambda: run([ok, "-C", alias, "status", "--json"]), "symlink selector resolves physical root"))
    assert alias_state["repository"] == identity

    def publish(label):
        s = json.loads(run([bound, "-C", repo, "status", "--json"]))
        prompt = repo / "fixture-prompt.txt"
        prompt.write_text("Disposable " + label + " source-installation action.\n")
        options = expectations(s)
        options[options.index("--action-id") + 1] = "FIXTURE-" + label.upper()
        options[options.index("--action-kind") + 1] = "maintain"
        run([bound, "-C", repo, "next-write", *options, "--prompt-file", prompt.name])
        published = (repo / "docs/NEXT.md").read_bytes()
        unchanged(repo, lambda: run([bound, "-C", repo, "next-write", *options,
            "--prompt-file", prompt.name], expected=2, error="stale_write"), label + " stale CAS refuses")
        git(repo, "add", ".")
        git(repo, "commit", "-m", label + " fixture closing commit")
        assert (repo / "docs/NEXT.md").read_bytes() == published
        return reads("previous" if label == "previous" else "current")

    state = publish("current")
    config = repo / ".overseer/config.yaml"
    original = config.read_bytes()
    config.write_bytes(original.replace(identity["id"].encode(), b"00000000-0000-0000-0000-000000000000"))
    unchanged(repo, lambda: run([bound, "-C", repo, "next"], expected=2,
        error="launcher_identity_mismatch"), "bound launcher rejects changed UUID")
    config.write_bytes(original)
    (other / ".overseer").mkdir()
    shutil.copy2(config, other / ".overseer/config.yaml")
    unchanged(other, lambda: run([ok, "-C", other, "status"], expected=2,
        error="config_repository_mismatch"), "copied configuration rejects different physical root")
    unchanged(other, lambda: run([bound, "-C", other, "next"], expected=2,
        error="launcher_repository_mismatch"), "bound launcher rejects other repository")
    for command in ("status", "next", "sync"):
        unchanged(repo, lambda command=command: run([alternate / "cli/ok", "-C", repo, command],
            expected=2, error="runtime_installation_mismatch"), "other installation refuses " + command)
    interpreter = active / ".venv/bin/python3"
    target = os.readlink(interpreter)
    interpreter.unlink()
    try:
        run([ok, "-C", repo, "next"], expected=2, error="no runtime fallback")
    finally:
        interpreter.symlink_to(target)
    venv_before = fingerprint(active / ".venv")
    checked("missing installation interpreter refuses without PATH or neighbor fallback")

    report["transitions"] = []
    for label in ("previous", "current"):
        retained = {p: fingerprint(repo)[p] for p in (*LIVING, "docs/NEXT.md")}
        old_config = config.read_bytes()
        install(label, active)
        assert fingerprint(active / ".venv") == venv_before
        for command in ("status", "next", "init"):
            unchanged(repo, lambda command=command: run([ok, "-C", repo, command],
                expected=2, error="runtime_changed"), label + " pre-refresh " + command + " refuses")
        unchanged(repo, lambda: run([bound, "-C", repo, "next"], expected=2,
            error="runtime_changed"), label + " pre-refresh bound NEXT refuses")
        stale = expectations(state)
        unchanged(repo, lambda: run([bound, "-C", repo, "next-write", *stale,
            "--prompt-file", "fixture-prompt.txt"], expected=2, error="runtime_changed"),
            label + " pre-refresh bound writer refuses")
        dry = json.loads(unchanged(repo, lambda: run([bound, "-C", repo, "sync", "--dry-run", "--json"]),
                                  label + " sync dry-run is read-only"))
        assert dry["changed"] == [".overseer/config.yaml"]
        synced = json.loads(run([bound, "-C", repo, "sync", "--json"]))
        assert synced["changed"] == dry["changed"]
        assert config.read_bytes() != old_config
        assert {p: fingerprint(repo)[p] for p in retained} == retained
        state = reads(label)
        report["transitions"].append({"to": label, "runtime": state["runtime"],
            "repo_id": state["repository"]["id"], "next_sha256_preserved": state["next_sha256"],
            "sync_changed": synced["changed"]})
        checked(label + " explicit refresh preserves UUID physical root NEXT and living documents")
        unchanged(repo, lambda: run([bound, "-C", repo, "sync"]), label + " repeated sync is a no-op")
        state = publish("previous" if label == "previous" else "recovered-current")

    # Owned launcher repair is explicitly requested and leaves canonical content alone.
    retained = {p: fingerprint(repo)[p] for p in (*LIVING, "docs/NEXT.md")}
    bound.chmod(0o644)
    dry = json.loads(unchanged(repo, lambda: run([ok, "-C", repo, "sync", "--dry-run", "--json"]),
                              "launcher mode repair dry-run is read-only"))
    assert dry["changed"] == [".overseer/bin/ok"]
    run([ok, "-C", repo, "sync"])
    assert stat.S_IMODE(bound.stat().st_mode) == 0o755
    assert {p: fingerprint(repo)[p] for p in retained} == retained
    state = reads("current")
    assert {p: fingerprint(repo)[p] for p in LIVING} == living
    assert fingerprint(active / ".venv") == venv_before
    report["final_status"] = state
    report["result"] = "passed"
    report["commands_sha256"] = sha((output / "commands.json").read_bytes())
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": "passed", "checks": len(checks), "evidence": str(output / "result.json")}))


if __name__ == "__main__":
    main()

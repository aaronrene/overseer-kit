"""Test helpers (not pytest fixtures)."""

from __future__ import annotations

import os
from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.factory import create_adapter
from adapters.runner import CommandResult, RecordingRunner

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PILOT = FIXTURES / "pilot"
CHECKPOINTS = FIXTURES / "checkpoints"
HONESTY = FIXTURES / "honesty"


def write_config(repo_root: Path, name: str) -> Path:
    src = FIXTURES / name
    dest = repo_root / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def load_fixture_config(repo_root: Path, name: str) -> OverseerConfig:
    return load_config(write_config(repo_root, name))


def ok(stdout: str = "") -> CommandResult:
    return CommandResult(stdout=stdout, stderr="", exit_code=0)


def fail(stderr: str = "error", code: int = 1) -> CommandResult:
    return CommandResult(stdout="", stderr=stderr, exit_code=code)


def make_runner(responses: dict[str, CommandResult]) -> RecordingRunner:
    return RecordingRunner(responses=responses, calls=[])


def adapter_for(config: OverseerConfig, repo_root: Path, runner: RecordingRunner):
    return create_adapter(config, repo_root, runner=runner)


def git_status_runner(branch: str = "main", dirty: bool = False) -> RecordingRunner:
    """Recording runner with git-only ``status()`` responses."""
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
        }
    )


def muse_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
) -> RecordingRunner:
    """Recording runner with muse-only ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} branch --show-current": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
        }
    )


def muse_mirror_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
) -> RecordingRunner:
    """Recording runner with muse+git-mirror ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
        }
    )


def run_cli(
    argv: list[str],
    *,
    cwd: Path,
    runner: RecordingRunner | None = None,
    kit: Path | None = None,
    review_provider_factory=None,
    script_executor=None,
    json_mode: bool = False,
) -> int:
    """Invoke ``cli.main`` with an injected runner and working directory."""
    from cli.context import CliContext
    from cli.main import main
    from cli.output import OutputContext

    old_cwd = Path.cwd()
    os.chdir(cwd)
    try:
        ctx = CliContext.create(
            runner=runner or make_runner({}),
            cwd=cwd,
            kit=kit,
            output=OutputContext(json_mode=json_mode),
            review_provider_factory=review_provider_factory,
            script_executor=script_executor,
        )
        return main(argv, ctx=ctx)
    finally:
        os.chdir(old_cwd)


def seed_muse_substrate(repo_root: Path) -> None:
    """Create minimal healthy ``.muse/`` for muse-backed regime tests."""
    muse = repo_root / ".muse"
    muse.mkdir(parents=True, exist_ok=True)
    (muse / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (muse / "repo.json").write_text("{}", encoding="utf-8")
    (muse / "config.toml").write_text("", encoding="utf-8")


def seed_freeze_repo(repo_root: Path, *, config_name: str = "config-git-only.yaml") -> Path:
    """Write config and copy a freeze artifact fixture into a temp repo."""
    write_config(repo_root, config_name)
    if "muse" in config_name:
        seed_muse_substrate(repo_root)
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    artifact = docs / "FREEZE.md"
    artifact.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")
    return artifact


def pass_provider_factory():
    """Factory returning a provider that always passes."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=[])

    return _factory


def findings_provider_factory(findings):
    """Factory returning a provider with scripted findings."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=list(findings))

    return _factory


def unreachable_provider_factory(cause: str = "offline"):
    """Factory returning an unreachable local provider."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(force_unreachable=True, unreachable_cause=cause)

    return _factory


class FakeHttpTransport:
    """Recording HTTP transport for API provider tests (no network)."""

    def __init__(
        self,
        *,
        health_status: int = 200,
        health_body: bytes = b'{"status":"ok"}',
        review_status: int = 200,
        review_body: bytes | None = None,
        fail_health: bool = False,
        fail_review: bool = False,
    ) -> None:
        self.health_status = health_status
        self.health_body = health_body
        self.review_status = review_status
        self.review_body = review_body or b'{"findings":[]}'
        self.fail_health = fail_health
        self.fail_review = fail_review
        self.calls: list[dict] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None = None,
        timeout: float = 30.0,
    ) -> tuple[int, bytes]:
        from tools.freeze_reviewer.providers.api_client import ProviderTransportError

        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": body,
            }
        )
        if "/health" in url:
            if self.fail_health:
                raise ProviderTransportError("health transport failure")
            return self.health_status, self.health_body
        if self.fail_review:
            raise ProviderTransportError("review transport failure")
        return self.review_status, self.review_body


def api_provider_factory(transport: FakeHttpTransport):
    """Factory returning an API provider wired to a fake HTTP transport."""
    from tools.freeze_reviewer.providers.api_client import ReviewApiClient
    from tools.freeze_reviewer.providers.base import ApiReviewProvider

    def _factory(_provider_name: str) -> ApiReviewProvider:
        client = ReviewApiClient(transport=transport)
        return ApiReviewProvider(client=client)

    return _factory


def api_unreachable_provider_factory(cause: str = "API provider unavailable"):
    """Factory returning a forced-unreachable API provider."""
    from tools.freeze_reviewer.providers.base import ApiReviewProvider

    def _factory(_provider_name: str) -> ApiReviewProvider:
        return ApiReviewProvider(force_unreachable=True, unreachable_cause=cause)

    return _factory


def seed_checkpoint_repo(repo_root: Path) -> None:
    """Copy checkpoint fixture pack into a temp repo and mark scripts executable."""
    import shutil
    import stat

    (repo_root / ".overseer").mkdir(parents=True, exist_ok=True)
    config_src = CHECKPOINTS / "config-checkpoints-enabled.yaml"
    (repo_root / ".overseer" / "config.yaml").write_text(
        config_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in ("policy", "manifests", "scripts"):
        src = CHECKPOINTS / rel
        dest = repo_root / rel
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    for script in (repo_root / "scripts" / "verify").glob("*.py"):
        script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def load_checkpoint_config(repo_root: Path) -> OverseerConfig:
    """Load checkpoint-enabled config from a seeded repo."""
    seed_checkpoint_repo(repo_root)
    return load_config(repo_root / ".overseer" / "config.yaml")


def seed_honesty_repo(repo_root: Path) -> None:
    """Copy honesty fixture pack into a temp repo."""
    import shutil

    (repo_root / ".overseer").mkdir(parents=True, exist_ok=True)
    config_src = HONESTY / "config-honesty-enabled.yaml"
    (repo_root / ".overseer" / "config.yaml").write_text(
        config_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in ("artifacts", "entries"):
        src = HONESTY / rel
        dest = repo_root / rel
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)


def load_honesty_config(repo_root: Path) -> OverseerConfig:
    """Load honesty-enabled config from a seeded repo."""
    seed_honesty_repo(repo_root)
    return load_config(repo_root / ".overseer" / "config.yaml")


def honesty_artifact_hash(repo_root: Path) -> str:
    """SHA-256 of the fixture sample artifact."""
    from tools.honesty.artifact import sha256_file_bytes

    return sha256_file_bytes(repo_root / "artifacts" / "sample.txt")


def load_honesty_entry(repo_root: Path, name: str, *, artifact_hash: str | None = None) -> dict:
    """Load a verdict entry fixture with artifact hash substituted."""
    import json

    text = (HONESTY / "entries" / name).read_text(encoding="utf-8")
    if artifact_hash is None:
        artifact_hash = honesty_artifact_hash(repo_root)
    text = text.replace("PLACEHOLDER", artifact_hash)
    return json.loads(text)


def seed_pilot_tree(
    repo_root: Path,
    *,
    handover_rel: str,
    handover_text: str = "# Hand preserved handover\n",
    roadmap_rel: str | None = None,
    roadmap_text: str | None = None,
    extra_cursor_rules: dict[str, str] | None = None,
) -> None:
    """Create a pre-existing living-doc layout for migrate fixtures."""
    hand = repo_root / handover_rel
    hand.parent.mkdir(parents=True, exist_ok=True)
    hand.write_text(handover_text, encoding="utf-8")
    if roadmap_rel is not None:
        road = repo_root / roadmap_rel
        road.parent.mkdir(parents=True, exist_ok=True)
        road.write_text(roadmap_text or "# Hand preserved roadmap\n", encoding="utf-8")
    if extra_cursor_rules:
        rules = repo_root / ".cursor" / "rules"
        rules.mkdir(parents=True, exist_ok=True)
        for name, text in extra_cursor_rules.items():
            (rules / name).write_text(text, encoding="utf-8")


def lock_origins(repo_root: Path) -> dict[str, str]:
    """Return path → origin map from ``version.lock``."""
    from cli.version_lock import entry_origin, read_version_lock

    lock = read_version_lock(repo_root / ".overseer" / "version.lock")
    return {e.path: entry_origin(e) for e in lock.footprint}


def generate_ed25519_keypair() -> tuple[object, str]:
    """Return ``(private_key, ed25519:<base64> pubkey token)`` for tests only."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from tools.honesty.ed25519_util import encode_ed25519_token

    private_key = Ed25519PrivateKey.generate()
    pubkey_token = encode_ed25519_token(private_key.public_key().public_bytes_raw())
    return private_key, pubkey_token


def sign_entry_hash(private_key: object, entry_hash_hex: str) -> str:
    """Sign lowercase hex ``entry_hash_hex``; return ``ed25519:<base64>`` token (tests only)."""
    from tools.honesty.ed25519_util import encode_ed25519_token

    sig_bytes = private_key.sign(entry_hash_hex.encode("utf-8"))  # type: ignore[attr-defined]
    return encode_ed25519_token(sig_bytes)


def attach_signed_provenance(
    body: dict,
    *,
    pubkey_token: str,
    agent_id: str = "cursor-agent",
    model_id: str = "gpt-5.6",
    human_ref: str | None = None,
) -> dict:
    """Return a copy of ``body`` with unsigned provenance identity fields."""
    provenance: dict = {"agent_id": agent_id, "model_id": model_id}
    if human_ref is not None:
        provenance["human_ref"] = human_ref
    signed = dict(body)
    signed["provenance"] = provenance
    signed["_test_pubkey"] = pubkey_token
    return signed


def sign_append_body(
    body: dict,
    *,
    kind: str,
    prev_hash: str,
    private_key: object,
    pubkey_token: str | None = None,
) -> dict:
    """Validate, hash, sign, and return an append-ready body with ``provenance.sig``."""
    from tools.honesty.validate import validate_append_body

    pubkey = pubkey_token or body.pop("_test_pubkey", None)
    if pubkey is None:
        raise ValueError("pubkey_token required")
    draft = dict(body)
    draft.pop("_test_pubkey", None)
    validated = validate_append_body(kind=kind, body=draft)
    preview = dict(validated)
    preview["prev_hash"] = prev_hash
    preview["provenance"] = {**validated["provenance"], "pubkey": pubkey}
    entry_hash = compute_entry_hash(preview)
    signed = dict(validated)
    signed["provenance"] = {
        **validated["provenance"],
        "pubkey": pubkey,
        "sig": sign_entry_hash(private_key, entry_hash),
    }
    return signed


def compute_entry_hash(body: dict) -> str:
    """Re-export for tests building signing previews."""
    from tools.honesty.canonical import compute_entry_hash as _compute

    return _compute(body)


def finalize_signed_body(body: dict, *, private_key: object, prev_hash: str) -> dict:
    """Compute envelope hashes and attach ``provenance.sig`` (tests / direct ledger writes)."""
    from tools.honesty.canonical import compute_entry_hash
    from tools.honesty.genesis import utc_now_z

    entry = dict(body)
    if not entry.get("ts"):
        entry["ts"] = utc_now_z()
    entry["prev_hash"] = prev_hash
    entry_hash = compute_entry_hash(entry)
    entry["entry_hash"] = entry_hash
    provenance = dict(entry.get("provenance", {}))
    provenance["sig"] = sign_entry_hash(private_key, entry_hash)
    entry["provenance"] = provenance
    return entry


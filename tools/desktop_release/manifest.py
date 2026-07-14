"""Release manifest builder and validator (§QR.7.1)."""

from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence

from tools.desktop_release.constants import (
    MANIFEST_SCHEMA_VERSION,
    PLATFORMS,
    PRODUCT_IDENTIFIER,
    PRODUCT_NAME,
    SIGNED_METHODS_BY_PLATFORM,
    SIGNING_METHODS,
    SIGNING_STATUSES,
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ManifestError(ValueError):
    """Raised when a release manifest fails schema or signing rules."""


def _require_str(obj: Mapping[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"manifest missing string field: {key}")
    return value


def validate_artifact(artifact: Mapping[str, Any]) -> None:
    """Validate one ``artifacts[]`` entry."""
    if not isinstance(artifact, Mapping):
        raise ManifestError("artifact must be an object")
    platform = _require_str(artifact, "platform")
    if platform not in PLATFORMS:
        raise ManifestError(f"unknown platform: {platform!r}")
    filename = _require_str(artifact, "filename")
    if "/" in filename or "\\" in filename:
        raise ManifestError(f"filename must be basename only: {filename!r}")
    sha256 = _require_str(artifact, "sha256").lower()
    if not _SHA256_RE.match(sha256):
        raise ManifestError(f"invalid sha256: {sha256!r}")
    signing = artifact.get("signing")
    if not isinstance(signing, Mapping):
        raise ManifestError("artifact.signing must be an object")
    status = _require_str(signing, "status")
    if status not in SIGNING_STATUSES:
        raise ManifestError(f"unknown signing.status: {status!r}")
    method = _require_str(signing, "method")
    if method not in SIGNING_METHODS:
        raise ManifestError(f"unknown signing.method: {method!r}")
    if status == "signed":
        if method == "none":
            raise ManifestError("signed + method none refused")
        allowed = SIGNED_METHODS_BY_PLATFORM[platform]
        if method not in allowed:
            raise ManifestError(
                f"signing.method {method!r} not allowed for platform {platform!r}"
            )


def validate_manifest(data: Mapping[str, Any]) -> None:
    """Validate a full release manifest document (§QR.7.1 enums + rules)."""
    if not isinstance(data, Mapping):
        raise ManifestError("manifest must be an object")
    schema = data.get("schema_version")
    if schema != MANIFEST_SCHEMA_VERSION:
        raise ManifestError(f"unsupported schema_version: {schema!r}")
    if _require_str(data, "product") != PRODUCT_NAME:
        raise ManifestError(f"product must be {PRODUCT_NAME!r}")
    if _require_str(data, "identifier") != PRODUCT_IDENTIFIER:
        raise ManifestError(f"identifier must be {PRODUCT_IDENTIFIER!r}")
    _require_str(data, "version")
    git_tag = _require_str(data, "git_tag")
    if not git_tag.startswith("v"):
        raise ManifestError(f"git_tag must start with v: {git_tag!r}")
    git_sha = _require_str(data, "git_sha").lower()
    if not _GIT_SHA_RE.match(git_sha):
        raise ManifestError(f"git_sha must be 40-char hex: {git_sha!r}")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        raise ManifestError("artifacts must be an array")
    if len(artifacts) == 0:
        raise ManifestError("artifacts must be non-empty")
    for item in artifacts:
        validate_artifact(item)


def build_manifest(
    *,
    version: str,
    git_sha: str,
    artifacts: Sequence[Mapping[str, Any]],
    git_tag: str | None = None,
    product: str = PRODUCT_NAME,
    identifier: str = PRODUCT_IDENTIFIER,
) -> dict[str, Any]:
    """Build a schema_version=1 release manifest and validate it.

    Artifact dicts must include ``platform``, ``filename``, ``sha256``, and
    ``signing`` (``status`` + ``method``). Optional ``arch`` is preserved when
    present and in ``{aarch64, x86_64}``.
    """
    version = version.strip()
    tag = (git_tag or f"v{version}").strip()
    normalized: list[dict[str, Any]] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ManifestError("artifact must be an object")
        entry: dict[str, Any] = {
            "platform": str(raw["platform"]).strip(),
            "filename": str(raw["filename"]).strip(),
            "sha256": str(raw["sha256"]).strip().lower(),
            "signing": {
                "status": str(raw["signing"]["status"]).strip(),
                "method": str(raw["signing"]["method"]).strip(),
            },
        }
        arch = raw.get("arch")
        if arch is not None:
            arch_s = str(arch).strip()
            if arch_s not in {"aarch64", "x86_64"}:
                raise ManifestError(f"unsupported arch: {arch_s!r}")
            entry["arch"] = arch_s
        normalized.append(entry)

    doc: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "product": product,
        "identifier": identifier,
        "version": version,
        "git_tag": tag,
        "git_sha": git_sha.strip().lower(),
        "artifacts": normalized,
    }
    validate_manifest(doc)
    return doc


def canonical_manifest_bytes(data: Mapping[str, Any]) -> bytes:
    """Serialize manifest with frozen key order for data-integrity twins."""
    validate_manifest(data)
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )

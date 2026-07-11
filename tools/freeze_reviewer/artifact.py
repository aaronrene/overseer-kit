"""Freeze artifact parsing and canonical digest bytes (§K5.4 / §K5.7)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.freeze_reviewer.serializer import dump_freeze_mapping, parse_freeze_mapping
from tools.freeze_reviewer.types import ArtifactKind, DeclarationStatus

UTF8_BOM = b"\xef\xbb\xbf"
FENCE_RE = re.compile(
    r"```[ \t]*(yaml|yml)[ \t]*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
STAMP_MARKER = "<!-- overseer:review-stamp -->"


@dataclass(frozen=True)
class ParsedArtifact:
    """Parsed freeze artifact metadata."""

    text: str
    canonical_text: str
    declaration: DeclarationStatus
    kind: ArtifactKind
    freeze_mapping: dict | None
    fence_match: re.Match[str] | None
    rel_path: str


def strip_bom_and_normalize_newlines(data: bytes) -> str:
    """Apply §K4.7 canonical byte rules items 1 and 2."""
    if data.startswith(UTF8_BOM):
        data = data[UTF8_BOM.__len__() :]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("not-utf8") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_artifact_bytes(path: Path) -> str:
    """Read artifact bytes as canonical text or raise ``not-utf8``."""
    return strip_bom_and_normalize_newlines(path.read_bytes())


def _is_valid_declaration(mapping: dict) -> bool:
    if not isinstance(mapping.get("phase"), str):
        return False
    outputs = mapping.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        return False
    for item in outputs:
        if not isinstance(item, dict):
            return False
        if item.get("frozen") is True:
            return True
    return False


def _detect_kind(path: Path, text: str) -> tuple[ArtifactKind, DeclarationStatus, dict | None, re.Match | None]:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            mapping = parse_freeze_mapping(text)
        except ValueError:
            mapping = None
        if mapping and _is_valid_declaration(mapping):
            return "yaml_whole", "present", mapping, None
        return "operator_forced_yaml", "absent", mapping if isinstance(mapping, dict) else None, None

    match = FENCE_RE.search(text)
    if match is not None:
        body = match.group(2)
        try:
            mapping = parse_freeze_mapping(body)
        except ValueError:
            mapping = None
        if mapping and _is_valid_declaration(mapping):
            return "markdown_fence", "present", mapping, match
    return "operator_forced_md", "absent", None, match


def parse_artifact(path: Path, *, rel_path: str) -> ParsedArtifact:
    """Parse artifact text and detect declaration status."""
    text = read_artifact_bytes(path)
    kind, declaration, mapping, fence_match = _detect_kind(path, text)
    return ParsedArtifact(
        text=text,
        canonical_text=text,
        declaration=declaration,
        kind=kind,
        freeze_mapping=mapping,
        fence_match=fence_match,
        rel_path=rel_path,
    )


def _operator_forced_md_prefix(text: str) -> str:
    """Recover pre-stamp prose bytes for operator-forced Markdown."""
    marker_index = text.rfind(STAMP_MARKER)
    if marker_index == -1:
        return text
    prefix = text[:marker_index]
    if prefix.endswith("\n\n"):
        return prefix[:-1]
    return prefix


def _remove_operator_forced_md_suffix(text: str) -> str:
    return _operator_forced_md_prefix(text)


def pre_stamp_canonical_bytes(parsed: ParsedArtifact) -> bytes:
    """Compute pre-stamp canonical form bytes for digest (§K5.7)."""
    if parsed.kind == "markdown_fence" and parsed.freeze_mapping is not None and parsed.fence_match:
        mapping = dict(parsed.freeze_mapping)
        mapping.pop("review_stamp", None)
        serialized = dump_freeze_mapping(mapping)
        start, end = parsed.fence_match.span()
        fence_lang = parsed.fence_match.group(1)
        before = parsed.text[:start]
        after = parsed.text[end:]
        body = f"```{fence_lang}\n{serialized}```"
        return (before + body + after).encode("utf-8")

    if parsed.kind == "yaml_whole" and parsed.freeze_mapping is not None:
        mapping = dict(parsed.freeze_mapping)
        mapping.pop("review_stamp", None)
        return dump_freeze_mapping(mapping).encode("utf-8")

    if parsed.kind == "operator_forced_md":
        return _remove_operator_forced_md_suffix(parsed.text).encode("utf-8")

    if parsed.kind == "operator_forced_yaml":
        if parsed.freeze_mapping is not None:
            mapping = dict(parsed.freeze_mapping)
            mapping.pop("review_stamp", None)
            return dump_freeze_mapping(mapping).encode("utf-8")
        return parsed.text.encode("utf-8")

    return parsed.text.encode("utf-8")


def artifact_digest(parsed: ParsedArtifact) -> str:
    """Return sha256 digest over pre-stamp canonical form."""
    payload = pre_stamp_canonical_bytes(parsed)
    digest_hex = hashlib.sha256(payload).hexdigest()
    return f"sha256:{digest_hex}"


def extract_existing_stamp(parsed: ParsedArtifact) -> dict | None:
    """Return existing review_stamp mapping if present."""
    if parsed.freeze_mapping and isinstance(parsed.freeze_mapping.get("review_stamp"), dict):
        return parsed.freeze_mapping["review_stamp"]
    if parsed.kind == "operator_forced_md":
        marker_index = parsed.text.rfind(STAMP_MARKER)
        if marker_index == -1:
            return None
        tail = parsed.text[marker_index:]
        match = FENCE_RE.search(tail)
        if not match:
            return None
        try:
            mapping = parse_freeze_mapping(match.group(2))
        except ValueError:
            return None
        stamp = mapping.get("review_stamp")
        return stamp if isinstance(stamp, dict) else None
    return None

"""Fail-closed validator for landing assets (K12 + Landing + access clarity)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tools.landing.schema import LandingManifest, load_manifest

# Frozen Auto v1 primary Download CTA (§LAC.2 / §LAC.12).
FROZEN_PRIMARY_DOWNLOAD_HREF = (
    "https://github.com/aaronrene/overseer-kit/releases/download/"
    "v0.1.0/Overseer.Kit_0.1.0_aarch64.dmg"
)

LAC_SECTION_IDS: tuple[str, ...] = (
    "hero",
    "kit-basics",
    "problem",
    "how-it-works",
    "structure",
    "console-access",
    "musehub",
    "next-steps",
    "scenarios",
)

# Public main page must not advertise private/personal product doors or broken MuseHub TLS origin.
MAIN_PAGE_FORBIDDEN_PRODUCTS: tuple[str, ...] = (
    "Knowtation",
    "Scooling",
    "VideoFactory",
    "musehub.ai",
)

DIAGRAM_REL_PATHS: tuple[str, ...] = (
    "assets/diagrams/lanes.svg",
    "assets/diagrams/regimes.svg",
    "assets/diagrams/layers.svg",
    "assets/diagrams/kit-consumer.svg",
)

FORBIDDEN_LANDING_PHRASES: tuple[str, ...] = (
    "Sign up",
    "Create account",
    "executes tasks",
)

# Heuristic patterns — aligned with kit security tests; not exhaustive secret scanning.
SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
)

EXTERNAL_SCRIPT_RE = re.compile(
    r"""<script[^>]+src\s*=\s*["']https?://""",
    re.IGNORECASE,
)

INLINE_EVAL_RE = re.compile(r"\beval\s*\(", re.IGNORECASE)

# Public status-table residue (DONE/TODO/WIP boards on main landing).
STATUS_TABLE_RESIDUE_RE = re.compile(
    r"<table[^>]*>.*?roadmap-public.*?</table>"
    r"|<th[^>]*>\s*Status\s*</th>.*?\b(?:DONE|TODO|WIP)\b",
    re.IGNORECASE | re.DOTALL,
)

MINT_CSRF_OR_SESSION_RE = re.compile(
    r"\bmint\w*.{0,40}\b(?:csrf|session_credential)\b"
    r"|\b(?:csrf|session_credential)\b.{0,40}\bmint\w*",
    re.IGNORECASE,
)

PRIMARY_CTA_HREF_RE = re.compile(
    r"""id=["']cta-download-mac["'][^>]*href=["']([^"']+)["']"""
    r"""|href=["']([^"']+)["'][^>]*id=["']cta-download-mac["']""",
    re.IGNORECASE,
)

GITHUB_RELEASE_DOWNLOAD_RE = re.compile(
    r"^https://github\.com/aaronrene/overseer-kit/releases/download/"
    r"v[0-9][^/]+/[^/]+\.dmg$"
)


@dataclass
class ValidationResult:
    """Outcome of ``validate_landing``."""

    ok: bool
    errors: list[str] = field(default_factory=list)

    def add(self, code: str, detail: str) -> None:
        self.errors.append(f"{code}: {detail}")
        self.ok = False


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_html_sections(html: str, manifest: LandingManifest, result: ValidationResult) -> None:
    for section_id in manifest.section_ids:
        if f'id="{section_id}"' not in html and f"id='{section_id}'" not in html:
            result.add("missing_section", section_id)
    if tuple(manifest.section_ids) != LAC_SECTION_IDS:
        result.add(
            "section_order",
            f"expected {list(LAC_SECTION_IDS)}, got {list(manifest.section_ids)}",
        )


def _check_personas(html: str, manifest: LandingManifest, result: ValidationResult) -> None:
    for persona_id in manifest.persona_ids:
        marker = f'id="persona-{persona_id}"'
        alt = f"id='persona-{persona_id}'"
        if marker not in html and alt not in html:
            result.add("missing_persona", persona_id)
            continue
        idx = html.find(marker) if marker in html else html.find(alt)
        window = html[max(0, idx - 200) : idx + 400]
        if not any(f"badge-{badge}" in window for badge in manifest.status_badges):
            result.add("missing_badge", persona_id)


def _check_secret_leaks(text: str, rel_path: str, result: ValidationResult) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            result.add("secret_leak", f"{rel_path} matches {pattern.pattern}")


def _check_html_security(html: str, rel_path: str, result: ValidationResult) -> None:
    if EXTERNAL_SCRIPT_RE.search(html):
        result.add("external_script", rel_path)
    if INLINE_EVAL_RE.search(html):
        result.add("external_script", f"{rel_path} contains eval()")


def _check_relative_doc_links(html: str, kit_root: Path, html_path: Path, result: ValidationResult) -> None:
    """Resolve href='../foo.md' style links from landing pages (fragments ignored)."""
    for match in re.finditer(r"""href=["'](\.\./[^"'#]+(?:\.md|\.yml)?)(?:#[^"']*)?["']""", html):
        target = (html_path.parent / match.group(1)).resolve()
        try:
            target.relative_to(kit_root.resolve())
        except ValueError:
            result.add("broken_link", f"{html_path.name} -> {match.group(1)} escapes kit root")
            continue
        if not target.exists():
            result.add("broken_link", f"{html_path.name} -> {match.group(1)}")


def _check_lac_index_contract(html: str, landing: Path, result: ValidationResult) -> None:
    """Enforce Download href, diagrams, forbidden copy, and residue strip (§LAC.12)."""
    match = PRIMARY_CTA_HREF_RE.search(html)
    if not match:
        result.add("download_cta", "missing #cta-download-mac primary Download href")
    else:
        href = match.group(1) or match.group(2)
        if href != FROZEN_PRIMARY_DOWNLOAD_HREF:
            result.add("download_cta", f"href {href!r} != frozen {FROZEN_PRIMARY_DOWNLOAD_HREF!r}")
        if not GITHUB_RELEASE_DOWNLOAD_RE.match(href):
            result.add("download_cta", f"href host/path not GitHub releases .dmg: {href}")

    for phrase in FORBIDDEN_LANDING_PHRASES:
        if phrase in html:
            result.add("forbidden_copy", phrase)

    for phrase in MAIN_PAGE_FORBIDDEN_PRODUCTS:
        if phrase in html:
            result.add("forbidden_product", phrase)

    if MINT_CSRF_OR_SESSION_RE.search(html):
        result.add("forbidden_copy", "mint+csrf/session_credential marketing")

    # Prefer GitHub-rendered docs over raw relative .md (file:// / Pages raw).
    for match in re.finditer(r"""href=["'](\.\./[^"']+\.md)["']""", html):
        result.add("raw_md_link", match.group(1))

    if 'id="roadmap-public"' in html or "id='roadmap-public'" in html:
        result.add("residue", "roadmap-public section present on main landing")
    if STATUS_TABLE_RESIDUE_RE.search(html):
        result.add("residue", "DONE/TODO/WIP status table residue on main landing")

    for rel in DIAGRAM_REL_PATHS:
        if rel not in html:
            result.add("missing_diagram_ref", rel)
        diagram_path = landing / rel
        if not diagram_path.is_file():
            result.add("missing_file", f"docs/landing/{rel}")
        else:
            text = _read(diagram_path)
            if "<svg" not in text.lower() or len(text.strip()) < 32:
                result.add("diagram_malformed", rel)

    for path_id in ("path-1", "path-2", "path-3", "console-access"):
        if f'id="{path_id}"' not in html and f"id='{path_id}'" not in html:
            result.add("missing_playbook", path_id)


def validate_landing(kit_root: Path) -> ValidationResult:
    """Validate landing assets under ``kit_root`` (fail-closed)."""
    result = ValidationResult(ok=True)
    landing = kit_root / "docs" / "landing"
    manifest_path = landing / "manifest.yaml"

    if not manifest_path.is_file():
        result.add("manifest_parse", "docs/landing/manifest.yaml missing")
        return result

    try:
        manifest = load_manifest(manifest_path)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        result.add("manifest_parse", str(exc))
        return result

    index_path = landing / "index.html"
    scenarios_path = landing / "scenarios" / "index.html"
    license_path = kit_root / "LICENSE"
    security_path = kit_root / "SECURITY.md"

    for path in (index_path, scenarios_path):
        if not path.is_file():
            result.add("missing_file", str(path.relative_to(kit_root)))
            continue
        html = _read(path)
        _check_secret_leaks(html, str(path.relative_to(kit_root)), result)
        _check_html_security(html, str(path.relative_to(kit_root)), result)
        _check_relative_doc_links(html, kit_root, path, result)

    if index_path.is_file():
        index_html = _read(index_path)
        _check_html_sections(index_html, manifest, result)
        _check_lac_index_contract(index_html, landing, result)

    if scenarios_path.is_file():
        _check_personas(_read(scenarios_path), manifest, result)

    if not license_path.is_file():
        result.add("license", "LICENSE missing")
    else:
        license_text = _read(license_path)
        spdx = (manifest.license or "").strip()
        if spdx == "MIT":
            if "MIT License" not in license_text and "MIT" not in license_text:
                result.add("license", "LICENSE must reference MIT")
            if "Copyright 2026 Overseer Kit contributors" not in license_text:
                result.add("license", "LICENSE missing frozen copyright holder line")
        elif spdx and spdx not in license_text:
            result.add("license", f"manifest expects {manifest.license}")
        elif not spdx:
            result.add("license", "manifest.license missing")

    if not security_path.is_file():
        result.add("security", "SECURITY.md missing")
    else:
        security_text = _read(security_path)
        if "Reporting a vulnerability" not in security_text:
            result.add("security", "SECURITY.md missing disclosure section heading")

    css_path = landing / "assets" / "style.css"
    if not css_path.is_file():
        result.add("missing_file", "docs/landing/assets/style.css")

    return result


def main() -> int:
    """CLI entry: ``python -m tools.landing.validate [KIT_ROOT]``."""
    import sys

    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    outcome = validate_landing(root)
    if not outcome.ok:
        for err in outcome.errors:
            print(err, file=sys.stderr)
        return 1
    print("landing: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

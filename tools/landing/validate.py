"""Fail-closed validator for Track N landing assets (K12)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tools.landing.schema import LandingManifest, load_manifest

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


def validate_landing(kit_root: Path) -> ValidationResult:
    """Validate Track N landing assets under ``kit_root`` (fail-closed)."""
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
        _check_html_sections(_read(index_path), manifest, result)

    if scenarios_path.is_file():
        _check_personas(_read(scenarios_path), manifest, result)

    if not license_path.is_file():
        result.add("license", "LICENSE missing")
    else:
        license_text = _read(license_path)
        if "Apache-2.0" not in license_text and "Apache License" not in license_text:
            result.add("license", "LICENSE must reference Apache-2.0")
        if manifest.license not in license_text and "Apache License" not in license_text:
            result.add("license", f"manifest expects {manifest.license}")

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

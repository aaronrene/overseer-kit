"""Fail-closed docs integrity harness for Track O product contracts (§O0.8 / O3 retarget).

Validates the normative product contract + consumer stubs without rewriting files,
opening network sockets, or walking the filesystem outside declared relative paths.
After O3: Stage 3 points at O2 freeze + ``ok upgrade-regime``; one-click stays blocked
until §O2.6 (no deferred-to-O2 shipping claim).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Declared pack paths (relative to kit root). Harness must not walk beyond these.
CONTRACT_REL = Path("docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md")
SCOOLING_REL = Path("docs/consumers/scooling/OVERSEER-SETUP.md")
KNOWTATION_REL = Path("docs/consumers/knowtation/OVERSEER-SETUP.md")
RUNBOOK_REL = Path("docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md")
O2_FREEZE_REL = Path("docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md")
PACK_RELS: tuple[Path, ...] = (CONTRACT_REL, SCOOLING_REL, KNOWTATION_REL)

STAGE_LABELS: tuple[str, ...] = (
    "Stage 1 — Start",
    "Stage 2 — Work",
    "Stage 3 — Optional GitHub backup",
    "Stage 4 — Optional Knowtation bind",
)

# O3 ceremony markers (replaces O1 "deferred to Thinking O2" keywords).
STAGE3_CEREMONY_KEYWORDS: tuple[str, ...] = (
    "ok upgrade-regime",
    "PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY",
    "one-click",
    "Silent config edit",
)

# Backward-compatible alias for unit tests that still import the O1 name.
DEFERRED_CEREMONY_KEYWORDS = STAGE3_CEREMONY_KEYWORDS

REJECTION_KEYWORDS: tuple[str, ...] = (
    "Require Scooling signup before `ok init`",
    "Require MuseHub for baseline",
    "Silent `vcs.regime` edit",
    "Stage 3 one-click backup before O2",
)

KIT_OWNS_LANGUAGE = "`ok init` / regimes / adapters"
MUSEHUB_OPTIONAL = "no MuseHub-only baseline"
SILENT_REGIME_REJECTION = "Silent `vcs.regime` edit for Stage 3"
OPERATOR_GATED = "operator-gated"

# Forbidden residual O1 shipping deferral language after O3 retarget.
STAGE3_FORBIDDEN_DEFERRED_MARKERS: tuple[str, ...] = (
    "deferred to Thinking O2",
    "deferred to O2",
    "coming soon / operator-assisted",
)

# Required pointers after O3.
STAGE3_REQUIRED_MARKERS: tuple[str, ...] = (
    "ok upgrade-regime",
    "PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY",
)

# Forbidden: absolute machine paths that look like /Users/... or Windows drive roots.
ABS_MACHINE_PATH_RE = re.compile(
    r"(?:/Users/|/home/[a-zA-Z]|[A-Za-z]:\\Users\\)",
)
# Heuristic secret-assignment patterns (aligned with landing validator).
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
)
SECRET_BLOB_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    SECRET_ASSIGNMENT_RE,
)

# Claims that Stage 3 one-click shipping is already done (fail-closed).
ONE_CLICK_SHIPPED_RE = re.compile(
    r"(?i)stage\s*3.*one[- ]click.*(?:shipped|available|live|enabled)",
)

MINIMAL_VALID_CONTRACT = """# Track O — Normie custody product contract

## Stages 1–4 (normie path)

### Stage 1 — Start
Preferred muse-only.

### Stage 2 — Work
Living docs.

### Stage 3 — Optional GitHub backup
Kit ceremony: docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md and ok upgrade-regime.
Products must not ship one-click until §O2.6.
Silent config edit of only vcs.regime is forbidden.

### Stage 4 — Optional Knowtation bind
Knowtation owns vault bytes.

## Boundary table (kit vs products)

| Concern | Overseer Kit | Scooling | Knowtation | MuseHub |
| --- | --- | --- | --- | --- |
| `ok init` / regimes / adapters | **Owns** | Consumes | Consumes | substrate |

**K7 MuseHub-optional guardrail:** no MuseHub-only baseline.

## Rejection table

| Proposal | Verdict |
| --- | --- |
| Require Scooling signup before `ok init` | **Reject** |
| Require MuseHub for baseline | **Reject** (K7) |
| Silent `vcs.regime` edit for Stage 3 without footprint re-seed | **Reject** |
| Product ships Stage 3 one-click backup before O2 kit ceremony freeze | **Reject** |
"""


@dataclass
class ValidationResult:
    """Outcome of ``validate_track_o_pack``."""

    ok: bool
    errors: list[str] = field(default_factory=list)

    def add(self, code: str, detail: str) -> None:
        self.errors.append(f"{code}: {detail}")
        self.ok = False


def _resolve_under_root(kit_root: Path, rel: Path) -> Path | None:
    """Resolve ``rel`` under ``kit_root``; return None on path escape."""
    root = kit_root.resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_stage_labels(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    """Require Stage 1–4 labels (Start / Work / GitHub backup / Knowtation bind)."""
    for stage in STAGE_LABELS:
        if stage not in text:
            result.add("missing_stage", f"{label}: missing {stage!r}")


def check_stage3_ceremony(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    """Require O3 Stage 3 ceremony keywords (O2 freeze + ok upgrade-regime)."""
    for keyword in STAGE3_CEREMONY_KEYWORDS:
        if keyword not in text:
            result.add("missing_stage3", f"{label}: missing {keyword!r}")


def check_deferred_ceremony(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    """Alias for ``check_stage3_ceremony`` (O1 harness name retained for unit imports)."""
    check_stage3_ceremony(text, result, label=label)


def check_rejection_keywords(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    """Require core rejection-table keywords."""
    for keyword in REJECTION_KEYWORDS:
        if keyword not in text:
            result.add("missing_rejection", f"{label}: missing {keyword!r}")


def check_no_abs_machine_paths(text: str, result: ValidationResult, *, label: str) -> None:
    if ABS_MACHINE_PATH_RE.search(text):
        result.add("abs_path", f"{label}: absolute machine path detected")


def check_no_secret_patterns(text: str, result: ValidationResult, *, label: str) -> None:
    for pattern in SECRET_BLOB_PATTERNS:
        if pattern.search(text):
            result.add("secret_leak", f"{label}: matches {pattern.pattern}")


def check_boundary_kit_owns(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    if KIT_OWNS_LANGUAGE not in text:
        result.add("missing_boundary", f"{label}: missing kit-owns language {KIT_OWNS_LANGUAGE!r}")
    if "**Owns**" not in text:
        result.add("missing_boundary", f"{label}: missing **Owns** ownership marker")


def check_not_one_click_shipped(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    if ONE_CLICK_SHIPPED_RE.search(text):
        result.add("one_click_shipped", f"{label}: claims Stage 3 one-click shipped without O2")


def check_stage3_not_deferred_shipping(text: str, result: ValidationResult, *, label: str) -> None:
    """Fail if Stage 3 still uses O1 'deferred to O2' / 'coming soon' shipping language."""
    for marker in STAGE3_FORBIDDEN_DEFERRED_MARKERS:
        if marker in text:
            result.add("stage3_stale_deferral", f"{label}: stale marker {marker!r}")


def check_stage3_points_at_ceremony(text: str, result: ValidationResult, *, label: str) -> None:
    for marker in STAGE3_REQUIRED_MARKERS:
        if marker not in text:
            result.add("stage3_missing_pointer", f"{label}: missing {marker!r}")


def validate_contract_text(text: str, result: ValidationResult, *, label: str = "contract") -> None:
    """Unit-level checks against a product-contract body (fixtures or real doc)."""
    check_stage_labels(text, result, label=label)
    check_stage3_ceremony(text, result, label=label)
    check_rejection_keywords(text, result, label=label)
    check_boundary_kit_owns(text, result, label=label)
    check_not_one_click_shipped(text, result, label=label)
    check_no_abs_machine_paths(text, result, label=label)
    check_no_secret_patterns(text, result, label=label)
    check_stage3_not_deferred_shipping(text, result, label=label)
    check_stage3_points_at_ceremony(text, result, label=label)
    if MUSEHUB_OPTIONAL not in text:
        result.add("missing_k7", f"{label}: missing {MUSEHUB_OPTIONAL!r}")
    if SILENT_REGIME_REJECTION not in text:
        result.add("missing_silent_reject", f"{label}: missing {SILENT_REGIME_REJECTION!r}")


def validate_consumer_stub(
    text: str,
    result: ValidationResult,
    *,
    label: str,
    require_track_o_pointer: bool = True,
) -> None:
    """Checks shared by Scooling + Knowtation consumer stubs."""
    if OPERATOR_GATED not in text:
        result.add("missing_operator_gate", f"{label}: live init must remain operator-gated")
    check_no_abs_machine_paths(text, result, label=label)
    check_no_secret_patterns(text, result, label=label)
    if require_track_o_pointer and "TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT" not in text:
        result.add("missing_track_o_link", f"{label}: missing Track O product-contract pointer")


def validate_track_o_pack(kit_root: Path) -> ValidationResult:
    """Validate the real Track O contract pack under ``kit_root`` (fail-closed).

    Only opens the declared relative paths. Does not rewrite any file.
    """
    result = ValidationResult(ok=True)
    root = kit_root.resolve()

    texts: dict[str, str] = {}
    for rel in PACK_RELS:
        resolved = _resolve_under_root(root, rel)
        if resolved is None:
            result.add("path_escape", f"{rel} escapes kit root")
            continue
        if not resolved.is_file():
            result.add("missing_file", str(rel))
            continue
        try:
            texts[str(rel)] = _read_text(resolved)
        except OSError as exc:
            result.add("read_error", f"{rel}: {exc}")

    contract_key = str(CONTRACT_REL)
    if contract_key in texts:
        validate_contract_text(texts[contract_key], result, label=contract_key)

    scooling_key = str(SCOOLING_REL)
    if scooling_key in texts:
        validate_consumer_stub(texts[scooling_key], result, label=scooling_key)
        body = texts[scooling_key]
        if "optional" not in body.lower() or "scooling" not in body.lower():
            result.add(
                "scooling_mandatory",
                f"{scooling_key}: must keep Scooling optional for kit custody",
            )
        if "never required" not in body.lower() and "optional** entry" not in body and "optional entry" not in body.lower():
            result.add(
                "scooling_mandatory",
                f"{scooling_key}: must state Scooling is optional / not required",
            )
        check_stage3_not_deferred_shipping(body, result, label=scooling_key)
        if "ok upgrade-regime" not in body and "O2" not in body and "STAGE3" not in body.upper():
            # Scooling must point at Stage 3 ceremony / unlock, not claim deferred shipping.
            if "PHASE-TRACK-O-O2" not in body and "upgrade-regime" not in body:
                result.add(
                    "stage3_missing_pointer",
                    f"{scooling_key}: missing Stage 3 ceremony / upgrade-regime pointer",
                )

    knowtation_key = str(KNOWTATION_REL)
    if knowtation_key in texts:
        validate_consumer_stub(texts[knowtation_key], result, label=knowtation_key)
        body = texts[knowtation_key]
        if "Stage 4" not in body:
            result.add("missing_stage4", f"{knowtation_key}: Stage 4 pointer missing")

    runbook = _resolve_under_root(root, RUNBOOK_REL)
    if runbook is None:
        result.add("path_escape", f"{RUNBOOK_REL} escapes kit root")
    elif not runbook.is_file():
        result.add("missing_file", str(RUNBOOK_REL))

    return result


def validate_contract_fixture(text: str) -> ValidationResult:
    """Validate a fixture contract body (integration tests) — same unit checks."""
    result = ValidationResult(ok=True)
    validate_contract_text(text, result, label="fixture")
    return result

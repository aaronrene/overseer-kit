"""Scaffold a side-check freeze artifact for ad-hoc / Thinking honesty gates.

Does **not** open a ``docs.lanes`` entry. Reuses the same §6 freeze declaration
shape that ``ok review --freeze`` already validates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_REVIEWS_DIR = "docs/reviews"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_topic(topic: str) -> str:
    """Return a filesystem-safe lowercase slug for a side-check topic."""
    cleaned = _SLUG_RE.sub("-", topic.strip().lower()).strip("-")
    return cleaned or "side-check"


@dataclass(frozen=True)
class ScaffoldResult:
    """Outcome of creating or reusing a side-check artifact."""

    path: Path
    rel_path: str
    created: bool


def render_side_check_markdown(
    *,
    topic: str,
    phase_id: str,
    scope: str,
    output_path: str,
    date_stamp: str | None = None,
) -> str:
    """Render a minimal §6.1 freeze artifact suitable for ``ok review --freeze``."""
    day = date_stamp or date.today().isoformat()
    scope_body = scope.strip() or (
        "Describe the work under review: intent, files touched, fail-closed rules, "
        "and the seven-tier test plan (unit, integration, e2e, stress, data-integrity, "
        "performance, security)."
    )
    return (
        f"# Side check — {topic}\n"
        f"\n"
        f"**Date:** {day}  \n"
        f"**Kind:** ad-hoc Check OK (not a roadmap lane)  \n"
        f"**Honesty:** same Freeze-Contract + build-verification path as roadmap phases\n"
        f"\n"
        f"## Freeze-contract declaration\n"
        f"\n"
        f"```yaml\n"
        f"phase: {phase_id}\n"
        f"outputs:\n"
        f"  - id: side-check\n"
        f"    path: {output_path}\n"
        f"    frozen: true\n"
        f"frozen_inputs: []\n"
        f"```\n"
        f"\n"
        f"## Scope\n"
        f"\n"
        f"{scope_body}\n"
        f"\n"
        f"## Ground-truth edge\n"
        f"\n"
        f"Downstream Auto / implementation sessions may treat this document as ground truth\n"
        f"for the scoped work without re-deriving the contract. This is **not** a new\n"
        f"``docs.lanes`` baton — promote to a lane only if the concern becomes durable.\n"
        f"\n"
        f"## Test matrix (seven tiers)\n"
        f"\n"
        f"| Tier | Expectation |\n"
        f"| --- | --- |\n"
        f"| unit | Core logic covered |\n"
        f"| integration | CLI / module seams covered |\n"
        f"| e2e | Full operator path covered |\n"
        f"| stress | Bounded / non-pathological under load |\n"
        f"| data-integrity | No silent corruption of declared state |\n"
        f"| performance | Completes within local budget |\n"
        f"| security | No secrets, path escape, or injection surfaces |\n"
        f"\n"
        f"Every freeze-review finding MUST cite **file+line** (SPEC §6).\n"
        f"\n"
        f"## Review record\n"
        f"\n"
        f"| Round | Reviewer | Verdict | Resolution |\n"
        f"| --- | --- | --- | --- |\n"
        f"| — | — | pending | Check-if-OK scaffold created |\n"
        f"\n"
    )


def resolve_artifact_path(
    repo_root: Path,
    *,
    path: str | None = None,
    topic: str | None = None,
    reviews_dir: str = DEFAULT_REVIEWS_DIR,
    today: date | None = None,
) -> Path:
    """Resolve where the side-check artifact should live (absolute under repo_root)."""
    if path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return (repo_root / candidate).resolve()
    day = (today or date.today()).isoformat()
    slug = slugify_topic(topic or "side-check")
    return (repo_root / reviews_dir / f"{day}-{slug}.md").resolve()


def scaffold_side_check(
    repo_root: Path,
    *,
    path: str | None = None,
    topic: str | None = None,
    scope: str = "",
    reviews_dir: str = DEFAULT_REVIEWS_DIR,
    overwrite: bool = False,
    today: date | None = None,
) -> ScaffoldResult:
    """Create a side-check freeze doc if missing; return path + created flag.

    Raises:
        FileExistsError: when the target exists and ``overwrite`` is False and
            the caller asked to force a new scaffold via a missing path that
            already exists — actually we reuse existing files without error.
        ValueError: when resolved path escapes ``repo_root``.
    """
    target = resolve_artifact_path(
        repo_root,
        path=path,
        topic=topic,
        reviews_dir=reviews_dir,
        today=today,
    )
    try:
        target.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError("path-escape") from exc

    rel = target.relative_to(repo_root.resolve()).as_posix()
    if target.is_file() and not overwrite:
        return ScaffoldResult(path=target, rel_path=rel, created=False)

    topic_label = (topic or target.stem).strip() or "side-check"
    phase_id = f"check-ok-{slugify_topic(topic_label)}"
    body = render_side_check_markdown(
        topic=topic_label,
        phase_id=phase_id,
        scope=scope,
        output_path=rel,
        date_stamp=(today or date.today()).isoformat(),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return ScaffoldResult(path=target, rel_path=rel, created=True)

"""Vendored footprint resolution per §K4.5."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig
from adapters.errors import ConfigError
from adapters.templating import render_template
from cli.docs_paths import join_docs_rel
from cli.kit_root import kit_root

MUSE_BRIDGE_WORKFLOW_DEST = "MUSE-BRIDGE-WORKFLOW.md"
MUSE_BRIDGE_DEPLOY_DEST = "scripts/muse-bridge-deploy.sh"
EXECUTABLE_FOOTPRINT_DESTINATIONS = frozenset({MUSE_BRIDGE_DEPLOY_DEST})


@dataclass(frozen=True)
class FootprintFile:
    """One vendored footprint file (destination path, kit source, rendered bytes)."""

    destination: str
    source: str
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")


def _docs_path(config: OverseerConfig, doc_name: str) -> str:
    return join_docs_rel(config.repo.root_relative_docs, doc_name)


def resolve_footprint(config: OverseerConfig, *, kit: Path | None = None) -> list[FootprintFile]:
    """Resolve the full footprint for ``config``; fail closed on destination collisions."""
    root = kit or kit_root()
    files: list[FootprintFile] = []

    template_specs: list[tuple[str, str]] = [
        ("templates/OVERSEER-HANDOVER.template.md", _docs_path(config, config.docs.handover)),
        ("templates/ROADMAP.template.md", _docs_path(config, config.docs.roadmap)),
        (
            "templates/STANDING-DECISIONS.template.md",
            ".overseer/STANDING-DECISIONS.reference.md",
        ),
    ]
    if config.docs.coordination:
        template_specs.append(
            (
                "templates/CROSS-REPO-COORDINATION.template.md",
                _docs_path(config, config.docs.coordination),
            )
        )

    if config.vcs.regime == "muse+git-mirror":
        template_specs.extend(
            [
                (
                    "templates/MUSE-BRIDGE-WORKFLOW.template.md",
                    MUSE_BRIDGE_WORKFLOW_DEST,
                ),
                (
                    "templates/scripts/muse-bridge-deploy.sh.template",
                    MUSE_BRIDGE_DEPLOY_DEST,
                ),
            ]
        )

    destinations: set[str] = set()
    for source_rel, dest in template_specs:
        if dest in destinations:
            raise ConfigError(
                f"duplicate footprint destination {dest!r} (config collision)",
                None,
            )
        destinations.add(dest)
        template_path = root / source_rel
        rendered = render_template(template_path, config)
        files.append(
            FootprintFile(
                destination=dest,
                source=source_rel,
                content=rendered.encode("utf-8"),
            )
        )

    policy_dir = root / "policy"
    for src in sorted(policy_dir.glob("*.yaml")):
        dest = f".overseer/policy/{src.name}"
        if dest in destinations:
            raise ConfigError(f"duplicate footprint destination {dest!r}", None)
        destinations.add(dest)
        files.append(
            FootprintFile(
                destination=dest,
                source=f"policy/{src.name}",
                content=src.read_bytes(),
            )
        )

    rules_dir = root / "cursor" / "rules"
    if rules_dir.is_dir():
        for src in sorted(rules_dir.iterdir()):
            if not src.is_file():
                continue
            dest = f".cursor/rules/{src.name}"
            if dest in destinations:
                raise ConfigError(f"duplicate footprint destination {dest!r}", None)
            destinations.add(dest)
            files.append(
                FootprintFile(
                    destination=dest,
                    source=f"cursor/rules/{src.name}",
                    content=src.read_bytes(),
                )
            )

    skills_dir = root / "cursor" / "skills"
    if skills_dir.is_dir():
        for src in sorted(skills_dir.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(skills_dir)
            content = src.read_bytes()
            source = f"cursor/skills/{rel.as_posix()}"
            # Cursor Agent Skills + Claude Code project skills (same bytes).
            for dest_prefix in (".cursor/skills", ".claude/skills"):
                dest = f"{dest_prefix}/{rel.as_posix()}"
                if dest in destinations:
                    raise ConfigError(f"duplicate footprint destination {dest!r}", None)
                destinations.add(dest)
                files.append(
                    FootprintFile(
                        destination=dest,
                        source=source,
                        content=content,
                    )
                )

    files.sort(key=lambda item: item.destination)
    return files


def footprint_tuples(files: list[FootprintFile]) -> list[tuple[str, str, bytes]]:
    """Return ``(destination, source, bytes)`` tuples for lock building."""
    return [(f.destination, f.source, f.content) for f in files]

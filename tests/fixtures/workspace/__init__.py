"""Fixture builders for multi-repo workspace lanes tests (§MR.9–§MR.10)."""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.workspace.next_extract import tip_hash_hex


def _member_config(
    *,
    name: str,
    regime: str,
    handover: str,
    roadmap: str,
    handover_title: str,
    roadmap_title: str,
    constellation_id: str | None = None,
    product_order_root: str | None = None,
    manifest: str | None = None,
) -> dict:
    if regime == "muse-only":
        vcs = {
            "regime": "muse-only",
            "canonical": "muse",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {"staging_remote": None, "main_branch": "main"},
        }
    elif regime == "muse+git-mirror":
        vcs = {
            "regime": "muse+git-mirror",
            "canonical": "muse",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": "muse-mirror",
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {"staging_remote": "staging", "main_branch": "main"},
        }
    else:
        vcs = {
            "regime": "git-only",
            "canonical": "git",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {"staging_remote": None, "main_branch": None},
        }

    cfg: dict = {
        "overseer_config_version": 1,
        "repo": {"name": name, "root_relative_docs": "docs"},
        "vcs": vcs,
        "docs": {
            "handover": handover,
            "roadmap": roadmap,
            "coordination": None,
            "standing_decisions": roadmap,
            "handover_title": handover_title,
            "roadmap_title": roadmap_title,
        },
        "thresholds": {"realign_max_commits": 50, "drift_warn_only": True},
        "freeze_contract": {
            "enabled": True,
            "reviewer": {
                "mode": "agent",
                "model": "thinking-high",
                "provider": "local",
                "fallback": "human",
            },
            "human_escalation": ["security"],
        },
    }
    if constellation_id is not None:
        ws: dict = {"constellation_id": constellation_id}
        if product_order_root is not None:
            ws["product_order_root"] = product_order_root
        if manifest is not None:
            ws["manifest"] = manifest
        cfg["workspace"] = ws
    return cfg


def primary_fence(
    *,
    step: str,
    model: str,
    repo: str,
    branch: str = "feat/test",
    authority: str = "authoritative",
) -> str:
    return (
        f"Phase {step} — test.\n"
        f"\n"
        f"Model: {model}\n"
        f"Repo: {repo}\n"
        f"Branch: {branch}\n"
        f"Step: {step}\n"
        f"Authority: {authority}\n"
    )


def write_primary_handover(
    path: Path,
    *,
    title: str,
    step: str,
    model: str,
    repo: str,
    lane: str = "product",
    extra_blocks: str = "",
) -> str:
    """Write product_order PRIMARY handover; return tip_hash of paste fence."""
    fence = primary_fence(step=step, model=model, repo=repo)
    digest = tip_hash_hex(fence)
    text = (
        f"# {title}\n"
        f"\n"
        f"<!-- overseer:next role=primary lane={lane} status=live -->\n"
        f"## NEXT SESSION — {step} (PRIMARY)\n"
        f"\n"
        f"**Model:** {model}\n"
        f"\n"
        f"### THE ONE NEXT STEP — **Model: {model}**\n"
        f"\n"
        f"| | |\n"
        f"| --- | --- |\n"
        f"| **ID** | **{step}** |\n"
        f"| **Branch** | `feat/test` |\n"
        f"| **Repo** | **{repo}** |\n"
        f"\n"
        f"### Paste-ready prompt — {step}\n"
        f"\n"
        f"```\n"
        f"{fence}"
        f"```\n"
        f"\n"
        f"{extra_blocks}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return digest


def write_relay_handover(
    path: Path,
    *,
    title: str,
    step: str,
    model: str,
    product_order: str,
    tip_hash: str,
    mode: str = "relay",
    ownership_primary: bool = False,
    ownership_step: str = "SEC-1",
    stale: bool = False,
) -> None:
    """Write ownership/enrichment board with RELAY or PRODUCT RELAY tip."""
    tip_step = "STALE-OLD" if stale else step
    tip_model = "Thinking" if stale else model
    tip_digest = "0" * 64 if stale else tip_hash
    redirect = (
        f"Model: {tip_model}\n"
        f"Repo: open product_order {product_order}\n"
        f"Branch: unknown\n"
        f"Step: {tip_step}\n"
        f"Authority: relay\n"
        f"Open product_order handover for authoritative paste.\n"
    )
    if ownership_primary and mode == "product_relay":
        text = (
            f"# {title}\n"
            f"\n"
            f"<!-- overseer:next role=primary lane=product status=live -->\n"
            f"## NEXT SESSION — {ownership_step} ownership work (PRIMARY)\n"
            f"\n"
            f"**Model:** Auto\n"
            f"\n"
            f"### Paste-ready prompt — {ownership_step}\n"
            f"\n"
            f"```\n"
            f"Model: Auto\n"
            f"Repo: ownership\n"
            f"Branch: feat/own\n"
            f"Step: {ownership_step}\n"
            f"Authority: authoritative\n"
            f"```\n"
            f"\n"
            f"<!-- overseer:next role=product_relay lane=product status=live "
            f"product_order={product_order} tip_hash=sha256:{tip_digest} -->\n"
            f"## PRODUCT RELAY — {product_order} {tip_step} {tip_model}\n"
            f"\n"
            f"```\n"
            f"{redirect}"
            f"```\n"
        )
    elif mode == "relay":
        text = (
            f"# {title}\n"
            f"\n"
            f"<!-- overseer:next role=relay lane=product status=live "
            f"product_order={product_order} tip_hash=sha256:{tip_digest} -->\n"
            f"## NEXT SESSION — Product tip (RELAY → {product_order} {tip_step} {tip_model})\n"
            f"\n"
            f"**Model:** {tip_model}\n"
            f"\n"
            f"### Paste-ready prompt — relay\n"
            f"\n"
            f"```\n"
            f"{redirect}"
            f"```\n"
        )
    else:
        raise ValueError(f"unsupported mode {mode}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_two_repo_constellation(
    root: Path,
    *,
    stale_relay: bool = False,
    bare_names_on_relay: bool = False,
    with_brain: bool = False,
    with_musehub: bool = False,
    with_lane_tip: bool = False,
    ownership_product_relay: bool = False,
    missing_product_relay: bool = False,
    constellation_id: str = "fixture-stack",
) -> dict:
    """Create product_order + ownership (+ optional) fixture constellation.

    Returns paths dict for tests.
    """
    scooling = root / "scooling"
    knowtation = root / "knowtation"
    for path in (scooling, knowtation):
        (path / ".overseer").mkdir(parents=True)
        (path / "docs").mkdir(parents=True)

    scooling_ho = "SCOOLING-OVERSEER-HANDOVER.md"
    scooling_rm = "SCOOLING-ROADMAP.md"
    if bare_names_on_relay:
        know_ho = "OVERSEER-HANDOVER.md"
        know_rm = "ROADMAP.md"
        know_title = "Overseer Handover"
    else:
        know_ho = "KNOWTATION-OVERSEER-HANDOVER.md"
        know_rm = "KNOWTATION-ROADMAP.md"
        know_title = "Knowtation Overseer Handover"

    tip_hash = write_primary_handover(
        scooling / "docs" / scooling_ho,
        title="Scooling Overseer Handover",
        step="L-SEAMb",
        model="Auto",
        repo=str(scooling),
    )
    lane_extra = ""
    if with_lane_tip:
        lane_extra = (
            "<!-- overseer:next role=lane_tip lane=security status=live -->\n"
            "## LANE TIP — Security harden (LANE: security)\n"
            "\n"
            "### Paste-ready prompt — security\n"
            "\n"
            "```\n"
            "Model: Thinking\n"
            "Repo: scooling\n"
            "Branch: feat/sec\n"
            "Step: SEC-LANE\n"
            "Authority: lane_tip\n"
            "```\n"
        )
        # Append lane tip to scooling handover
        path = scooling / "docs" / scooling_ho
        path.write_text(path.read_text(encoding="utf-8") + "\n" + lane_extra, encoding="utf-8")

    (scooling / "docs" / scooling_rm).write_text("# Scooling Roadmap\n", encoding="utf-8")
    (knowtation / "docs" / know_rm).write_text("# Knowtation Roadmap\n", encoding="utf-8")

    if missing_product_relay:
        # Ownership PRIMARY only — no product tip
        (knowtation / "docs" / know_ho).write_text(
            (
                "# Knowtation\n"
                "\n"
                "<!-- overseer:next role=primary lane=product status=live -->\n"
                "## NEXT SESSION — SEC-9 ownership (PRIMARY)\n"
                "\n"
                "### Paste-ready prompt\n"
                "\n"
                "```\n"
                "Model: Auto\n"
                "Repo: knowtation\n"
                "Branch: feat/sec\n"
                "Step: SEC-9\n"
                "Authority: authoritative\n"
                "```\n"
            ),
            encoding="utf-8",
        )
    elif ownership_product_relay:
        write_relay_handover(
            knowtation / "docs" / know_ho,
            title=know_title,
            step="L-SEAMb",
            model="Auto",
            product_order="scooling",
            tip_hash=tip_hash,
            mode="product_relay",
            ownership_primary=True,
            stale=stale_relay,
        )
    else:
        write_relay_handover(
            knowtation / "docs" / know_ho,
            title=know_title,
            step="L-SEAMb",
            model="Auto",
            product_order="scooling",
            tip_hash=tip_hash,
            mode="relay",
            stale=stale_relay,
        )

    members = [
        {
            "id": "scooling",
            "role": "product_order",
            "root": str(scooling),
            "regime": "git-only",
            "required": True,
            "relay": False,
        },
        {
            "id": "knowtation",
            "role": "ownership",
            "root": str(knowtation),
            "regime": "git-only",
            "required": True,
            "relay": True,
        },
    ]
    lanes = [
        {"id": "product", "primary": True, "owner_member": "scooling"},
        {"id": "security", "primary": False, "owner_member": "knowtation"},
    ]

    musehub = None
    if with_musehub:
        musehub = root / "musehub"
        (musehub / ".overseer").mkdir(parents=True)
        (musehub / "docs").mkdir(parents=True)
        (musehub / "docs" / "MUSEHUB-OVERSEER-HANDOVER.md").write_text(
            "# MuseHub\n", encoding="utf-8"
        )
        (musehub / "docs" / "MUSEHUB-ROADMAP.md").write_text("# MuseHub Roadmap\n", encoding="utf-8")
        mh_cfg = _member_config(
            name="musehub",
            regime="muse-only",
            handover="MUSEHUB-OVERSEER-HANDOVER.md",
            roadmap="MUSEHUB-ROADMAP.md",
            handover_title="MuseHub Overseer Handover",
            roadmap_title="MuseHub Roadmap",
            constellation_id=constellation_id,
            product_order_root=str(scooling),
        )
        (musehub / ".overseer" / "config.yaml").write_text(
            yaml.safe_dump(mh_cfg, sort_keys=False), encoding="utf-8"
        )
        members.append(
            {
                "id": "musehub",
                "role": "enrichment",
                "root": str(musehub),
                "regime": "muse-only",
                "required": False,
                "relay": False,
            }
        )

    if with_brain:
        members.append(
            {
                "id": "brain",
                "role": "edge",
                "root": "${BRAIN_ROOT}",
                "regime": None,
                "required": False,
                "relay": False,
            }
        )

    manifest = {
        "overseer_workspace_version": 1,
        "id": constellation_id,
        "product_order_member": "scooling",
        "strict_markers": True,
        "strict_board_names": True,
        "members": members,
        "lanes": lanes,
    }
    manifest_path = scooling / ".overseer" / "workspace.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    scooling_cfg = _member_config(
        name="scooling",
        regime="git-only",
        handover=scooling_ho,
        roadmap=scooling_rm,
        handover_title="Scooling Overseer Handover",
        roadmap_title="Scooling Roadmap",
        constellation_id=constellation_id,
        manifest=str(manifest_path),
    )
    know_cfg = _member_config(
        name="knowtation",
        regime="git-only",
        handover=know_ho,
        roadmap=know_rm,
        handover_title=know_title,
        roadmap_title="Knowtation Roadmap",
        constellation_id=constellation_id,
        product_order_root=str(scooling),
    )
    (scooling / ".overseer" / "config.yaml").write_text(
        yaml.safe_dump(scooling_cfg, sort_keys=False), encoding="utf-8"
    )
    (knowtation / ".overseer" / "config.yaml").write_text(
        yaml.safe_dump(know_cfg, sort_keys=False), encoding="utf-8"
    )

    return {
        "scooling": scooling,
        "knowtation": knowtation,
        "musehub": musehub,
        "manifest": manifest_path,
        "tip_hash": tip_hash,
        "constellation_id": constellation_id,
        "scooling_handover": scooling / "docs" / scooling_ho,
        "knowtation_handover": knowtation / "docs" / know_ho,
    }

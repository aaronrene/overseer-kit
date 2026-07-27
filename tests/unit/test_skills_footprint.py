"""Unit tests — overseer skills ship in vendored footprint."""

from __future__ import annotations

from cli.footprint import resolve_footprint


def test_footprint_includes_review_loop_skills(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert ".cursor/skills/freeze-review-loop/SKILL.md" in dests
    assert ".cursor/skills/build-verification-review/SKILL.md" in dests
    assert ".claude/skills/freeze-review-loop/SKILL.md" in dests
    assert ".claude/skills/build-verification-review/SKILL.md" in dests


def test_review_loop_skill_documents_bounded_loop(git_only_config) -> None:
    files = {f.destination: f.text for f in resolve_footprint(git_only_config)}
    loop = files[".cursor/skills/freeze-review-loop/SKILL.md"]
    assert "MAX_ROUNDS" in loop
    assert "Not automatic by default" in loop
    assert "while ROUND" in loop


def test_footprint_includes_build_verification_rule(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert ".cursor/rules/build-verification-required.mdc" in dests


def test_footprint_includes_orchestrator_rule(git_only_config) -> None:
    files = {f.destination: f.text for f in resolve_footprint(git_only_config)}
    assert ".cursor/rules/orchestrator.mdc" in files
    text = files[".cursor/rules/orchestrator.mdc"]
    assert "alwaysApply: true" in text
    assert "RULE #8" in text
    assert "ok init" in text
    assert "Paste-ready prompt" in text
    assert "/freeze-review-loop" in text
    assert "/build-verification-review" in text
    assert "{{docs.roadmap_path}}" in text
    assert "{{docs.handover_path}}" in text


def test_build_verification_skill_documents_honesty_gate(git_only_config) -> None:
    files = {f.destination: f.text for f in resolve_footprint(git_only_config)}
    verify = files[".cursor/skills/build-verification-review/SKILL.md"]
    assert "honesty gate" in verify.lower()
    assert "{step}b" in verify
    assert "thinking-high" in verify
    assert "Mandatory" in verify


def test_footprint_includes_workspace_authority_and_skill(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert ".cursor/rules/workspace-authority.mdc" in dests
    assert ".cursor/skills/workspace-status/SKILL.md" in dests
    assert ".claude/skills/workspace-status/SKILL.md" in dests


def test_rendered_templates_include_build_verification_in_dod(git_only_config) -> None:
    from adapters.templating import render_template
    from cli.kit_root import kit_root

    handover = render_template(kit_root() / "templates/OVERSEER-HANDOVER.template.md", git_only_config)
    roadmap = render_template(kit_root() / "templates/ROADMAP.template.md", git_only_config)
    assert "build-verification-review" in handover
    assert "Build verification" in roadmap

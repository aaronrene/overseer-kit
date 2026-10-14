"""Bound Cursor event adapters and instruction-triggered host bookends.

This module supplies transport validation and presentation only. The dispatcher
uses the same canonical NEXT reader and final context recheck as ``ok next``.
No event may publish a handoff or discover another launcher/runtime.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex

from cli.v1_io import LIMIT, Refusal, confined, read


EVENT_PATHS = {
    "sessionStart": ".cursor/hooks/session-start-next.sh",
    "stop": ".cursor/hooks/session-end-closeout.sh",
}


def hook_script(root: Path, event: str | None = None) -> bytes:
    """Generate one root-bound adapter; retain the B script form for upgrades."""
    if event is not None and event not in EVENT_PATHS:
        raise Refusal("hook_event_invalid")
    suffix = "" if event is None else " --event " + shlex.quote(event)
    return ("#!/bin/sh\nset -eu\nexec "
            + shlex.quote(str(root / ".overseer/bin/ok"))
            + ' hook --hook-path "$0"' + suffix + "\n").encode()


def cursor_assets(root: Path) -> dict[str, bytes]:
    """Only explicit init/sync --hooks installs these assets in the chosen root."""
    result = {relative: hook_script(root, event)
              for event, relative in EVENT_PATHS.items()}
    result[".cursor/hooks.json"] = (json.dumps({"version": 1, "hooks": {
        event: [{"command": shlex.quote(str(root / relative)),
                 "failClosed": False, **({"loop_limit": 1} if event == "stop" else {})}]
        for event, relative in EVENT_PATHS.items()
    }}, indent=2) + "\n").encode()
    return result


def instruction_assets(root: Path) -> dict[str, bytes]:
    command = shlex.quote(str(root / ".overseer/bin/ok")) + " -C " + shlex.quote(str(root)) + " next"
    return {".overseer/instructions/bookends.md": (
        "# Instruction-triggered NEXT bookends\n\n"
        "These instructions apply when explicitly adopted by the repository's "
        "Claude Code skill or Codex AGENTS instructions. They do not register "
        "native lifecycle hooks or prove host delivery.\n\n"
        "At session entry, before acting, run the bound command below. At "
        "closeout, run it again after the accepted handoff and final local "
        "closing commit. Display its validated paste-ready action verbatim; "
        "label this an instruction-triggered bookend.\n\n"
        "```sh\n" + command + "\n```\n\n"
        "If it refuses, report the refusal and stop the proposed action. Do not "
        "guess a task, use another runtime, scrape HANDOVER/ROADMAP, or run "
        "governance-sync to create a prompt. Only an explicit accepted "
        "next-write publication may change canonical docs/NEXT.md.\n"
    ).encode()}


def read_event(stream) -> bytes:
    """Bound stdin regardless of whether an engine test supplies a text stream."""
    source = getattr(stream, "buffer", stream)
    raw = source.read(LIMIT + 1)
    if isinstance(raw, str):
        try:
            raw = raw.encode("utf-8")
        except UnicodeError:
            raise Refusal("hook_input_invalid") from None
    if not isinstance(raw, bytes):
        raise Refusal("hook_input_invalid")
    if len(raw) > LIMIT:
        raise Refusal("hook_input_too_large")
    return raw


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal("hook_duplicate_key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(value)


def _physical_root(value, root):
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise Refusal("hook_workspace_mismatch")
    try:
        if Path(value).resolve(strict=True) != root:
            raise Refusal("hook_workspace_mismatch")
    except (OSError, ValueError, RuntimeError):
        raise Refusal("hook_workspace_mismatch") from None


def validate_event(root: Path, config: dict, args, raw: bytes) -> str:
    """Validate an event after the dispatcher's repository/runtime validation.

    Empty stdin and {} preserve B's native-event compatibility. Optional event
    root/lane fields become assertions, never selectors or fallback discovery.
    Unrelated host metadata is ignored; all binding fields we accept are strict.
    """
    if not all(getattr(args, field, None) for field in ("bound_id", "bound_root", "binding_path")):
        raise Refusal("hook_requires_bound_launcher")
    path = Path(os.path.abspath(args.hook_path))
    events = [event for event, relative in EVENT_PATHS.items() if path == root / relative]
    if len(events) != 1:
        raise Refusal("hook_location_mismatch")
    event = events[0]
    relative = EVENT_PATHS[event]
    confined(root, relative)
    requested = getattr(args, "event", None)
    if requested is not None and requested != event:
        raise Refusal("hook_event_mismatch")
    # A copied or edited hook must not acquire authority just from its filename.
    actual = read(root, relative)
    allowed = {hook_script(root, event)}
    if requested is None:
        allowed.add(hook_script(root))
    if actual not in allowed:
        raise Refusal("hook_binding_mismatch")
    if not isinstance(raw, bytes):
        raise Refusal("hook_input_invalid")
    if len(raw) > LIMIT:
        raise Refusal("hook_input_too_large")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant) if raw.strip() else {}
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise Refusal("hook_input_invalid") from None
    if not isinstance(payload, dict):
        raise Refusal("hook_input_invalid")
    if "workspace_roots" in payload:
        roots = payload["workspace_roots"]
        if not isinstance(roots, list) or len(roots) > 1:
            raise Refusal("hook_workspace_mismatch")
        for selected in roots:
            _physical_root(selected, root)
    for field in ("workspace_root", "repo_root"):
        if field in payload:
            _physical_root(payload[field], root)
    if "lane" in payload and payload["lane"] != config["context"]["lane"]:
        raise Refusal("hook_lane_mismatch")
    if "repo_id" in payload and payload["repo_id"] != config["repo"]["id"]:
        raise Refusal("hook_identity_mismatch")
    for field in ("hook_event_name", "event_name", "event"):
        if field in payload and payload[field] != event:
            raise Refusal("hook_event_mismatch")
    return event


def hook_response(output: str, event: str) -> dict[str, str]:
    if event not in EVENT_PATHS:
        raise Refusal("hook_event_invalid")
    # Preserve P/B's observed Cursor payload keys without claiming delivery on
    # any untested client version. No transport wrapper changes canonical text.
    return {"additional_context": output, "followup_message": output}

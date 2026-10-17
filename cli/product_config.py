"""Lossless configuration normalization for the bound product dispatcher.

Only this module classifies serialized product configurations.  The retained
adapter validator supplies the engine view from the already normalized mapping;
it does not read another file.  Normalization never writes, activates authority,
refreshes an existing runtime digest, or follows an external Muse working dir.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any
import uuid

import yaml

from adapters import config as legacy
from adapters.errors import ConfigError
from cli.v1_io import Refusal
from tools.hosted_dashboard.config import parse_hosted_dashboard_config

TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
OPTIONAL = frozenset({"checkpoints", "honesty", "modules", "extensions",
    "governance_gates", "model_routing", "cost_awareness", "session_bookends",
    "workspace", "hosted_dashboard", "close_ritual"})
CORE = frozenset({"repo", "vcs", "docs", "thresholds", "freeze_contract"})
DOC_KEYS = frozenset({"handover", "roadmap", "coordination", "standing_decisions",
    "handover_title", "roadmap_title", "default_lane", "lanes", "canonical_next"})
LANE_KEYS = frozenset({"handover", "roadmap", "handover_title", "roadmap_title", "repo_id"})


class UniqueLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise Refusal("duplicate_or_invalid_key")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def decode(data: bytes) -> dict:
    try:
        value = yaml.load(data.decode("utf-8"), Loader=UniqueLoader)
    except (UnicodeError, yaml.YAMLError, ValueError, TypeError, RecursionError) as exc:
        raise Refusal("malformed_config") from exc
    if not isinstance(value, dict):
        raise Refusal("config_root_must_be_mapping")
    # Recursive YAML anchors are not a finite configuration/field map.
    def finite(item, ancestors):
        if isinstance(item, (dict, list)):
            if id(item) in ancestors:
                raise Refusal("recursive_config_alias")
            next_ancestors = ancestors | {id(item)}
            for child in (item.values() if isinstance(item, dict) else item):
                finite(child, next_ancestors)
    try:
        finite(value, set())
    except RecursionError as exc:
        raise Refusal("config_nesting_invalid") from exc
    return value


def _mapping(value, allowed, field, required=()):
    if not isinstance(value, dict):
        raise Refusal(f"config_mapping_required: {field}")
    unknown = set(value) - set(allowed)
    if unknown:
        raise Refusal(f"unknown_unmapped_settings: {field}: {','.join(sorted(unknown))}")
    if not set(required).issubset(value):
        raise Refusal(f"config_fields_missing: {field}: {','.join(sorted(set(required) - set(value)))}")
    return value


def _label(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 200 or any(ord(c) < 32 for c in value):
        raise Refusal("config_label_invalid: " + field)
    return value


def _token(value, field):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise Refusal("config_identifier_invalid: " + field)
    return value


def _identity(value):
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise Refusal("repo_identity_invalid") from None


def _relative(value, field, root, *, directory=False):
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value:
        raise Refusal("config_path_invalid: " + field)
    if any(ord(c) < 32 for c in value):
        raise Refusal("config_path_invalid: " + field)
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or (not directory and value == "."):
        raise Refusal("config_path_invalid: " + field)
    if value != "." and (str(path) != value or "." in value.split("/")):
        raise Refusal("config_path_alias: " + field)
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise Refusal("config_path_symlink: " + field)
    return path


def _runtime(value, field="runtime"):
    _mapping(value, {"root", "version", "sha256"}, field, {"root", "version", "sha256"})
    for key in ("root", "version", "sha256"):
        _label(value[key], field + "." + key)
    if not Path(value["root"]).is_absolute() or str(Path(value["root"]).resolve()) != value["root"]:
        raise Refusal("runtime_root_not_physical")
    if not SHA256.fullmatch(value["sha256"]):
        raise Refusal("runtime_digest_invalid")


def _default_full(authority):
    return {"vcs": {"regime": "git-only" if authority == "git" else "muse-only",
        "canonical": authority,
        "git": {"remote": "origin", "main_branch": "main", "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}"},
        "muse": {"staging_remote": None, "main_branch": None if authority == "git" else "main",
                 "working_dir": None}},
        "docs": {"handover": "OVERSEER-HANDOVER.md", "roadmap": "ROADMAP.md",
                 "coordination": None, "standing_decisions": "ROADMAP.md",
                 "handover_title": "Overseer Handover", "roadmap_title": "Roadmap"},
        "thresholds": {"realign_max_commits": 50, "drift_warn_only": True},
        "freeze_contract": {"enabled": True, "reviewer": "agent", "human_escalation": ["security"]}}


def _validate_shapes(data):
    _mapping(data["repo"], {"name", "id", "root", "root_relative_docs"}, "repo", {"name", "root_relative_docs"})
    _mapping(data["vcs"], {"regime", "canonical", "git", "muse"}, "vcs", {"regime", "canonical", "git", "muse"})
    _mapping(data["vcs"]["git"], {"remote", "main_branch", "mirror_branch", "feature_branch_pattern"}, "vcs.git")
    _mapping(data["vcs"]["muse"], {"staging_remote", "main_branch", "working_dir", "binding"}, "vcs.muse")
    docs = _mapping(data["docs"], DOC_KEYS, "docs", {"handover", "roadmap", "standing_decisions"})
    if docs.get("lanes") is not None:
        if not isinstance(docs["lanes"], dict) or not docs["lanes"]:
            raise Refusal("config_lanes_invalid")
        for lane, lane_docs in docs["lanes"].items():
            _token(lane, "docs.lanes")
            _mapping(lane_docs, LANE_KEYS, "docs.lanes." + lane, {"handover", "roadmap"})
    _mapping(data["thresholds"], {"realign_max_commits", "drift_warn_only"}, "thresholds")
    if type(data["thresholds"].get("realign_max_commits")) is not int:
        raise Refusal("config_integer_required: thresholds.realign_max_commits")
    freeze = _mapping(data["freeze_contract"], {"enabled", "reviewer", "human_escalation"}, "freeze_contract")
    if isinstance(freeze.get("reviewer"), dict):
        reviewer = _mapping(freeze["reviewer"], legacy.REVIEWER_MAPPING_KEYS, "freeze_contract.reviewer")
        # The historic human-mode parser substitutes defaults for malformed
        # optional values. A migration must expose invalid settings, never make
        # a different engine selection from the retained serialized value.
        if "model" in reviewer:
            _label(reviewer["model"], "freeze_contract.reviewer.model")
        if "provider" in reviewer and reviewer["provider"] not in legacy.REVIEWER_PROVIDERS:
            raise Refusal("config_reviewer_provider_invalid")
        if "fallback" in reviewer and reviewer["fallback"] not in legacy.REVIEWER_FALLBACK:
            raise Refusal("config_reviewer_fallback_invalid")
    hosted = data.get("hosted_dashboard")
    if isinstance(hosted, dict):
        for field in ("enumeration_cap", "max_doc_bytes"):
            if field in hosted and type(hosted[field]) is not int:
                raise Refusal("config_integer_required: hosted_dashboard." + field)
        if "musehub_hosts" in hosted and (not isinstance(hosted["musehub_hosts"], list)
                or any(not isinstance(host, str) for host in hosted["musehub_hosts"])):
            raise Refusal("config_hosted_hosts_must_be_strings")
    extensions = data.get("extensions")
    if isinstance(extensions, list):
        for index, extension in enumerate(extensions):
            if isinstance(extension, dict) and type(extension.get("schema_version")) is not int:
                raise Refusal(f"config_integer_required: extensions[{index}].schema_version")
    # The preserved validators cover every nested optional mapping.  They also
    # enforce agreement between section and modules enable flags.


def _adapter_view(data):
    view = {key: deepcopy(value) for key, value in data.items() if key in CORE | OPTIONAL}
    view["overseer_config_version"] = 1
    view["repo"] = {key: view["repo"][key] for key in ("name", "root_relative_docs")}
    view["vcs"]["muse"].pop("binding", None)
    if data['vcs']['regime'] == 'git-only':
        # Full schema retains inactive source settings across explicit adoption.
        # The historical Git adapter must not interpret them as active Muse.
        for field in ('staging_remote', 'main_branch', 'working_dir'):
            value = view['vcs']['muse'].get(field)
            if value is not None and not isinstance(value, str):
                raise Refusal('config_invalid: inactive Muse setting must be a string or null')
            view['vcs']['muse'][field] = None
    view["docs"].pop("canonical_next", None)
    for lane in (view["docs"].get("lanes") or {}).values():
        lane.pop("repo_id", None)
    try:
        return legacy._validate_config(view, "<normalized-config>")
    except (ConfigError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise Refusal("config_invalid: " + str(exc)) from exc


def _validate_paths(data, root):
    docs = data["docs"]
    base = _relative(data["repo"]["root_relative_docs"], "repo.root_relative_docs", root, directory=True)
    occupied = {}
    for lane, lane_docs in docs["lanes"].items():
        for field in ("handover", "roadmap"):
            relative = _relative(lane_docs[field], f"docs.lanes.{lane}.{field}", root / base)
            path = (base / relative).as_posix()
            if path == "docs/NEXT.md" or path in occupied:
                raise Refusal("config_document_alias: " + path)
            occupied[path] = (lane, field)
    for field in ("handover", "roadmap", "coordination", "standing_decisions"):
        if docs.get(field) is not None:
            _relative(docs[field], "docs." + field, root / base)
            if (base / docs[field]).as_posix() == "docs/NEXT.md":
                raise Refusal("config_competing_next_document")
    paths = {"checkpoints": ("policy", "active_manifest", "progress", "orchestrator"),
             "honesty": ("ledger", "roles_file", "ci_reexecutor"),
             "model_routing": ("policy",), "close_ritual": ("consumer_verify_script",),
             "workspace": ("manifest",)}
    for section, fields in paths.items():
        for field in fields:
            value = (data.get(section) or {}).get(field)
            if value is not None:
                _relative(value, section + "." + field, root)
    for index, ext in enumerate(data.get("extensions") or []):
        _relative(ext["config_path"], f"extensions[{index}].config_path", root)
    for index, path in enumerate((data.get("close_ritual") or {}).get("require_paths", [])):
        _relative(path, f"close_ritual.require_paths[{index}]", root)


def _leaves(value, prefix=""):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from _leaves(child, prefix + ("." if prefix else "") + key)
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from _leaves(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def _field_map(before, after, source_schema):
    old, new = dict(_leaves(before)), dict(_leaves(after))
    result, mapped = [], set()
    for key, value in old.items():
        target = key
        if key == "overseer_config_version":
            target = "schema"
        elif key == "vcs" and source_schema in ("bounded-1", "october-2"):
            target = "vcs.canonical"
        elif key.startswith("muse.") and source_schema == "october-2":
            target = "vcs.muse.binding." + key[5:]
        mapped.add(target)
        result.append({"before_path": key, "after_path": target, "before": value,
                       "after": new.get(target), "disposition": "preserved" if value == new.get(target) else "mapped"})
    for key, value in new.items():
        if key not in mapped:
            result.append({"before_path": None, "after_path": key, "before": None,
                           "after": value, "disposition": "added"})
    return tuple(result)


@dataclass(frozen=True)
class NormalizedConfig:
    data: dict[str, Any]
    source_schema: str
    field_map: tuple[dict, ...]
    diagnostics: tuple[str, ...]
    adapter: legacy.OverseerConfig
    hosted_dashboard: Any

    @property
    def bound(self):
        return bool(self.data["repo"].get("id") and self.data["repo"].get("root") and self.data.get("runtime"))

    @property
    def authority(self):
        return self.data["vcs"]["canonical"]

    def to_bytes(self):
        return yaml.safe_dump(self.data, sort_keys=False, allow_unicode=True).encode("utf-8")


def normalize(data: bytes, *, root: Path, runtime: dict | None = None,
              bind: bool = False, lane: str | None = None, model: str | None = None,
              identity: str | None = None) -> NormalizedConfig:
    """Read all supported schemas without resetting known values.

    ``bind=True`` is reserved for explicit init/migration planning.  Existing
    identity, physical root, context and runtime origin must still agree.  A
    supplied runtime is never substituted for an existing runtime binding;
    explicit refresh remains the caller's separate reviewed operation.
    """
    root = Path(root).resolve()
    raw = decode(data)
    if "overseer_config_version" in raw:
        _mapping(raw, CORE | OPTIONAL | {"overseer_config_version", "context", "runtime"}, "config", CORE)
        if type(raw["overseer_config_version"]) is not int or raw["overseer_config_version"] != 1:
            raise Refusal("config_version_or_vcs_unsupported")
        source = "legacy-full"
        result = deepcopy(raw)
        del result["overseer_config_version"]
    elif type(raw.get("schema")) is int and raw["schema"] in (1, 2):
        authority = raw.get("vcs")
        if authority not in ("git", "muse") or (authority == "muse" and raw["schema"] != 2):
            raise Refusal("config_version_or_vcs_unsupported")
        required = {"schema", "repo", "context", "runtime", "vcs"} | ({"muse"} if authority == "muse" else set())
        _mapping(raw, required, "config", required)
        _mapping(raw["repo"], {"name", "id", "root"}, "repo", {"name", "id", "root"})
        _identity(raw["repo"]["id"])
        if raw["repo"]["root"] != str(root):
            raise Refusal("config_repository_mismatch")
        _mapping(raw["context"], {"lane", "model"}, "context", {"lane", "model"})
        _runtime(raw["runtime"])
        source = "bounded-1" if raw["schema"] == 1 else "october-2"
        result = _default_full(authority)
        result.update({key: deepcopy(raw[key]) for key in ("repo", "context", "runtime")})
        result["repo"]["root_relative_docs"] = "docs"
        if authority == "muse":
            result["vcs"]["muse"]["binding"] = deepcopy(raw["muse"])
    elif type(raw.get("schema")) is int and raw["schema"] == 3:
        _mapping(raw, CORE | OPTIONAL | {"schema", "context", "runtime"}, "config", CORE | {"schema", "context", "runtime"})
        source, result = "schema-3", deepcopy(raw)
    else:
        raise Refusal("config_version_or_vcs_unsupported")
    result["schema"] = 3
    _validate_shapes(result)
    diagnostics = []
    repo = result["repo"]
    _label(repo["name"], "repo.name")
    if repo.get("id") is not None:
        _identity(repo["id"])
        if identity is not None and identity != repo["id"]:
            raise Refusal("repo_identity_change_requires_rebind")
    elif bind:
        repo["id"] = identity or str(uuid.uuid4())
        _identity(repo["id"])
    else:
        repo["id"] = None
    if repo.get("root") is not None and repo["root"] != str(root):
        raise Refusal("config_repository_mismatch")
    repo["root"] = repo.get("root") or (str(root) if bind else None)
    if runtime is not None:
        _runtime(runtime)
    if result.get("runtime") is not None:
        _runtime(result["runtime"])
        if runtime is not None and result["runtime"]["root"] != runtime["root"]:
            raise Refusal("runtime_installation_mismatch")
    elif bind:
        if runtime is None:
            raise Refusal("explicit_runtime_required_to_bind")
        result["runtime"] = deepcopy(runtime)
    else:
        result["runtime"] = None
    docs = result["docs"]
    if docs.get("canonical_next", "docs/NEXT.md") != "docs/NEXT.md":
        raise Refusal("config_canonical_next_must_be_docs_NEXT")
    docs["canonical_next"] = "docs/NEXT.md"
    docs.setdefault("handover_title", "Overseer Handover")
    docs.setdefault("roadmap_title", "Roadmap")
    context = result.get("context")
    if context is not None:
        _mapping(context, {"lane", "model"}, "context", {"lane", "model"})
        if lane is not None and lane != context["lane"]:
            raise Refusal("config_context_lane_change_requires_selection")
        if model is not None and model != context["model"]:
            raise Refusal("config_context_model_change_requires_selection")
    else:
        selected_lane = docs.get("default_lane") or lane or "product"
        if lane is not None and lane != selected_lane:
            raise Refusal("config_default_lane_conflict")
        context = {"lane": selected_lane, "model": model or "GPT-6 Astra"}
        diagnostics.append("context_proposed: lane=" + selected_lane + "; model=" + context["model"])
    result["context"] = context
    _token(context["lane"], "context.lane")
    _label(context["model"], "context.model")
    if docs.get("lanes") is None:
        if docs.get("default_lane") is not None:
            raise Refusal("config_default_lane_requires_lanes")
        docs["default_lane"] = context["lane"]
        docs["lanes"] = {context["lane"]: {field: docs[field] for field in ("handover", "roadmap", "handover_title", "roadmap_title")}}
    if docs.get("default_lane") != context["lane"]:
        raise Refusal("config_default_lane_conflict")
    for name, lane_docs in docs["lanes"].items():
        if lane_docs.get("repo_id") not in (None, repo["id"]):
            raise Refusal("config_lane_owner_mismatch: " + name)
        lane_docs["repo_id"] = repo["id"]
    muse = result["vcs"]["muse"]
    binding = muse.get("binding")
    if binding is not None:
        if result["vcs"]["canonical"] != "muse":
            raise Refusal("muse_binding_requires_muse_authority")
        _mapping(binding, {"repo_id", "store", "runtime"}, "vcs.muse.binding", {"repo_id", "store", "runtime"})
        if not isinstance(binding["repo_id"], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", binding["repo_id"]):
            raise Refusal("muse_source_identity_invalid")
        if not isinstance(binding["store"], str) or not Path(binding["store"]).is_absolute():
            raise Refusal("muse_store_binding_invalid")
        mr = _mapping(binding["runtime"], {"python", "version", "sha256"}, "vcs.muse.binding.runtime", {"python", "version", "sha256"})
        for key, value in mr.items():
            _label(value, "vcs.muse.binding.runtime." + key)
        if not Path(mr["python"]).is_absolute() or Path(mr["python"]).parent.name != "bin" or not SHA256.fullmatch(mr["sha256"]):
            raise Refusal("muse_runtime_binding_invalid")
        diagnostics.append("muse_source_binding_requires_native_verification")
    working_dir = muse.get("working_dir")
    if working_dir is not None:
        _relative(working_dir, "vcs.muse.working_dir", root, directory=True)
        if (root / working_dir).resolve() != root:
            if bind:
                raise Refusal("muse_working_dir_requires_explicit_pairing")
            diagnostics.append("muse_working_dir_requires_explicit_pairing")
    adapter = _adapter_view(result)
    _validate_paths(result, root)
    try:
        hosted = parse_hosted_dashboard_config(result.get("hosted_dashboard"))
    except (ValueError, TypeError) as exc:
        raise Refusal("config_invalid: " + str(exc)) from exc
    diagnostics.extend(adapter.extension_warnings)
    if adapter.freeze_contract.reviewer.model == "thinking-high":
        diagnostics.append("legacy_reviewer_model_preserved: thinking-high")
    if source != "schema-3":
        diagnostics.append("migration_required: " + source + " -> schema-3")
    if not (repo["id"] and repo["root"] and result["runtime"]):
        diagnostics.append("explicit_binding_required")
    return NormalizedConfig(result, source, _field_map(raw, result, source), tuple(diagnostics), adapter, hosted)

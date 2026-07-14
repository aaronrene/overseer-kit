"""Upstream credential scope refuse helpers (§HGD.6.2)."""

from __future__ import annotations

# Conceptual write-class scopes — refuse when advertised by host introspection.
REJECTED_SCOPE_TOKENS = frozenset(
    {
        "contents:write",
        "administration",
        "admin:org",
        "admin:repo_hook",
        "admin:org_hook",
        "workflows",
        "delete_repo",
        "workflow",
        "repo:status",  # not write; keep focused on true write classes below
    }
)

# Explicit write-class tokens used by tests and startup checks.
WRITE_SCOPE_TOKENS = frozenset(
    {
        "contents:write",
        "administration",
        "admin:org",
        "admin:repo_hook",
        "admin:org_hook",
        "workflows",
        "workflow",
        "delete_repo",
        "repo",  # classic full-access PAT — refuse when introspected
    }
)

# Narrow read-only conceptual scopes (informational).
READ_SCOPE_TOKENS = frozenset(
    {
        "contents:read",
        "metadata:read",
        "public_repo",  # classic public read — handled carefully; prefer contents:read
    }
)


def scopes_contain_write_class(scopes: frozenset[str] | set[str] | list[str] | None) -> bool:
    """Return True when any advertised scope is a rejected write class.

    When scopes cannot be introspected (``None``), returns False so the operator
    runbook + tests must prove write HTTP verbs are unreachable.
    """
    if scopes is None:
        return False
    normalized = {s.strip().lower() for s in scopes if isinstance(s, str) and s.strip()}
    write_normalized = {s.lower() for s in WRITE_SCOPE_TOKENS}
    # ``repo`` is classic full access — refuse when present among introspected scopes
    # unless the only intersection is empty.
    return bool(normalized & write_normalized)


def refuse_write_scopes(scopes: frozenset[str] | set[str] | list[str] | None) -> str | None:
    """Return error token ``write_scope_refused`` when write scopes are present."""
    if scopes_contain_write_class(scopes):
        return "write_scope_refused"
    return None

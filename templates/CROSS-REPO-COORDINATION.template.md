# Cross-repository coordination — {{repo.name}}

## Ownership

Each repository owns its identity, physical root, runtime, history authority,
settings and canonical `docs/NEXT.md`. A lane never grants another repository's
write authority. Declare authorized absolute member roots in an explicit workspace
manifest; do not discover repositories from sibling directories or environment.

## Dependency board

| Member | Owned outcome | Dependency | Evidence |
| --- | --- | --- | --- |
| {{repo.name}} | Owner-defined | Explicit dependency | Canonical member NEXT |

Use `ok workspace status`, `ok workspace check-next --lane product` and
`ok workspace doctor`. Optional member failures remain visible; `--strict-all`
on status makes them failing. A relay pin is a SHA-256 of the whole canonical
member NEXT and fails when stale. No workspace read updates another member.

## Handoff

Update each repository's paired summaries in its own authorized session.
Validate that repository's NEXT through its bound launcher. Never scrape or
copy a HANDOVER prompt into a new authoritative action.

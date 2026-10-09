# Explicit Muse mirror workflow — {{repo.name}}

Git-only operation is a permanent choice. Mirroring requires explicit Muse
adoption, approved main/revision and destination, and an isolated physical target.
The current bounded-v1 runtime offers `ok mirror prepare`, `verify`, and separately
authorized `deliver`. The script delegates to the bound launcher; it has no default
export/push and no positional commit-message interface.

Read the installed kit's `MUSE-BRIDGE-WORKFLOW.md` for the reviewed JSON plan schema,
raw plan-digest requirement, exclusions, explicit executable list and retry rules.
Prepare creates only a dedicated bare target outside all source/development trees.
No-change runs preserve correspondence; delivery independently observes Hub/Git
state and reports export, push and PR outcomes separately with explicit context.

Do not reuse legacy `.muse/mirror` targets, native export defaults, automatic hooks,
old regime tokens or old publication instructions. Existing remote mirror history
needs explicit reconciliation before use. Preparation is offline; it does not
establish publication authorization or complete-product readiness.

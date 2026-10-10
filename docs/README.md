# Overseer Kit v1 documentation

Start with the repository `README.md`. It describes installation, initialization,
daily use, handoff publication, update notifications, and current limitations.

## Current documents

| Document | Purpose |
| --- | --- |
| [Published rc.1 closeout](decisions/V1-RELEASE-PUBLICATION.md) | Exact tag, assets and completed publication |
| [Public evidence](validation/V1-PUBLIC-EVIDENCE.md) | Public release/CI links and local-evidence limits |
| [Git-only quickstart](GIT-ONLY-QUICKSTART.md) | Permanent Git-only operation with current commands |
| [Installation and rollback](releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md) | Unchanged published companion guide |
| [Scope reset](decisions/V1-SCOPE-RESET.md) | Authoritative bounded-v1 product scope |
| [Validation](validation/V1-RECOVERY.md) | Reviews, test results, installation/rollback, and consumer pilot evidence |
| [Muse restoration audit](validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08) | Corrected Muse-first scope, reproduced gaps, architecture, and restoration plan |
| [Canonical NEXT format](PRINT-NEXT.md) | How v1 reads and publishes the sole handoff |
| [Explicit adoption and rollback](MIGRATE-EXISTING-REPO.md) | Git/Muse selection, local exclusions, config migration and rollback |
| [Roadmap](ROADMAP.md) | Current milestone summary; never a prompt source |
| [Handover](OVERSEER-HANDOVER.md) | Current evidence summary; never a prompt source |
| [Test scope](../tests/README.md) | Supported and historical test boundaries |

## Historical material

The October 2026 scope reset superseded the former hosted/desktop product,
multi-repository orchestration, freeze/ledger gates, governance-sync,
publishing commands, OCI/registry design, and automatic recovery machinery.

Older specifications, runbooks, landing pages, templates, skills, policies, tools,
and phase records remain in this repository as historical source and evidence.
Unless a current document above explicitly incorporates them, they do not describe
the v1 command surface and should not be followed as installation or operating
instructions. `cli/legacy_main.py` preserves the former CLI source; `cli/main.py`
exposes only bounded v1.

The owner corrected the mistaken exclusion of MuseHub authority and GitHub
mirroring. R1–R3 restoration, repaired source delivery, GitHub acceptance and rc.1
publication are recorded in the current closeouts above. The controlled bridge
workflow describes explicit preparation and separately authorized delivery.
Git-only remains permanent and Muse adoption explicit. This documentation proposal
does not update the published candidate or claim stable/complete-product readiness.

# Overseer Kit v1 documentation

Start with the repository `README.md`. It describes installation, initialization,
daily use, handoff publication, update notifications, and current limitations.

## Current documents

| Document | Purpose |
| --- | --- |
| [Scope reset](decisions/V1-SCOPE-RESET.md) | Authoritative bounded-v1 product scope |
| [Validation](validation/V1-RECOVERY.md) | Reviews, test results, installation/rollback, and consumer pilot evidence |
| [Canonical NEXT format](PRINT-NEXT.md) | How v1 reads and publishes the sole handoff |
| [Roadmap](ROADMAP.md) | Current milestone summary; never a prompt source |
| [Handover](OVERSEER-HANDOVER.md) | Current evidence summary; never a prompt source |
| [Test scope](../tests/README.md) | Supported and historical test boundaries |

## Historical material

The October 2026 scope reset superseded the former hosted/desktop product,
multi-repository orchestration, Muse regimes, freeze/ledger gates, governance-sync,
publishing commands, OCI/registry design, and automatic recovery machinery.

Older specifications, runbooks, landing pages, templates, skills, policies, tools,
and phase records remain in this repository as historical source and evidence.
Unless a current document above explicitly incorporates them, they do not describe
the v1 command surface and should not be followed as installation or operating
instructions. `cli/legacy_main.py` preserves the former CLI source; `cli/main.py`
exposes only bounded v1.

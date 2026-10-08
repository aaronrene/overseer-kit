# Overseer Kit v1 roadmap

2026-10-08 — Muse restoration audit complete; intended v1 remains incomplete.
The owner's [scope correction](decisions/V1-SCOPE-RESET.md) restores MuseHub
authority and GitHub mirroring as requirements. OCI remains excluded. The
Git-only release candidate is preserved locally and is on hold.

| Milestone | State |
| --- | --- |
| Preserve original work and recovery snapshots | Complete; original Muse refs/config and Git edits unchanged during this audit |
| Git repository-bound status/init/sync/NEXT and atomic writer | Implemented; existing supported suite has 77 tests |
| Git-core architecture and corrected build findings | Closed; unchanged review not repeated |
| Git clean installation and current/previous rollback | Closed; two separate venv installations, six fixture lifecycle stages |
| Previously authorized DINERO manual pilot | Closed; 32 checks passed; no consumer access in this audit |
| README/update reminders and local release preparation | Completed for Git scope; candidate held pending intended Muse scope |
| Muse restoration audit and remote-base reconciliation | Complete; 841/841 Git main file bytes match staging MuseHub main |
| R1: Muse-aware local status/NEXT and adoption | Planned; production implementation not authorized by this audit |
| R2: Controlled mirror with reliable retry and source correspondence | Planned; depends on R1 authority/exclusion policy |
| R3: Isolated source reconciliation, integration review, combined installation/rollback | Planned; depends on R1/R2 |
| Authorized Muse-first publication and bounded consumer validation | Later gate; no remote write or consumer activation authorized here |

The [audit record](validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08)
contains current/proposed diagrams, 18 prioritized findings, feature disposition,
an ordered restoration plan, commands/results and the acceptance matrix. Ordinary
local logs are retained in `../RECOVERY-RUNS/20261008-muse-restoration-audit/`.
There were 40 diagnostic probes: 39 confirmed their named observations and one
hypothesis was corrected. Some observations reproduce defects; this is not a count
of passing product tests. The supported suite passed **77 tests, zero failures or
skips in 41.80s**; the closeout result and hygiene checks are in validation.

Reuse the tested Git handoff core and native Muse import/export. Add a narrow Muse
revision backend and repair the mirror boundary before use. The current runtime
does not notice a Muse-only revision change; the retained script can export HEAD,
push before its checks, hide PR failure, and mishandle an interrupted push. Native
export also needs clean-target, exact-content, mode and mapping checks. Local
bindings/NEXT must remain local in both VCS systems. Muse symbol/caller analysis
worked in fixtures and is optional advisory context, not a handoff authority.

Staging is the verified current Hub. Production CLI access refuses a hub fingerprint
mismatch; no trust reset or host switch occurred. Read-only GitHub queries succeeded
with approved network access, correcting the earlier conclusion that sandbox
authentication output established invalid credentials. Publication rights remain
untested. No branch, tag, release, mirror or remote source change was published.

Budget: four sessions were explicitly numbered. README maintenance, release
preparation and this audit were additional substantial work. Conservatively plan
with seven used, while recognizing that exact historical session boundaries were
not recorded. R1–R3 need an estimated three further sessions, with a fourth
contingency. This does not fit the original eight-session ceiling on that count.
The next decision is a bounded budget extension: three additional restoration
sessions, with a checkpoint before a fourth or any remote publication. R1 follows
that decision. Only canonical `docs/NEXT.md`, published by `next-write`, carries
the executable next prompt; this summary is not a competing task queue.

Keep the release worktree, original history and existing consumer installations
intact. Do not rerun closed Git review/install/pilot work against unchanged code.
Automatic hooks remain off; broad adoption waits for combined validation. Simple
opt-in GitHub Release watching can remain the update reminder once releases follow
verified Muse-to-GitHub publication. No automatic pull, OCI, daemon or replacement
governance framework is required.

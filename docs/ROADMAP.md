# Overseer Kit v1 roadmap

2026-10-08 — R2 controlled mirror preparation and retry are implemented locally.
R3 source reconciliation and combined validation are next. The complete intended
product remains unfinished; the preserved release candidate stays on hold. The
[scope clarification](decisions/V1-SCOPE-RESET.md) authorizes local restoration
without a session ceiling and preserves two permanent choices:

- **Git/GitHub only:** standalone handoffs without Muse, an account, network checks,
  or forced migration.
- **MuseHub with a GitHub mirror:** explicitly selected Muse authority and controlled
  one-way snapshot distribution. Preparation is offline; delivery is a separately
  authorized operation with fresh source/destination observations.

| Milestone | State |
| --- | --- |
| Preserve original work and recovery snapshots | Complete through R2; original Muse state/Git edits and clean held release preserved |
| Git status/init/sync/NEXT and confined atomic writer | Retained; full supported matrix includes the permanent Git-only mode |
| Git-core architecture/build review, installation/rollback, authorized DINERO pilot | Closed; unchanged reviews and consumer work not repeated |
| Muse restoration audit and common-base reconciliation | Complete; 841/841 shared file bytes matched verified staging main |
| R1: Optional Muse local handoffs and explicit adoption | Implemented; original 135-test combined evidence retained |
| R2: Controlled mirror preparation, correspondence and delivery retry | Implemented; 66 new mirror cases pass; full combined results in validation |
| R3: Isolated source reconciliation, changed-integration review, combined installation/rollback | Next |
| Authorized Muse-first publication and bounded consumer validation | Later gate; no real mirror, remote write or consumer activation performed in R2 |

R1 retains checkout UUID/root/context protections and uses the selected VCS for
freshness. Muse logical identity and its separate runtime are pinned; Git bindings
never convert automatically. Explicit adoption preserves documents and edits, saves
exact prior config, and supports tested rollback. R1 exclusions protect local
config, launcher, NEXT, backups and editor assets. Local status/NEXT still report
publication as `not_checked_offline`.

R2 adds `mirror prepare`, `verify`, and explicit `deliver`, plus a bound replacement
for the old deploy script/template. An approved plan pins source main/revision/Hub
identity, target physical path, GitHub repository/branches and expected heads.
Only newly created or engine-owned bare targets are accepted. Inherited hooks,
foreign content, overlap, source/target drift and missing objects refuse.

Pinned native Muse reads supply the projected bytes; Git plumbing replaces the
unsafe native export mutation path. Every blob/path/mode is checked before updating
the target ref. Actual snapshot exclusions are reported. Regular files project to
`100644`/`100755` under an explicit executable list; symlinks, hardlinks and special
permission bits refuse. No-change retry preserves the mapping; interrupted record
writes recover from checked source/plan trailers. Push and PR retry independently
observe state and report separate outcomes with explicit repository context.

The [mirror runbook](../MUSE-BRIDGE-WORKFLOW.md) describes the schema, supported
limits and invocation. Existing legacy mirrors need explicit reconciliation; this
implementation does not authorize replacing the kit's current remote mirror.
The live public-staging JSON refs adapter and GitHub write lifecycle have only
recording-transport evidence. Production trust, private Hub authentication and
publication rights remain unverified. There is no host/trust fallback.

**Final combined suite: 201 passed, zero failures/errors/skips in 261.42s.**

The [R2 validation entry](validation/V1-RECOVERY.md#r2-controlled-mirror-preparation-and-retry--2026-10-08)
records exact commands, full suite counts, initial corrections, runtime digest and
preservation checks. No independent integration review or final-v1 approval is
claimed from the implementation suite.

R3 must reconcile in isolation from verified staging main
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`,
apply only the reviewed recovery delta from Git `d47291d5d9030de5ebef713da95efa978c4d8c6e`,
and compare source bytes, exclusions and explicit executable policy. Preserve
original refs and the held release. Validate supported Git/Muse CI, review the
changed integration once, and exercise fresh combined installation, migration,
current/previous rollback and a no-hooks manual lifecycle in disposable fixtures.
Production fingerprint trust must not be reset to bypass its recorded refusal.

Only canonical `docs/NEXT.md`, published and validated through `next-write`, carries
the executable next action. R2 closeout advances it to R3; this is a summary.

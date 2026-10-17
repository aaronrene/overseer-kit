# Maintained product surfaces

Use the physical installation's `cli/ok -C ROOT`, or the repository-bound
`.overseer/bin/ok -C ROOT`. Every command captures repository identity, full
configuration, runtime digest and selected authority. Reads recheck before output;
retained engine writes use a request-local guard, directory lock, prior-file digest
and confined atomic replacement. Per-file writes are not a cross-file transaction. Config/NEXT retain their 128 KiB limits; full migration records and engine assets have a separate 16 MiB bound. Existing lock timestamps are preserved; new timestamps are labelled unrecorded rather than fabricated.

`status` includes canonical NEXT and lane states, footprint drift, governance,
configured gates, optional-feature reminders, routing, cost and readiness.
`--workspace` adds declared member status. Remote freshness is unknown by default.
`route --validate` checks policy; position/tier/gate queries give hints without
calling a model or changing the owner's selected model. Full settings remain in
schema 3; modules and policy files are owner-controlled.

`governance-sync` defaults to a read-only local observation and paired-summary
plan. `--write` requires a clean selected feature branch, applies both summaries
and makes a local commit. `--push --allow-network` separately requests Git feature
transport. Muse distribution uses the controlled mirror service. Explicit remote
PR enrichment needs `--allow-network --gh /physical/gh`. Existing prose and NEXT
are preserved; old prompt regeneration, automatic branch switching and native
export are not used. `--print-next` reads canonical NEXT and cannot accompany
writing, push or all-lanes ambiguity. A work commit may make NEXT stale; publish
accepted follow-up text explicitly. Repeating an unchanged local hygiene plan
is a no-op. `handover-compact --keep N` previews dated-entry archiving;
`--write` explicitly applies it without touching canonical prompts.

`review --freeze PATH` retains local mechanical checks, API-provider mode, human
fallback, reviewer labels, explicit checklist, dry-run and controlled stamps.
A mechanical pass is not an independent semantic review. Existing non-pass stamps
and policy escalation remain meaningful. API use requires `--allow-network`;
focused tests use injected fake providers. `check-ok` creates/reuses a scoped
artifact and uses the same reviewer; `--scaffold-only` only creates the artifact,
while `--dry-run` writes nothing. The deprecated alias shares this implementation.

`verify-step --step ID`, `--through current` or `--all` uses configured consumer
scripts; `--dry-run` plans without execution. A configured orchestrator returns
its confined argv, working directory and explicit environment without invoking
an executor or marking steps verified; selected manifest/policy paths remain
confined for both preview and execution. Scripts are explicit local code,
confined to the selected repository, and run with captured context. Their own
external effects remain the owner's responsibility. Missing prerequisites and
nonzero exits never become PASS. `honesty-status` reads configured verdict,
provenance, evidence, deployment-health, ISR and adversarial-freeze requirements.
`ledger append --kind KIND --file FILE` (or `--stdin`), `verify` and `show --last N`
retain the hash chain, role distinctions and signature/evidence validation.

Workspace uses an explicitly configured repository-relative manifest. Member
roots must be explicit absolute paths; no ambient environment, home index or
sibling scan supplies them. Each member independently validates UUID, runtime,
authority, lane and canonical NEXT. Optional missing members remain visible;
`--strict-all` makes them failures. Optional `canonical_next_pins: {member: SHA256}`
in that manifest checks relayed whole-file digests. Live canonical reads are
labelled separately from pinned relays. No member write is reachable.

`land-check` retains prepare-PR/verify-landed checks and never merges.
`land-closeout` is read-only and defaults offline. Remote enrichment is opt-in.
`pr-land` requires an authorization reason, `--allow-network` and explicit `--gh`;
its dry-run still reads the remote. Configured post-land synchronization is clean,
ff-only, requires the additional `--post-land-sync` authorization and remains separate from NEXT publication. GitHub transport explicitly pins every invocation to the configured GitHub remote. PR selectors and resolved URL/number identities must match that repository; option-shaped selectors and target drift refuse before further transport. Release/signing/deployment are not
part of these commands or session hooks.

The loopback app exposes status, selected-lane documents, canonical `/api/next`,
review, local governance, honesty and ledger services. Bearer credentials are
process-local, mutations require CSRF, origins are checked and paths confined.
The startup banner is emitted after binding succeeds. Desktop uses that same
launcher and checks health identity. Hosted routes accept only read verbs and
explicit host/org/repository allowlists; remote NEXT is display-only and cannot
authorize local work. Hosted upstream HTTP redirects refuse before a second
request, so redirects cannot forward credentials outside the original request.
No hosted endpoint can invoke a local mutator.

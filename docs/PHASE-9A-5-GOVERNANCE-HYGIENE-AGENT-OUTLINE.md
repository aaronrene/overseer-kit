# Phase 9A-5 — Governance Hygiene Agent (Frozen Thinking Outline)

Status: **Frozen design for the Auto build (9A-5 impl). No implementation in this step. No env
changes. No live hooks installed. No `muse push staging`. No `git push origin main`. No `main`
merge. All write paths ship behind a default dry-run mode; the inert double for this agent is a
dry-run that reports what it would do and writes nothing.**

This document freezes WHAT and HOW for the Governance Hygiene Agent so the Auto build implements
mechanically against a fixed spec, per RULE #8 (Orchestrator) and the single-model handover
protocol. It is the contract layer only.

The agent is the **first tool shipped by the Overseer Kit**, and it is specified **against the kit's
VCS adapter interface** (`docs/OVERSEER-KIT-ARCHITECTURE-OUTLINE.md` §4) so it is **repo-agnostic
from day one** — the same agent runs in Scooling, Knowtation (`muse+git-mirror`), MuseHub
(`muse-only`), and any external `git-only` repo, driven entirely by that repo's
`.overseer/config.yaml`.

Frozen inputs it composes with (does **not** fork):

- `docs/OVERSEER-KIT-ARCHITECTURE-OUTLINE.md` §3 (`.overseer/config.yaml`), §4 (VCS adapter
  interface + three fail-closed backends), §6 (Freeze-Contract policy).
- `docs/OVERSEER-HANDOVER.md` — the doc it maintains (its NEXT SESSION block, VCS table, Done
  recently, Verified snapshot, Change log, paste-ready prompt).
- `docs/ROADMAP.md` — the doc it maintains (queue status rows, "Next step at a glance").
- `docs/GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` — the recurring inversion failure it detects.
- `docs/CROSS-REPO-COORDINATION.md` — SD-11 (no docs-only PR to `main` without operator request),
  SD-14 (Muse main before GitHub; never `git push origin main`), SD-17 (governance sync is a hard
  prerequisite; routine feature-branch hygiene is Tier 1), the Tier 1/2/3 authority table.
- `.cursor/skills-cursor/automate/SKILL.md` — the Cursor Automation implementation surface for the
  scheduled/session-end trigger.

---

## Simple summary (no jargon)

Every work session is supposed to end with two documents matching reality: the handover note (what
just happened, what is next) and the roadmap (phase status). The problem is that when someone merges
code on GitHub without also updating our canonical history (Muse), the documents quietly go stale
and the two histories get out of order — and a human has to notice and fix it. That has happened
four times.

This agent is a careful assistant that, on demand or at the end of a session, **reads the true
state from the tools themselves** (not from the documents, which may be wrong), compares that truth
to what the documents claim, and — if they disagree — updates the documents and, when safe, nudges
the canonical history back into line. It is deliberately timid: if any read fails, it stops and
tells you exactly which command failed rather than guessing. Its default mode is a "dry run" that
shows you what it *would* change without touching anything. It never does the risky things
(merging to the main line, publishing, flipping a live switch) on its own.

## Technical summary

This freezes a repo-agnostic **Governance Hygiene Agent** invoked as `overseer governance-sync`
(and the `/governance-sync` slash command / session-end Automation). It reads true VCS state via the
kit's §4 adapter (`status`, `read_head`, `read_canonical_anchor`) plus `gh pr list --state merged`,
**never** parsing the governance docs to infer state. It detects a **minimal drift set** (handover
VCS-table sha vs `origin/main` sha; canonical anchor sha vs canonical-main sha; queue-row statuses
vs recently-merged PRs) chosen to catch the documented inversion pattern. On drift it performs
**templated section replacement** on the handover + roadmap (VCS table, Done recently, Verified
snapshot, Change log, paste-ready prompt block, queue rows, "Next step at a glance"). It runs
`realign()` (Muse `git-import --incremental`) **only** when the canonical anchor sha differs from
the canonical-main sha, **dry-run first**, applying only when the would-import commit count is under
`thresholds.realign_max_commits`. It commits to a feature branch (Tier 1), never to `main`, and —
per SD-11 — pushes the branch and **reports the PR URL for the operator** rather than opening a
docs-only PR to `main`. Every read is fail-closed; the whole run is idempotent; the default is
`--dry-run`.

---

## §0 — Scope (this Outline only)

Freezes: the trigger (§1), verified reads (§2), drift detection fields (§3), writes/patching (§4),
Muse realignment guard (§5), commit strategy (§6), error handling + idempotency (§7), the seven-tier
test matrix with the dry-run inert double (§8), security/privacy checklist (§9), blockers +
Definition of Done (§10).

**Not in scope (build-later, Auto):** the agent implementation, the Automation install, the slash
command registration, any real doc write outside a fixture, any env flip, any `main` merge, any
staging push. This doc adds **no code**.

**Compose, do not redesign:** the agent is a **consumer of the kit's §4 adapter** and the §3 config;
it does not implement VCS logic itself, does not fork the handover/roadmap templates, and does not
invent new authority tiers. It automates the existing SD-17 governance-sync obligation.

---

## §1 — TRIGGER (frozen)

**Decision: combination of (b) `/governance-sync` slash command + (a) session-end Cursor
Automation, both delegating to the same idempotent `overseer governance-sync` CLI. A git
`post-merge` hook (c) is explicitly REJECTED as a trigger.**

| Option | Verdict | Rationale |
| --- | --- | --- |
| (b) `/governance-sync` slash command → `overseer governance-sync` | **CHOSEN (primary)** | Works offline, no cloud credentials, fully idempotent, on-demand. The single source of behavior. |
| (a) Cursor Automation (session-end / schedule) → same CLI | **CHOSEN (secondary)** | Automates the SD-17 session-end obligation. Per `automate/SKILL.md`, degrades gracefully: if the Automations editor handoff is unavailable in the environment, the slash command / CLI remains the path. |
| (c) git `post-merge` hook | **REJECTED** | Does not fire for the actual failure mode (a **GitHub-side** merge on `origin/main` never runs a local `post-merge`); would not fire in `muse-only` MuseHub; hooks are per-clone and easy to miss. The kit prefers an explicit, auditable command over an invisible hook. |

The trigger requirement is satisfied by one behavior (`overseer governance-sync`) reachable two
ways; both are offline, credential-free, and idempotent (§7).

---

## §2 — READS (verified, not assumed) (frozen)

The agent reads true state **only from source**, via the kit's §4 adapter + `gh`. It **never**
parses `OVERSEER-HANDOVER.md` or `ROADMAP.md` to infer VCS state — those are the things being
checked.

| # | What it reads | How (via kit §4 adapter / tool) | Regime applicability |
| --- | --- | --- | --- |
| R1 | Current GitHub `main` sha | `adapter.read_head({ ref: "<git.remote>/<git.main_branch>" })` | `muse+git-mirror`, `git-only` |
| R2 | Canonical anchor sha (bridge anchor) | `adapter.read_canonical_anchor()` | all (muse-only → muse tip; git-only → origin/main tip) |
| R3 | Canonical-main sha (Muse `main` tip) | `adapter.read_head({ ref: "muse:<muse.main_branch>" })` | `muse+git-mirror`, `muse-only` |
| R4 | Recent merged PRs (last N, N=5) | `gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt` | regimes with `vcs.git` present |
| R5 | Working-tree cleanliness + branch | `adapter.status()` | all |

**Cross-repo cwd safety:** all Muse reads go through the adapter, which uses explicit
`muse -C <absolute-repo-root>` per the `CROSS-REPO-COORDINATION.md` 2026-06-20 note; the agent
confirms branch + HEAD before any subsequent write.

**Fail-closed (frozen):** if **any** of R1–R5 errors (missing ref, command failure, `gh`
unauthenticated, git/muse absent), the agent **stops and reports the exact failing command** and
writes nothing (§7). No read result is ever fabricated or defaulted.

---

## §3 — DRIFT DETECTION (frozen minimal set)

The agent compares exactly these fields — the minimal set that catches the documented inversion
pattern — and no more:

| Drift check | Compares | Drift condition | Catches |
| --- | --- | --- | --- |
| **D1 handover-vs-git** | Handover VCS-table "GitHub `main`" sha (parsed as a *claim to verify*) vs **R1** | not equal | Stale handover after a GitHub merge. |
| **D2 anchor-vs-canonical** | **R2** canonical anchor sha vs **R3** canonical-main sha | not equal | The Muse↔Git inversion itself (bridge behind Muse main, or Muse main behind Git) — the exact `GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` failure. |
| **D3 queue-vs-merged** | Roadmap queue-row statuses (parsed as claims) vs **R4** merged PRs | a merged PR has no matching row status of MERGED, or a row claims MERGED with no merged PR | Roadmap rows left as "PR open"/"NEXT" after the PR merged. |

**Important distinction (frozen):** parsing the docs in D1/D3 is reading them **as claims to be
verified against source**, which is allowed and is the whole point. It is **not** the forbidden
"parse the doc to *infer* VCS state" — the source of truth is always R1–R5; the doc value is only
the left-hand side of an equality check.

Drift result is a typed `{ D1, D2, D3 }` each `aligned | drifted | unreadable`; any `unreadable`
→ fail-closed stop (§7).

---

## §4 — WRITES (frozen: templated section replacement)

**Method: templated section replacement against named anchors, not free-form rewriting.** Each
maintained section has a stable heading/anchor the agent replaces wholesale from a template filled
with verified values; it never edits prose around the anchors.

| Doc | Section (anchor) | Patch content |
| --- | --- | --- |
| `OVERSEER-HANDOVER.md` | **VCS table** | Rebuilt from R1/R2/R3 (+ feature branch from R5). |
| `OVERSEER-HANDOVER.md` | **Done recently** | Prepend rows for R4 merged PRs not already listed. |
| `OVERSEER-HANDOVER.md` | **Verified snapshot** | Phase-position line updated from the reconciled queue (§3 D3). |
| `OVERSEER-HANDOVER.md` | **Change log** | Append one dated line describing the sync (what drifted, what was patched, realign result). |
| `OVERSEER-HANDOVER.md` | **NEXT SESSION heading + paste-ready prompt block** | See below. |
| `ROADMAP.md` | **Queue status rows** | Set the drifted rows to MERGED with PR number + sha from R4. |
| `ROADMAP.md` | **"Next step at a glance"** | Rebuilt from the reconciled next step. |

**Paste-ready prompt block (frozen handling):** the block is delimited by fenced markers the agent
owns. The agent **regenerates the block, it does not hand-edit inside it** — consistent with the
`CROSS-REPO-COORDINATION.md` rule that the handover block is a **projection of the durable docs**
(docs-first). If the reconciled NEXT step is an SD-3 `Thinking → Auto` step, the agent emits
`{step}a` and `{step}b` as **two** blocks (SD-3); otherwise one. The agent does **not** invent the
next step — it carries forward the queue's declared next row; if the next step is ambiguous
(no unambiguous next row), it patches everything else and **flags the NEXT block for human
authorship** rather than guessing (fail-closed on ambiguity).

**No content outside anchors is touched**, so a run is a minimal, reviewable diff.

---

## §5 — MUSE REALIGNMENT (frozen guard)

Runs **only** in regimes with a canonical/mirror split (`muse+git-mirror`); a **no-op** in
`muse-only` (single canonical history) and `git-only` (no Muse).

**Guard sequence (frozen):**

1. **Condition:** run realignment **only when D2 shows drift** (R2 canonical anchor sha ≠ R3
   canonical-main sha) **and** GitHub `main` (R1) is confirmed a **content superset** of the anchor
   (the recovery precondition in `GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md`). If D2 is aligned,
   **skip** realignment entirely.
2. **Dry-run first:** `adapter.realign({ dry_run: true, max_commits: thresholds.realign_max_commits })`
   → returns `would_import: n, from_ref, to_ref`.
3. **Threshold:** if `n > realign_max_commits` (default 50), **do not apply** — report the count and
   stop realignment (the operator investigates a large divergence manually). Patching of the docs
   still proceeds; only the realign apply is withheld.
4. **Apply:** if `n <= max_commits`, `adapter.realign({ dry_run: false, ... })`, which wraps
   `muse bridge git-import . --branch main --incremental --preserve-merge-commits` with explicit
   `muse -C <abs-root>`.
5. **Verify:** re-read R2/R3; confirm anchor now equals canonical-main; record the from/to shas in
   the Change-log patch (§4). If verification fails, report and stop (§7).

Realignment never runs on `--dry-run` of the agent as a whole (that mode reports the planned
realign but does not execute it).

---

## §6 — COMMIT STRATEGY (frozen)

- **Feature branch pattern:** from `.overseer/config.yaml` `vcs.git.feature_branch_pattern`, default
  `feat/{slug}`; slug = `governance-sync-<yyyy-mm-dd>`. Never commits on `main`/canonical-main
  (adapter `commit_feature` refuses protected refs, §4 of the kit spec).
- **Commit message template (frozen):**
  `chore(governance): sync handover+roadmap to <git-main-sha> (drift: <D1,D2,D3>)` with a body
  listing patched sections and the realign result. No secrets, **no hardcoded SHAs in the agent
  code** — the sha is read at runtime (R1) and interpolated into the message only.
- **Bundle rule (SD-17):** the commit bundles the handover + roadmap patches together; a
  governance-sync commit that omits either doc is incomplete and the agent refuses to make it.
- **Push:** Tier 1 — the agent may `git push` the **feature branch** (and, for `muse+git-mirror`,
  the corresponding Muse feature-branch commit), per SD-17.
- **PR (SD-11):** the agent **does not open a docs-only PR to `main`**. It pushes the branch and
  **prints the ready-to-open PR URL for the operator**, noting it is docs-only and therefore
  operator-gated. Opening/merging any PR to `main` stays Tier 3 (human).

---

## §7 — ERROR HANDLING + IDEMPOTENCY (frozen)

- **Any read failure = stop + report the exact command that failed** (R1–R5). The report names the
  failing command and the regime; the agent exits non-zero and writes nothing.
- **Never write partial state:** patches to the two docs + any realign are staged and committed as
  one unit; if any step fails mid-way, nothing is committed (the working tree is left clean, or the
  failure is reported with the tree untouched). No half-patched doc is ever committed.
- **Idempotent:** running twice in a row with no external change produces the **same result** — the
  second run detects `aligned` on D1–D3, makes no patch, performs no realign, creates no commit.
  Templated section replacement (§4) guarantees byte-stable output for the same inputs.
- **Ambiguity is fail-closed:** an undeterminable NEXT step (§4) or an `unreadable` drift field
  (§3) halts writing for that section and reports, rather than guessing.
- **Dry-run default:** `overseer governance-sync --dry-run` is the inert double — it runs R1–R5 and
  D1–D3 and prints the exact planned patch + planned realign, and **writes nothing, commits
  nothing, realigns nothing**.

---

## §8 — TEST MATRIX (seven tiers per RULE #0) (frozen — one case per tier before Build)

The **inert double is the dry-run mode**: it exercises the full read + drift + plan path and asserts
zero writes.

| Tier | One frozen test case |
| --- | --- |
| **unit** | `detectDrift` returns `{D1:drifted, D2:aligned, D3:aligned}` for a handover VCS-table sha that differs from a fixture `origin/main` sha, with all reads mocked. |
| **integration** | `governance-sync --dry-run` against a fixture `muse+git-mirror` repo reads R1–R5 via the fake adapter, computes D1–D3, and emits the planned handover+roadmap patch **without writing** (assert tree unchanged). |
| **e2e** | Full non-dry-run run on a fixture repo where D1+D3 drift: asserts the VCS table, Done-recently, queue rows, and paste block are patched, a feature-branch commit exists, `main` is untouched, and the printed PR URL is docs-only + operator-gated. |
| **stress** | A roadmap with 200 queue rows + 40 merged PRs (R4) reconciles within the performance bound and patches only the drifted rows. |
| **data-integrity** | Idempotency: run twice; second run detects fully `aligned`, produces no diff, no commit. Plus: induced failure after patching the handover but before the roadmap leaves **no** commit and a clean tree. |
| **performance** | `governance-sync` on a realistic repo (current Scooling handover+roadmap sizes) completes under the bounded budget; no unbounded VCS log scan (R4 limited to N=5). |
| **security** | The commit message + Change-log line contain no secrets and no hardcoded sha in source (sha only via R1 at runtime); `muse-only` regime never invokes git; a simulated `gh` auth failure fails closed with the exact command reported and zero writes. |

Realignment-specific cases fold into integration (dry-run count under/over threshold) and e2e
(apply + verify), asserting the §5 guard: skip when D2 aligned, refuse apply when `n > max_commits`.

---

## §9 — Security / privacy gate checklist (frozen)

- **No secrets / no hardcoded SHAs** in the agent source, commit templates, or Change-log lines —
  shas are read at runtime; `gh` uses the ambient authenticated session, never an embedded token.
- **Fail closed on every read** (R1–R5) — exact failing command reported; zero writes on failure.
- **Least privilege per regime** — `muse-only` never calls git/gh; `git-only` never calls muse;
  the agent asks the adapter, which enforces the regime.
- **No canonical write outside the review path** — the agent only patches governance **docs** on a
  **feature branch**; it never merges to `main`, never pushes staging, never flips a gate, never
  writes product/canonical data.
- **Docs-only PR restraint (SD-11)** — never auto-opens a docs-only PR to `main`; prints the URL
  for the operator.
- **Injection-safe** — doc text parsed in D1/D3 is treated as data (sha/status extraction only),
  never executed or interpolated into shell.
- **Idempotent + reviewable** — every run is a minimal, byte-stable, human-reviewable diff.

---

## §10 — Blockers + Definition of Done

**Blockers (explicit):**

| Blocker | State | Consequence |
| --- | --- | --- |
| Kit §4 VCS adapter interface must exist (K2) | OPEN | 9A-5 builds against it; until K2 lands, the agent uses the frozen interface with a fake adapter in tests only. |
| `.overseer/config.yaml` schema (K3 vendoring) | OPEN | The agent reads config via the frozen §3 schema; a real config is written at `overseer init` (K6). |
| Cursor Automation availability differs per environment | OPEN (K5) | Session-end trigger degrades to slash command / CLI when the Automations editor handoff is unavailable. |
| Muse `git-import --incremental` behavior re-verified per Muse version | OPEN | `realign` apply gated on a passing dry-run; large-divergence (> threshold) always defers to the operator. |

**Definition of Done (9A-5 build):** the agent runs as `overseer governance-sync [--dry-run]`,
repo-agnostic across the three regimes via `.overseer/config.yaml`; all seven test tiers green
locally with the dry-run inert double; fail-closed on every simulated read failure; idempotent;
no secrets/hardcoded SHAs; SD-11/SD-14/SD-17 honored (feature-branch commit, PR URL printed not
opened, no `main` merge, no staging push, no gate flip); and **both** governance docs updated for
the 9A-5 phase itself in the closing commit.

---

## Cross-references

- `docs/OVERSEER-KIT-ARCHITECTURE-OUTLINE.md` — §3 config, §4 adapter interface, §6 Freeze-Contract
  policy this agent is built against.
- `docs/GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` — the inversion pattern D2 + §5 detect and repair.
- `docs/CROSS-REPO-COORDINATION.md` — SD-11, SD-14, SD-17, Tier 1/2/3 authority table.
- `docs/OVERSEER-HANDOVER.md`, `docs/ROADMAP.md` — the two docs the agent maintains.

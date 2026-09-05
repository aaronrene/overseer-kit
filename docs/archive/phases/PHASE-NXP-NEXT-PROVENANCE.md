# Phase NXP — NEXT provenance + board identity activation

Status: **Thinking freeze — awaiting review.** NXP-a is **spec-only**; no code lands in this
phase. NXP-b (Auto) may not start until this document carries a `pass` review stamp.

```yaml
phase: NXP
outputs:
- id: nxp-next-provenance
  path: docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md
  frozen: true
frozen_inputs:
- id: ons-operator-next-surfacing
  path: docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
- id: k13-multi-repo-workspace-lanes
  path: docs/archive/phases/MULTI-REPO-WORKSPACE-LANES-FREEZE.md
- id: kh1-relay-standard
  path: docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: print-next-extract
  path: tools/print_next/extract.py
- id: next-command
  path: cli/commands/next.py
- id: workspace-board-names
  path: tools/workspace/board_names.py
- id: workspace-check-next
  path: tools/workspace/check_next.py
- id: status-command
  path: cli/commands/status.py
- id: session-start-hook
  path: cursor/hooks/session-start-next.sh
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
review_stamp:
  reviewed_at: '2026-09-05T00:10:47Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:2a1e297bfb81246fd29268a3399da23dfbcf20d6941ca85afcf99afe918ec46d
```

**Downstream edge:** NXP-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze).

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6;
uncited findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature
branch); merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| NXP-r1 | `ok review --freeze` (checklist, local) | findings | F1 MINOR C8 — citation-readiness discipline not evidenced (`docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md:1`). Fixed by adding this §6.2 review record. |
| NXP-r2 | Semantic re-read (thinking, authoring session — **not** independent) | findings | S1 layout supersede left existing ONS §ONS.5.4 assertions undefined, invitable as "regression" (`PHASE-NXP-NEXT-PROVENANCE.md:117`) → new §NXP.3.3. S2 `read_at` made full-stdout golden tests impossible; no clock seam frozen (`PHASE-NXP-NEXT-PROVENANCE.md:138`) → new §NXP.3.4. S3 N4 advisory undefined under `docs.lanes` (which lane? how many lines?) (`PHASE-NXP-NEXT-PROVENANCE.md:216`) → lane rule added to §NXP.6. |
| NXP-r3 | `ok review --freeze` (checklist, local) | **pass** | Checklist clean (0 findings) after S1–S3 fixes; stamp rewritten. |

---

## §NXP.0 — Simple summary

A `ok next` block cannot be traced back to the repo it came from. The heading
`## CURRENT NEXT — paste this` is byte-identical for every repo on the machine. When two or
more repos inject blocks into one chat, the operator and the agent must guess which authority
each block carries. This phase makes the printed block **say where it came from**, and turns on
the board-name identity the kit already built but never activated.

This phase does **not** disable session hooks. Hooks are the mechanism that keeps stale
instructions out of a session; the repo that caused the live incident is the one with **no**
hook. This phase sequences provenance **before** wider hook enablement.

---

## §NXP.1 — Verified problem (do not redesign)

Each claim below was confirmed live on this repo in the authoring session. NXP-b must not
re-litigate them.

| # | Verified fact | Evidence |
| --- | --- | --- |
| **V1** | Human stdout carries **no** repo identity. `format_current_next` emits heading + blank + fenced body only. | `tools/print_next/extract.py:129` (`format_current_next`), contract at `docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md` §ONS.5.4 steps 1–9 |
| **V2** | The identity data **already exists in memory** at print time and is simply not emitted. | `tools/print_next/extract.py:35-41` — `CurrentNextResult` holds `path` and `lane` |
| **V3** | `--json` is already self-identifying; only the human surface is anonymous. | `docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md` §ONS.5.5 — `path`, `lane` keys |
| **V4** | The frozen heading is byte-identical across all repos, so two adjacent blocks are indistinguishable at the heading level. | §ONS.5.3 `CURRENT_NEXT_HEADING`; asserted byte-for-byte by tests |
| **V5** | Repo-prefixed board names are **already specified and already built** — not a new idea. | `docs/archive/phases/MULTI-REPO-WORKSPACE-LANES-FREEZE.md` §MR.6.5 (`{n}-OVERSEER-HANDOVER.md`, e.g. `SCOOLING-OVERSEER-HANDOVER.md`); H17 predicate implemented at `tools/workspace/board_names.py:94` (`board_name_violation`) |
| **V6** | That identity check is **silently inert**: with no `workspace:` configured it prints a notice and **exits 0**. | Live run: `ok workspace check-next` → `workspace not configured (check-next requires workspace:)`, exit `0`; gate at `tools/workspace/check_next.py:117` |
| **V7** | Nothing nags an unconfigured repo toward board identity, so V5's shipped feature stays off indefinitely. | V6 exit `0` + `ok status` reporting `workspace_relay: not_configured` as informational only |

**Root cause statement (frozen):** the kit built board identity (V5) but gated it entirely
behind an opt-in manifest whose absence is a silent success (V6, V7), while the one surface an
operator actually reads in chat omits identity it already holds (V1, V2).

---

## §NXP.2 — Scope

**In scope (NXP-b):**

1. A visible provenance line on `ok next` human stdout (N1).
2. Additive `--json` identity keys (N2).
3. `ok workspace check-next` stops being a silent success when unconfigured (N3).
4. A **non-blocking** bare-board-name advisory in `ok status` outside workspace mode (N4).
5. Hook-enablement sequencing statement (N5).

**Out of scope — explicitly not this phase:**

- Renaming any consumer repo's handover files. That is operator work, per-repo, Tier 2/3.
- Authoring `.overseer/workspace.yaml` for any consumer constellation.
- Auto-enabling hooks anywhere (deferred to a separate phase; see N5).
- Any change to fence **body** bytes. `extract_paste_fence_body` and the GS-PASTE regen
  contract are **not** reopened.
- Any change to `CURRENT_NEXT_HEADING` itself (§ONS.5.3 stays byte-exact).
- Per-branch handover filenames — remains forbidden by §ONS.3 A1.2.

---

## §NXP.3 — N1. Provenance line on human stdout

### §NXP.3.1 — Narrow supersede of §ONS.5.4

This is a **named, narrow supersede** of ONS §ONS.5.4's byte layout. Everything else in ONS
stands. The heading remains line 1 so existing `startswith` / grep assertions and the operator's
visual anchor are preserved.

Frozen byte layout (UTF-8, trailing newline on last line):

1. `CURRENT_NEXT_HEADING` — unchanged, still line 1
2. newline
3. newline (blank line)
4. **provenance line** (§NXP.3.2) — new
5. newline
6. newline (blank line)
7. opening fence line `` ```text ``
8. newline
9. fence body from `extract_paste_fence_body` — **unchanged bytes**
10. if body does not end with newline, append one newline
11. closing fence line `` ``` ``
12. newline

### §NXP.3.2 — Provenance line format (frozen)

Exactly one line, rendered visibly (not an HTML comment — it must survive markdown rendering
in a chat surface):

```
**Source:** `<repo_name>` · `<repo_root_abs>` · `<doc_rel>` · lane `<lane>` · read `<read_at>`
```

| Field | Value | Fallback |
| --- | --- | --- |
| `repo_name` | `config.repo.name` | literal `unknown` when absent |
| `repo_root_abs` | absolute POSIX path of the resolved repo root (folder containing `.overseer/`) | never empty; resolution failure is a §NXP.3.4 refusal |
| `doc_rel` | repo-relative POSIX handover path — the existing `CurrentNextResult.path` | required |
| `lane` | resolved lane name; literal `-` when `docs.lanes` unset | `-` |
| `read_at` | UTC ISO-8601 `YYYY-MM-DDTHH:MM:SSZ`, second precision, at read time | required |

Separator is ` · ` (space, U+00B7, space). Constant name in code: `PROVENANCE_LINE_TEMPLATE`.
Tests assert the exact template and the exact separator.

`read_at` MUST be the time the bytes were read from disk, not a cached or doc-embedded stamp.
It is the operator's staleness signal: a block pasted from an old chat carries an old `read_at`.

### §NXP.3.3 — Existing ONS layout tests are updated, not regressions

ONS-b's tests assert the §ONS.5.4 nine-step layout. Because §NXP.3.1 narrowly supersedes that
layout, those assertions **will** fail until updated. NXP-b MUST update them to the twelve-step
layout and MUST NOT interpret their failure as a regression to be worked around by suppressing
the provenance line. `CURRENT_NEXT_HEADING` assertions (§ONS.5.3) and fence-body assertions must
continue to pass **unchanged** — if either of those breaks, that *is* a real regression.

### §NXP.3.4 — Injectable clock (test determinism)

`read_at` changes on every invocation, so full-stdout golden comparisons are otherwise
impossible. The clock MUST be injectable (parameter or module-level seam) so tests can pin
`read_at` to a fixed instant. Production callers use the real UTC clock. NXP-b MUST NOT make the
timestamp omittable in production to satisfy tests — the seam is injection, not omission.

### §NXP.3.5 — Constraints inherited (unchanged)

- `ok next` still MUST NOT call `muse` or `git` (§ONS.5.1). Provenance is config load +
  filesystem resolution + clock only.
- `--quiet` still prints the whole block including provenance.
- `--print-next` synonym prints identically.
- Diagnostics stay on stderr; the block stays on stdout.

### §NXP.3.6 — Fail-closed

If repo root cannot be resolved to an absolute path, `ok next` MUST refuse rather than print an
anonymous block: exit `2`, reason token `repo_root_unresolved`, message containing
`cannot resolve repo root for provenance`. **Printing a block without provenance is not an
acceptable degrade path** — that is the exact defect this phase closes.

---

## §NXP.4 — N2. `--json` identity keys (additive)

Add three keys. All existing keys and their types are unchanged; consumers keying on `ok`,
`path`, `lane`, `heading`, `fence`, `error` are unaffected.

| Key | Type | Value |
| --- | --- | --- |
| `repo_name` | string \| null | `config.repo.name`, else `null` |
| `repo_root` | string | absolute POSIX repo root |
| `read_at` | string | same UTC ISO-8601 value rendered in §NXP.3.2 |

On the failure shape (`ok: false`), `repo_name` and `repo_root` are emitted when resolvable and
`null` otherwise; `read_at` is always emitted.

---

## §NXP.5 — N3. `check-next` stops being a silent success

`ok workspace check-next` with no `workspace:` configured currently prints a notice and exits
`0` (V6). Frozen behavior:

| Condition | stdout/stderr | Exit |
| --- | --- | --- |
| `workspace:` configured | unchanged (K13 §MR behavior, exit `35` on violation) | unchanged |
| `workspace:` absent, board names already prefixed per §MR.6.5 | advisory: workspace not configured; board names already compliant | `0` |
| `workspace:` absent, board names bare/legacy | advisory naming the bare basename **and** the compliant `{n}-` target | `0` |

Exit code stays `0` in both unconfigured cases. Raising it to a failure would break every
existing consumer that never opted in, which §NXP.7 forbids. The fix is **visibility**, not a
new gate. The advisory MUST name the actual basename found and the exact compliant target so
the operator can act without reading the spec.

Reuse `board_name_violation` (`tools/workspace/board_names.py:94`) with `strict=True` for this
advisory. Do **not** fork the predicate.

---

## §NXP.6 — N4. Bare-board-name advisory in `ok status`

When `workspace:` is **absent** and the resolved handover or roadmap basename is bare/legacy per
`board_name_violation`, `ok status` emits one advisory line naming the compliant target.

When `docs.lanes` is configured, evaluate **every** lane's handover and roadmap basenames and
emit **at most one** advisory line, naming the count of non-compliant lanes and the first
offending basename. Rationale: one line keeps `ok status` readable; the operator gets the exact
first target and can re-run per lane. When `docs.lanes` is unset, evaluate the single configured
pair.

**This is a warn, never a gate.** It MUST NOT contribute to `--exit-code`, MUST NOT change the
frozen exit precedence (`2 > 6 > 35 > 3 > 0`), and MUST NOT block DONE. Rationale: board naming
is an operator hygiene preference; the kit's hard gates are reserved for correctness failures
(substrate, muse-sync, footprint integrity). Turning a naming preference into a gate would
false-close working consumer repos.

---

## §NXP.7 — N5. Hook sequencing (frozen decision)

Session hooks are **not** disabled, discouraged, or removed by this phase.

Frozen ordering: the exploration-backlog idea *"Auto-enable session hooks on `ok sync`"* MUST
NOT be promoted to a build phase until N1 has a `pass` build verification. Enabling hooks more
widely while blocks remain anonymous multiplies the exact ambiguity this phase closes — more
repos pasting more identical headings into one chat.

Once N1 ships, wider hook enablement becomes strictly beneficial and may be freshly frozen on
its own merits.

---

## §NXP.8 — Seven-tier test matrix (NXP-b)

| Tier | Coverage |
| --- | --- |
| **unit** | `PROVENANCE_LINE_TEMPLATE` exact string + ` · ` separator; each field's fallback (`unknown` name, `-` lane); `read_at` format `YYYY-MM-DDTHH:MM:SSZ` (second precision, `Z` suffix); byte layout §NXP.3.1 steps 1–12 including both blank lines; heading still line 1; `board_name_violation` reuse (no forked predicate) |
| **integration** | `ok next` on single-lane fixture; `--lane` on two-lane fixture emits that lane; `--print-next` synonym identical bytes; `--quiet` still includes provenance; `--json` carries `repo_name`/`repo_root`/`read_at` with all pre-existing keys unchanged; `check-next` advisory in both unconfigured branches; `ok status` advisory present when bare, absent when prefixed |
| **e2e** | Two distinct fixture repos printed into one captured stream — assert each block is attributable to its own root; `ok status --exit-code` unchanged by the N4 advisory (bare-name fixture still exits on its pre-existing conditions only) |
| **stress** | Deep nested repo root; long repo names; unicode + spaces in path; very long fence body; repo root at filesystem root; `docs.lanes` with many lanes |
| **data-integrity** | Fence **body** bytes are byte-identical before/after this change (golden comparison against pre-NXP output); `CURRENT_NEXT_HEADING` unchanged; JSON pre-existing keys unchanged in name, order-independence, and type |
| **performance** | `ok next` performs no `muse`/`git` subprocess (assert via subprocess spy); added cost is config + path resolve + one clock read |
| **security** | Provenance leaks no secrets: emits repo name, absolute path, lane, timestamp only — never config values, env, tokens, or remote URLs. Absolute local path disclosure is accepted and documented (§NXP.9) |

---

## §NXP.9 — Security / privacy

The provenance line discloses an absolute local filesystem path. This is **intended** — it is
the disambiguator — and is consistent with existing kit output (`ok status` already prints repo
root context). It is local-operator-facing output. NXP-b MUST NOT add remote URLs, branch names,
tokens, or any config value beyond `repo.name` to this line.

---

## §NXP.10 — Definition of Done (NXP-b)

- N1–N4 implemented exactly as frozen; N5 recorded in `docs/ROADMAP.md` backlog row.
- Seven-tier matrix §NXP.8 green; full existing suite green with **no** regression.
- Fence body and `CURRENT_NEXT_HEADING` byte-identical to pre-NXP (data-integrity tier).
- No new hard gate; `--exit-code` precedence unchanged.
- Build verification `pass` before ROADMAP → DONE.
- Both governance docs updated together in the closing feature-branch commit (SD-17).

---

## §NXP.11 — Hard stops

- Do **not** disable, remove, or discourage session hooks.
- Do **not** rename consumer repo handovers or author consumer `workspace.yaml` in NXP-b.
- Do **not** change fence body bytes or the frozen heading.
- Do **not** introduce per-branch handover filenames (§ONS.3 A1.2).
- Do **not** make board naming a blocking gate.
- Do **not** print a NEXT block without provenance as a degrade path (§NXP.3.4).
- No merge to `main` without Tier 3.

---

## §NXP.12 — Cross-references

| Doc | Relationship |
| --- | --- |
| `docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md` | §ONS.5.4 byte layout **narrowly superseded** by §NXP.3.1; all else stands |
| `docs/archive/phases/MULTI-REPO-WORKSPACE-LANES-FREEZE.md` | §MR.6.5 board identity **activated** as advisory outside workspace mode (N3, N4) |
| `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` | Relay shape unchanged |

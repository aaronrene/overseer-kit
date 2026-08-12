# Phase ONS — Operator NEXT surfacing (portable + optional host niceties)

Status: **Reviewed → `pass` (ONS-r2).** ONS-a is **spec-only** and now frozen; no code
lands in this phase. ONS-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: ONS
outputs:
- id: ons-operator-next-surfacing
  path: docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
  frozen: true
frozen_inputs:
- id: kh1-relay-standard
  path: docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: gs-paste-ready-regen
  path: docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md
- id: check-ok
  path: docs/archive/phases/PHASE-CHECK-OK.md
- id: k8-multi-lane
  path: docs/archive/phases/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: model-labels
  path: policy/model-labels.yaml
- id: next-regen-extract
  path: tools/governance_hygiene/next_regen.py
- id: paste-block-extract
  path: tools/governance_hygiene/patch.py
- id: footprint
  path: cli/footprint.py
- id: cli-main
  path: cli/main.py
- id: handover-template
  path: templates/OVERSEER-HANDOVER.template.md
review_stamp:
  reviewed_at: '2026-08-12T17:43:55Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:242e318feb880b5d632356e625f71a99f0a724dd5281afb80db2a0080fb463d8
```

**Downstream edge:** ONS-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the operator-visible gap: disk handover/roadmap
can be correct while an open IDE tab or an old chat paste still shows a stale wave. The kit
**cannot** force any IDE to reload a tab. Master control is therefore a **portable print
contract** (CLI + skill/rule + Copilot paste). Host niceties are optional and non-blocking.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6;
uncited findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature
branch); merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| ONS-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Semantic completeness: JSON `lane` null vs name; `--print-next --lane` compose; `--print-next --all-lanes`; heading_missing-before-extract; exact hook filenames; fifth skill grep (honesty). Fixed in-tree. |
| ONS-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist dry-run clean (0 findings). Semantic re-read: portable A1–A6 locked; niceties best-effort and non-DONE-gate; GS-PASTE regen not reopened; `ok next` ≠ `ok workspace check-next`; exit `37`; no tab-reload claim; no per-branch handover names. Stamp written by `ok review --freeze`. |

---

## §ONS.0 — Simple summary

Agents already update the living handover and roadmap on disk. Operators often keep an old
editor tab or an old chat paste open, so they **see** yesterday’s next step even when the
files on disk are current. This phase freezes a portable way to **print the current
paste-ready prompt from disk** (`ok next`), and a rule that the agent’s last message after
updating those files must include that same printed fence. Optional editor extras may make
a tab more likely to refresh. They do **not** guarantee the open tab is right, and they are
**not** a gate for DONE.

**Technical summary:** add a read-only CLI `ok next` (synonym:
`ok governance-sync --print-next`) that extracts the KH1 paste-ready fence from the
config-driven handover path and prints it under a fixed heading. Fail closed if the file or
fence is missing/malformed. Vendor a skill + `alwaysApply` rule to `.cursor/` **and**
`.claude/` via existing `ok sync` footprint globs. Ship Copilot/other-assistant instruction
text (`docs/PRINT-NEXT.md` + AGENTS/install notes). Optional Cursor `stop` hook template is
opt-in, fail-open, and must not replace the portable contract. Reuse
`extract_paste_fence_body` (`tools/governance_hygiene/next_regen.py`). Do **not** regenerate
NEXT (GS-PASTE remains the sole regen surface). Do **not** add per-branch handover filenames.

---

## §ONS.1 — Verified problem (do not redesign)

| Fact | Evidence |
| --- | --- |
| One living handover filename per repo, config-driven | `.overseer/config.yaml` `docs.handover`; `cli/docs_paths.py` `living_doc_abs` / `join_docs_rel` |
| Closeout already requires roadmap + handover on the feature branch | SD-17; `cursor/rules/governance-sync.mdc`; KH1 |
| Paste fence already has an extractor | `extract_paste_fence_body` in `tools/governance_hygiene/next_regen.py` (regex `_PASTE_FENCE_RE`); `extract_paste_ready_block` in `tools/governance_hygiene/patch.py` |
| KH1 requires `### Paste-ready prompt` + `Model:` in the fence | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` H7 / H8 |
| GS-PASTE regenerates those anchors via `ok governance-sync` only | `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md` §GSP.3 |
| GS-PASTE forbade a **regen** subcommand | same §GSP.1 / §GSP.3 “Any other command MUST NOT regenerate NEXT / paste” |
| Skills vendor to Cursor **and** Claude Code; Copilot uses CLI + paste doc | `cli/footprint.py` dual dest; `docs/archive/phases/PHASE-CHECK-OK.md`; `docs/CHECK-OK.md` |
| Automations/hooks are templates, not auto-enabled | `cursor/README.md`; GFG session-end Automation is Tier 2 confirm-once |
| `ok workspace check-next` already exists (constellation relays, exit `35`) | SPEC §5; `cli/main.py` workspace subparser |
| Kit cannot force IDE tab reload | Operator problem statement; no existing CLI/API in this repo reloads editor buffers |

---

## §ONS.2 — Scope

**In scope (ONS-a freezes; ONS-b implements):**

1. Portable contract A1–A6 (§ONS.3–§ONS.8).
2. Optional host niceties B (§ONS.9) — documented as best-effort; must not replace A.
3. Seven-tier matrix (§ONS.12) and Definition of Done (§ONS.13).
4. Additive SPEC §5 row, `COMMANDS` membership, kit AGENTS / install-doc text.

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected |
| --- | --- |
| **Claiming the kit can force IDE tab reload** | False assurance; CLI/Muse/shell rewrites and dirty buffers can still stale a tab |
| **Per-branch handover file names** | Violates A1; one config-driven living path |
| **Requiring merge to `main` to “refresh” NEXT** | NEXT lives on the feature branch (SD-17); merge is Tier 3 |
| **Making tab sync a gate for DONE** | Niceties are non-blocking; BV + tests + docs remain the DONE gates |
| **Regenerating NEXT / paste via `ok next`** | GS-PASTE sole regen surface; this command is **read-only extract** |
| **Redesigning product waves / KH1 shape / GS-PASTE selector** | Operator: do not redesign |
| **Aliasing `ok next` to `ok workspace check-next`** | Different command; constellation vs paste-print |
| **ONS-b Auto implementation in the Thinking phase** | SD-3 split |
| **Live consumer `ok sync` / re-init** | Operator-gated |
| **Native Copilot Agent Skills** | GitHub does not support SKILL.md; CLI + paste is the Copilot contract (Check OK precedent) |
| **Auto-enabling Cursor hooks/Automations on `ok sync`** | Tier 2 confirm-once; same as GFG |

**GS-PASTE supersession (narrow):** `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md` §GSP.1
rejected a “Separate CLI / slash command for NEXT **regen**.” **This phase does not reopen
regen.** It adds a **read-only print** command. §GSP.3 “Any other command MUST NOT
regenerate NEXT / paste” **remains in force** for `ok next` and for
`ok governance-sync --print-next`.

---

## §ONS.3 — A1. One living handover path (invariant)

1. The living handover path is **only** the config-driven destination:
   `join_docs_rel(config.repo.root_relative_docs, handover_name)` where `handover_name` is
   `config.docs.handover` or, when `docs.lanes` is set, the selected lane’s `handover`
   (`resolve_lane_docs`, §ONS.5.8).
2. ONS-b **MUST NOT** introduce per-branch handover filenames, per-wave copies, or
   `OVERSEER-HANDOVER-<branch>.md` patterns.
3. K13 `{REPO_SLUG}-OVERSEER-HANDOVER.md` board identity (§MR.6.5) is unchanged — that is a
   **repo-slug** prefix when `workspace:` is configured, not a branch suffix.

---

## §ONS.4 — A2. Closeout still updates both docs (existing SD-17)

ONS does **not** change when or where closeout writes. Agents still update
`{{docs.roadmap_path}}` and `{{docs.handover_path}}` together on the **feature branch**.
`ok next` runs **after** those bytes are on disk. A session that updates one living doc
without the other remains incomplete under existing SD-17.

---

## §ONS.5 — A3. CLI: `ok next` (canonical) + `--print-next` (synonym)

### §ONS.5.1 — Surfaces

| Surface | Behavior |
| --- | --- |
| `ok next` | Canonical. Read-only. Print the current paste-ready fence from disk. |
| `ok governance-sync --print-next` | Synonym. **Short-circuits** to the same extractor. Does **not** run R1–R5, D1–D4, patches, commits, or marker stamps. |
| `ok governance-sync --print-next --write` | **Fail closed** — mutually exclusive. Exit `2`. Message must include `print-next mutually exclusive with --write`. |
| `ok governance-sync --print-next --all-lanes` | **Fail closed** — mutually exclusive. Exit `2`. Message must include `print-next mutually exclusive with --all-lanes`. One fence per invocation. |
| `ok governance-sync --print-next --lane NAME` | Allowed. Same `resolve_lane_docs` as `ok next --lane`. |
| `ok governance-sync --print-next --dry-run` | Allowed; `--print-next` still short-circuits (print-only). `--dry-run` does not add a plan. |
| Any other command | Must not print this heading as a substitute for `ok next` (skills may instruct agents to run `ok next`). |

`ok next` **MUST NOT** call `muse` or `git`. Config load + filesystem read only.

### §ONS.5.2 — Module + wiring (exact paths)

| Piece | Path |
| --- | --- |
| Extract + format | `tools/print_next/` (`extract_current_next`, `format_current_next`, `CurrentNextResult`) |
| Reuse | `extract_paste_fence_body` from `tools/governance_hygiene/next_regen.py` — do **not** fork the regex |
| CLI command | `cli/commands/next.py` (`run_next_command`) |
| Parser | `cli/main.py`: add `"next"` to `COMMANDS`; subparser `next`; `governance-sync` flag `--print-next` |
| Dispatch | `args.command == "next"` → `run_next_command`; `--print-next` on governance-sync → same function, skip `run_governance_sync` |

### §ONS.5.3 — Frozen heading

Exact heading string (one space before the Unicode em dash `—`, matching the operator prompt byte-for-byte):

```
## CURRENT NEXT — paste this
```

Constant name in code: `CURRENT_NEXT_HEADING`. Tests assert this exact string.

### §ONS.5.4 — Human stdout (exit 0)

Print **exactly** these bytes (UTF-8), with a trailing newline on the last line:

1. `CURRENT_NEXT_HEADING`
2. one newline
3. one newline (blank line)
4. opening fence line `` ```text ``
5. newline
6. fence **body** as returned by `extract_paste_fence_body` (no extra strip beyond what that
   function already captures)
7. if the captured body does not already end with a newline, append one newline
8. closing fence line `` ``` ``
9. newline

Do **not** prepend `### Paste-ready prompt`. That heading stays in the handover file. The
chat/CLI surface uses `CURRENT_NEXT_HEADING` plus the fence body.

`--quiet` still prints this block (the block **is** the product). Diagnostics stay on stderr.

### §ONS.5.5 — `--json` stdout (exit 0)

Single JSON object, no human wrap:

```json
{
  "ok": true,
  "path": "<repo-relative POSIX handover path>",
  "lane": "<lane id or null>",
  "heading": "## CURRENT NEXT — paste this",
  "fence": "<body>",
  "error": null
}
```

On success, `lane` is JSON `null` when `docs.lanes` is unset; otherwise the resolved
lane name string (`--lane` or `docs.default_lane`).

On failure with `--json`: `ok: false`, `fence: null`, `error` = closed reason token
(§ONS.5.7), `message` = human string. Exit code still §ONS.5.6 (not 0).

### §ONS.5.6 — Exit codes

| Code | When |
| --- | --- |
| `0` | Fence extracted and printed |
| `2` | Config error; `--print-next` combined with `--write` or `--all-lanes`; `--lane` invalid / not configured (same class as other CLI config refusals) |
| `4` | Config path outside repo root (existing `is_within_repo` refusal) |
| `37` | `EXIT_NEXT_MALFORMED` — handover missing/unreadable or fence missing/malformed (§ONS.5.7) |

Do **not** reuse `35` (`ok workspace check-next`) or `36` (`EXIT_POST_LAND_SYNC`).
Unknown command remains `1`.

Constant: `EXIT_NEXT_MALFORMED = 37` in `cli/commands/next.py` (and imported by tests).

### §ONS.5.7 — Fail-closed reasons (closed vocabulary)

stderr (non-JSON) prefix: `next: <reason> — <detail>`

| `reason` | Trigger |
| --- | --- |
| `handover_missing` | Resolved handover path does not exist on disk |
| `handover_unreadable` | Exists but cannot be read as UTF-8 text |
| `heading_missing` | Handover text has no `### Paste-ready prompt` heading (KH1 H7). Checked **before** fence extract so a stray triple-backtick elsewhere cannot become the paste fence. |
| `fence_missing` | Heading present but `extract_paste_fence_body` returns `None` |
| `fence_empty` | Body after `str.strip()` is empty |
| `model_missing` | Body does not contain the substring `Model:` (KH1 H8) |

First matching reason in the order above wins. Do **not** invent a fence from roadmap
glance, change-log, chat memory, or `next_regen` planned bytes.

### §ONS.5.8 — Flags

`ok next`:

| Flag | Meaning |
| --- | --- |
| `--lane NAME` | Use that `docs.lanes` handover. Absent `docs.lanes` or unknown name → exit `2`. |
| (globals) | `-C/--repo`, `--config`, `--json`, `-q/--quiet`, `-v/--verbose`, `--no-color` as existing CLI |

No `--write`. No `--apply`. Resolve the handover file with existing
`adapters.config.resolve_lane_docs(config, lane)` (`adapters/config.py`): `--lane` omitted
uses `docs.default_lane` when `docs.lanes` is set; `--lane` when `docs.lanes` is absent
raises `ConfigError` (CLI exit `2`); unknown lane name raises `ConfigError` (exit `2`).
Do not fork a second default-lane rule.

---

## §ONS.6 — A4. Skill + alwaysApply rule (Cursor and Claude Code)

### §ONS.6.1 — Deliverable paths

| Item | Kit source | Vendored dest (existing footprint globs) |
| --- | --- | --- |
| Skill | `cursor/skills/print-next/SKILL.md` | `.cursor/skills/print-next/SKILL.md` **and** `.claude/skills/print-next/SKILL.md` |
| Rule | `cursor/rules/print-next-closeout.mdc` | `.cursor/rules/print-next-closeout.mdc` (`alwaysApply: true`) |

`cli/footprint.py` already copies every `cursor/rules/*` file and every `cursor/skills/**`
file to both skill trees. ONS-b adds the files; it does **not** change glob logic unless a
test proves a new file is skipped (then fix the glob — do not special-case).

### §ONS.6.2 — Frozen skill/rule obligations (normative text)

Both files MUST contain all of the following substrings (tests grep them):

1. `## CURRENT NEXT — paste this`
2. `ok next`
3. `read from disk after write`
4. `Session incomplete without it`
5. `do not guarantee an accurate open tab`

Normative behavior (write this into the skill **and** the alwaysApply rule):

After **any** update to the living handover and/or roadmap, the agent’s **FINAL reply**
MUST include the full paste-ready fence under heading `## CURRENT NEXT — paste this`.
Bytes MUST come from disk **after** the write (run `ok next`, or Read the handover file
and extract the `### Paste-ready prompt` fence). Do **not** paste from memory, from an
earlier chat, or from an unsaved editor buffer. A session that updated those docs and
omits this block is **incomplete**.

Prefer native editor tools (Cursor StrReplace/Write; Claude Code Edit) for
handover/roadmap so the host is more likely to refresh an open tab. That preference is
**best-effort** and **does not** replace `ok next`.

### §ONS.6.3 — Also touch (additive one-liners, not a second protocol)

| File | Additive requirement |
| --- | --- |
| `cursor/rules/governance-sync.mdc` | Closeout list item: after writing both docs, print `ok next` / CURRENT NEXT block |
| `cursor/rules/orchestrator.mdc` | Starting-a-phase / close step: final reply includes CURRENT NEXT from disk |
| `cursor/skills/governance-sync/SKILL.md` | After apply/write of living docs, run `ok next` (or equivalent Read) and include the heading+fence in the user-visible close |
| `cursor/README.md` | Table rows for the new skill + rule; Copilot fallback `ok next` + `docs/PRINT-NEXT.md` |
| `templates/OVERSEER-HANDOVER.template.md` | Regeneration-rules list item: print CURRENT NEXT from disk after closeout |

---

## §ONS.7 — A5. Copilot / other assistants

| Item | Path | Role |
| --- | --- | --- |
| Paste prompt | `docs/PRINT-NEXT.md` | Same job as `docs/CHECK-OK.md`: CLI + paste for tools without SKILL.md |
| Kit agent doc | `AGENTS.md` | Short “Print NEXT on closeout” section: prefer `ok next`; never trust the open tab |
| Consumer stubs | `docs/consumers/scooling/OVERSEER-SETUP.md`, `docs/consumers/knowtation/OVERSEER-SETUP.md`, `docs/consumers/videofactory/OVERSEER-SETUP.md` | One paragraph each: after handover/roadmap update, print fence via `ok next` |
| Cursor README | `cursor/README.md` | Already listed in §ONS.6.3 |

`docs/PRINT-NEXT.md` MUST include:

- Fast path: `ok next` (and `ok governance-sync --print-next`)
- The heading `## CURRENT NEXT — paste this`
- Source-of-truth order (§ONS.8)
- Runtime map table (Cursor / Claude Code / Copilot) matching Check OK’s shape
- Explicit: niceties do not guarantee tab accuracy

`ok sync` already ships the alwaysApply rule to Cursor. Copilot does not load `.mdc`.
Install docs + `docs/PRINT-NEXT.md` + `AGENTS.md` are the Copilot contract. Do **not**
vendor a Copilot-only hook.

---

## §ONS.8 — A6. Operator source of truth order (frozen)

When the printed fence, the disk file, and an open tab disagree:

1. **`ok next` / the printed CURRENT NEXT fence** (this session, after the write)
2. **The handover file on disk** at the config-driven path
3. **Never** “whatever the open tab happens to show”

An old chat paste is not a source of truth. Merge to `main` is not required to refresh NEXT.

---

## §ONS.9 — B. Optional host niceties (non-blocking)

Niceties **improve odds** of tab refresh. They **do not** guarantee an accurate open tab.
CLI, Muse, shell redirects, and dirty buffers can still leave a stale tab. Niceties **MUST
NOT** replace §ONS.5–§ONS.8. Tab sync **MUST NOT** be a DONE gate.

### §ONS.9.1 — Cursor

| Nicety | Frozen HOW |
| --- | --- |
| Prefer native edit tools | Skill/rule text only (§ONS.6.2) |
| Optional `stop` hook | Kit template under `cursor/hooks/` — **not** auto-enabled; **not** added to `resolve_footprint` in this phase (same posture as `cursor/automations/`) |
| Tab sync | Best-effort only; no API claim |

Stop-hook template files (exact; ONS-b must not invent extra names):

| Path | Contents |
| --- | --- |
| `cursor/hooks/README.md` | Enable instructions; honesty sentence; Tier 2 confirm-once; not in footprint |
| `cursor/hooks/print-next-stop.json` | A **snippet** to merge into a project `.cursor/hooks.json` — not a full overwrite of consumer hooks |

Stop-hook snippet requirements:

- Event: `stop`
- `failClosed`: **false** (fail open)
- `loop_limit`: `1` (at most one follow-up)
- If the agent’s last reply lacks `## CURRENT NEXT — paste this` **and** this session
  wrote the living handover or roadmap, follow up once: run or request `ok next` and
  include the heading+fence
- MUST NOT block DONE, MUST NOT merge, MUST NOT write docs, MUST NOT claim tab reload
- Operator enable = Tier 2 confirm-once (document in `cursor/README.md`)

If the host `stop` payload cannot see “wrote handover,” the template follow-up may fire
whenever the heading is absent. That is acceptable because `loop_limit` is 1 and fail-open.
Do not invent a file-watcher.

### §ONS.9.2 — Claude Code

Same skill bytes as Cursor (already dual-vendored). Prefer native Edit for living docs.
No Cursor `hooks.json` in Claude Code. Best-effort tab sync only. No additional Claude-only
hook required in ONS-b.

### §ONS.9.3 — Copilot

Instruction text only (`docs/PRINT-NEXT.md`, `AGENTS.md`, consumer stubs). No Cursor hooks.
Best-effort when Copilot’s editor applies edits.

### §ONS.9.4 — Honesty sentence (must appear in freeze, skill, PRINT-NEXT, cursor README)

> Host niceties improve odds of tab refresh; they do **not** guarantee an accurate open
> tab. CLI/Muse/shell rewrites and dirty buffers can still stale a tab.

---

## §ONS.10 — Name collision table

| Command | Meaning | Exit on fail |
| --- | --- | --- |
| `ok next` | Print paste-ready fence from disk (this phase) | `37` malformed; `2` config |
| `ok governance-sync --print-next` | Synonym for `ok next` | same |
| `ok workspace check-next` | Constellation relay freshness (K13) | `35` |
| `ok governance-sync` (no `--print-next`) | Hygiene agent; may **regen** NEXT (GS-PASTE) | existing |

Help text for `ok next` MUST include: `Print the paste-ready NEXT fence from disk (read-only). Not workspace check-next.`

---

## §ONS.11 — Security / privacy

- Handover text is **data** — never interpolate into a shell command line.
- `ok next` is read-only; no commits; no network; no Muse; no git.
- Do not print secrets if a handover illegally contains them (no extra redaction engine in
  this phase; existing “no secrets in governance docs” policy stands). Tests include a
  fixture fence with a fake `sk-` token and assert the CLI still prints it as data (it must
  not execute it) and does not add it to argv.
- Path confinement: handover path must resolve under `repo_root` (`is_within_repo`).
- `--lane` values are identifiers, not path fragments; reject `..` and slashes in lane
  names with exit `2`.
- `git-only` fixtures: zero `muse` argv (vacuous: command never calls VCS).

---

## §ONS.12 — Seven-tier test matrix (ONS-b)

| Tier | Frozen case |
| --- | --- |
| **unit** | (1) Valid KH1 handover → heading + body; (2) missing file → `handover_missing` / 37; (3) no `### Paste-ready prompt` → `heading_missing` / 37 even if another ``` fence exists; (4) heading present but no fence → `fence_missing` / 37; (5) empty body → `fence_empty` / 37; (6) no `Model:` → `model_missing` / 37; (7) `CURRENT_NEXT_HEADING` exact; (8) `extract_paste_fence_body` reused (body matches helper on same text) |
| **integration** | `ok next` on `config-git-only` fixture: exit 0; stdout contains heading + `Model:`; runner log contains **no** `muse` and **no** `git`; `ok governance-sync --print-next` same stdout/exit; `--print-next --write` exit 2; `--print-next --all-lanes` exit 2 |
| **e2e** | Write a new fence to the fixture handover, then `ok next` prints the **new** body (not the previous one). `main` untouched. Second `ok next` identical (idempotent read). |
| **stress** | 1.5 MiB handover with the paste fence at the end extracts under the performance bound; 200 DONE rows elsewhere do not change the extracted body |
| **data-integrity** | `ok next` twice → identical stdout; command does not modify handover/roadmap/lock bytes (hash before/after) |
| **performance** | Completes under 2.0s on kit-sized handover in the existing test harness (no unbounded `docs/` walk) |
| **security** | Path escape (`--config` outside repo) → 4; lane name `../x` → 2; git-only fixture zero Muse argv; skill+rule files contain the five required substrings (§ONS.6.2); `docs/PRINT-NEXT.md` contains the honesty sentence (§ONS.9.4); `cursor/hooks/print-next-stop.json` has `failClosed` false |

---

## §ONS.13 — Definition of Done (ONS-b)

- [ ] `ok next` and `ok governance-sync --print-next` implement §ONS.5
- [ ] Fail-closed reasons + exits `0`/`2`/`4`/`37` as frozen
- [ ] Skill + alwaysApply rule vendored to `.cursor/` and `.claude/` via `ok sync` globs
- [ ] Copilot path: `docs/PRINT-NEXT.md` + AGENTS + consumer-stub paragraph
- [ ] Host niceties documented as best-effort; optional hook not auto-enabled; honesty sentence present
- [ ] SPEC §5 additive `ok next` row; `COMMANDS` includes `next`
- [ ] Seven-tier §ONS.12 green locally; git-only fixture proves no Muse
- [ ] `/build-verification-review` → `pass` before ROADMAP ONS-b **DONE**
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17)
- [ ] No consumer re-init; no feature→GitHub-`main`; no secrets
- [ ] ONS-b Auto does **not** mark tab sync as a DONE gate

---

## §ONS.14 — Hard stops

- No ONS-b Auto implementation during ONS-a
- No merge to `main` / staging push / live posture flips without Tier 3
- No live consumer re-init
- No inventing a paste fence when extraction fails
- No claiming IDE tab reload
- No per-branch handover filenames
- No Muse required for baseline green

---

## §ONS.15 — Auto paste (ONS-b) — frozen for handover after ONS-a `pass`

```text
You are Auto on overseer-kit — ONS-b Operator NEXT surfacing.

Model: Auto
Repo: overseer-kit
Branch: feat/ons-operator-next-surfacing
Step: ONS-b
Authority: authoritative

Read first (frozen; do not redesign):
- docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md
- docs/ROADMAP.md row ONS-b
- docs/OVERSEER-HANDOVER.md

Build ONS-b and ONLY ONS-b:
- tools/print_next/ + cli/commands/next.py + ok next + governance-sync --print-next
- cursor/skills/print-next/SKILL.md + cursor/rules/print-next-closeout.mdc
- docs/PRINT-NEXT.md + AGENTS.md + consumer stub paragraphs + SPEC §5 row
- optional cursor/hooks/ template (not footprint, failClosed false)
- seven-tier §ONS.12; /build-verification-review → pass
- update ROADMAP ONS-b + handover; feature-branch commit

Do NOT: regenerate NEXT (GS-PASTE); alias workspace check-next; auto-enable hooks;
claim tab reload; merge to main; live consumer sync; start other phases.

Model: Auto
```

---

## §ONS.16 — Cross-references

- `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — H7/H8 paste shape
- `docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md` — sole regen surface
- `docs/archive/phases/PHASE-CHECK-OK.md` — dual skill vendor + Copilot paste doc
- `docs/archive/phases/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md` — `--lane`
- `docs/OVERSEER-KIT-SPEC.md` §5 — CLI table (ONS-b additive row)
- `policy/test-tiers.yaml` — seven tiers
- `cli/footprint.py` — rules + dual skills glob
- `tools/governance_hygiene/next_regen.py` — `extract_paste_fence_body`

# Phase Track Q / Q2a — Freeze OK CLI entrypoint (Thinking freeze)

Status: **Reviewed → `pass` (Q2a-r2).** Q2a Thinking is **spec-only** and now frozen; no code,
no shim file, and no template edit land in this phase. The Track Q / Q2b Auto build (`{step}b`)
is cleared to start mechanically against this frozen contract; it is the only phase that writes
shim/docs/CI naming files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-Q-Q2A
outputs:
- id: track-q-q2a-ok-cli-entrypoint
  path: docs/archive/phases/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md
  frozen: true
frozen_inputs:
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: k4-global-conventions
  path: docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
- id: q0-overseer-app
  path: docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md
- id: kit-boundary
  path: AGENTS.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap-track-q-rows
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T18:02:16Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:dbfbf9ad6a32b139d86eb8ab0691382427655dcd5a58b6cd7a83e02dbc714cad
```

**Downstream edge:** the Track Q / Q2b OK CLI entrypoint Auto build treats this document as ground
truth without re-deriving it (SPEC §6 mandatory reviewed freeze). Track Q / Q3 Tauri packaging
consumes Q2b's shipped canonical launcher name (`ok app`) as ground truth for the desktop
launcher — it does not reopen this Q2a naming scope. Prior frozen contracts that still spell
commands as `overseer <subcommand>` (K4, Q0, etc.) remain historically valid; Q2a amends the
**entrypoint name only**, with `overseer` retained as a compatibility synonym.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| Q2a-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist initially **blocked** on C4 absolute-path false positive (placeholder path with a leading slash). Semantic review added completeness findings below. No `irreversible`/`real_money`/`gates_tier3` escalation. |
| Q2a-r1 fix | Author (cited items only) | — | **R1-C4** fixed: skill-path example no longer uses a leading-slash absolute form. **R1-M1** fixed: existing-test stderr migration rule. **R1-M2** fixed: SPEC §5 command table must rewrite to `ok`. **R1-N1** fixed: Q2a DoD uses `./cli/overseer review --freeze`. **R1-N2** fixed: twin `.cursor/` + `cursor/` skill trees named. |
| Q2a-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1 items RESOLVED: canonical `cli/ok` + compat `cli/overseer` with exact one-line stderr deprecation; `prog="ok"`; engine shims excluded from footprint; SPEC §5 table rewrite mandatory; existing-test stderr migration frozen; twin skill trees named; seven-tier §Q2A.10 complete; hard stop on silent `overseer` removal; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `overseer review --freeze`. |

---

## §Q2A.0 — Simple summary

Operators currently invoke the kit as `overseer …`. The public product brand is **🆗 Overseer Kit**,
and the short, intentional CLI name is **`ok`**. This phase freezes that rename as a first-class
POSIX entrypoint — not a shell alias — so docs, CI, and the future Tauri desktop launcher all use
the same name.

**Technical summary:** freeze canonical shim `cli/ok` → `python -m cli.main`; set argparse
`prog="ok"`; keep `cli/overseer` as a compatibility shim that runs the **same** runtime and prints
exactly one deprecation line to stderr per process; amend K4/SPEC §5 entrypoint naming only —
**no** subcommand, exit-code, or `.overseer/` path changes.

---

## §Q2A.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Canonical entrypoint name `ok` and shim path `cli/ok` (§Q2A.3).
- Compatibility shim `cli/overseer` + deprecation rule (§Q2A.4).
- Argparse `prog` + help/usage surface (§Q2A.5).
- Operator-doc / template / CI naming preference (§Q2A.6).
- Relationship to prior frozen contracts (K4, SPEC §5, Q0) (§Q2A.7).
- Explicit non-changes: subcommands, exit codes, config paths (§Q2A.8).
- Q2b Auto build file list + SPEC amendment duties (§Q2A.9).
- Seven-tier test matrix Q2b must satisfy (§Q2A.10).
- Boundary + hard stops (§Q2A.11).

**Out of scope (explicit non-goals — prevent creep):**

- **Any subcommand add/remove/rename.** `COMMANDS` membership and per-command flags stay as shipped
  (including `app` from Q1).
- **Any exit-code renumbering** (shared `0–6` taxonomy and later extensions `7+` unchanged).
- **Any `.overseer/` path change** (`config.yaml`, `version.lock`, policy, ledger, etc.).
- **Vendoring `cli/ok` or `cli/overseer` into the consumer footprint.** Per K4.5 / SPEC §5, the
  engine (`adapters/`, `tools/`, `cli/`) is carried by the CLI and pinned by `kit_version` — it is
  **not** copied file-by-file into every repo. Q2b does **not** add a footprint or `version.lock`
  manifest row for either shim.
- **Silent removal of `cli/overseer`.** Compatibility shim is mandatory in Q2b and remains until a
  later Thinking freeze authorizes removal (with a migration window).
- **Tauri / native packaging** — Track Q / Q3 only; Q2a freezes that Q3's launcher invokes `ok app`.
- **Changing the public product brand** ("🆗 Overseer Kit") or the repo slug (`overseer-kit`).
- **Tier-3 merge, staging push, or live capability flips** — this freeze never authorizes them.
- **New governance capabilities, HTTP surface changes, or engine rewrites.**

---

## §Q2A.2 — Product boundary

| Concern | Q2a / Q2b | Not Q2a / Q2b |
| --- | --- | --- |
| What changes | Entrypoint **name** + shim files + operator-facing invocation spelling | Subcommands, gates, adapters, honesty ledger |
| Where shims live | Kit engine tree: `cli/ok`, `cli/overseer` | Consumer vendored footprint |
| Who runs them | Operator / CI / Q3 Tauri launcher against a kit checkout or install | Remote hosted CLI SaaS |
| Compatibility | `overseer` keeps working with one stderr deprecation line | Breaking cutover that drops `overseer` |

---

## §Q2A.3 — Canonical entrypoint (frozen)

**Canonical name:** `ok`

**Canonical POSIX shim path (kit engine):** `cli/ok`

**Shim behavior (frozen — mirrors today's `cli/overseer` mechanics):**

1. `#!/usr/bin/env sh` with `set -eu`.
2. Resolve kit root as the parent of `cli/`.
3. Prepend kit root to `PYTHONPATH`.
4. Prefer `$ROOT/.venv/bin/python3` when executable; else `python3`.
5. `exec` that interpreter as `python -m cli.main` with all remaining arguments forwarded unchanged
   (`"$@"` only — no shell evaluation of operator args).
6. Executable bit set on the file (same as `cli/overseer` today).
7. **No** deprecation line when invoked as `ok`.

**Implementation note (frozen):** `cli/ok` and `cli/overseer` may be near-duplicate shell scripts.
Q2b must not introduce a second Python entry module; both shims must land in `python -m cli.main`.

**Invocation forms (all equivalent at the Python runtime):**

| Form | Role |
| --- | --- |
| `./cli/ok <subcommand> …` | Canonical POSIX path |
| `ok <subcommand> …` | Canonical short name when `cli/` (or an install wrapper) is on `PATH` |
| `python -m cli.main <subcommand> …` | Direct module form; argparse `prog` is still `ok` |

**No global install required.** An optional published package wrapper may expose the `ok` console
script later; it remains a convenience only (SPEC §5), never the sole path.

---

## §Q2A.4 — Compatibility shim `cli/overseer` (frozen)

**Path:** `cli/overseer` **must remain** in the kit engine tree after Q2b.

**Runtime:** identical to `cli/ok` — same `PYTHONPATH` / venv preference / `exec python -m cli.main`
forwarding. Same exit codes. Same subcommands. Same config resolution.

**Deprecation (frozen):**

| Rule | Value |
| --- | --- |
| Channel | **stderr only** (never stdout; never inside `--json` payloads) |
| Count | **Exactly one line per process** (before `exec` into Python) |
| Emitter | The **`cli/overseer` shell shim** (not Python). Required because `exec python -m cli.main` replaces argv such that Python cannot reliably see the shim basename. |
| Exact text | `warning: 'overseer' is deprecated; use 'ok' (same commands).` |
| Trailing newline | Yes (one complete line) |
| Effect on exit code | None — deprecation is informational; exit code comes from the Python runtime only |
| Quiet / verbose | Still emitted under `-q` / `--quiet` and under `--json` (stderr is outside those contracts) |

**Hard stop:** Q2b **must not** delete, rename-away, or no-op `cli/overseer`. Removal requires a
later Thinking freeze + freeze review `pass` + explicit operator authorization.

**Direct module form:** `python -m cli.main` does **not** print the deprecation line (it is not the
`overseer` shim).

---

## §Q2A.5 — Argparse `prog` and help surface (frozen)

| Surface | Frozen value |
| --- | --- |
| `argparse.ArgumentParser(prog=…)` | `"ok"` |
| Usage / help banners | Spell the program as `ok` (e.g. `usage: ok [-h] …`) |
| Subparser help | Unchanged flags and subcommand names |
| Error messages that name the CLI | Prefer `ok` (e.g. remediation `run ok init first`) |

**Message-string migration rule for Q2b (frozen):** operator-facing strings that today say
`overseer <subcommand>` (remediation hints, listening banners, `--help` prose) **must** be updated
to `ok <subcommand>` in the same Auto build. Historical freeze artifacts under `docs/archive/phases/PHASE-*` are
**not** rewritten by Q2b except where this contract explicitly requires a SPEC / K4.1 amendment
note (§Q2A.7 / §Q2A.9).

---

## §Q2A.6 — Operator docs, templates, and CI (frozen)

**Preference rule:** after Q2b, every **operator-facing** invocation example that the kit ships
uses `ok <subcommand>` (or `./cli/ok <subcommand>` when a repo-relative path is required).

**Must update in Q2b (non-exhaustive but mandatory classes):**

| Class | Examples |
| --- | --- |
| Kit operator docs | Runbooks, quickstarts, `AGENTS.md` CLI examples that tell operators what to type |
| Vendored templates that instruct operators | Handover template reminders that name the CLI |
| Cursor / skill command examples (both twin trees) | `.cursor/skills/**` and `cursor/skills/**` examples that invoke the shim — use kit-relative `cli/ok …` (a kit-root placeholder is allowed; never a machine absolute path) |
| CI workflow examples | `templates/ci/freeze-review-github-actions.yml` and kit `.github` workflows that invoke the shim |

**Path form when a filesystem path is required:** prefer `./cli/ok` (canonical). `./cli/overseer`
may appear only in a **compatibility** note that points operators at the deprecation rule.

**Public brand vs CLI name:** the product remains **🆗 Overseer Kit**; the CLI binary/shim name is
`ok`. Docs must not conflate the brand string with the argv program name.

---

## §Q2A.7 — Amendment to prior frozen contracts (frozen)

Q2a is an **additive naming amendment**, not a reopen of K4/Q0 behavior.

| Prior artifact | Amendment |
| --- | --- |
| `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` §K4.1 | Invocation line becomes: canonical `ok <command> [options]` via `cli/ok`; `cli/overseer` is the compatibility shim per §Q2A.4. Global options, exit codes, output discipline, fail-closed / idempotency / dry-run rules are **unchanged**. |
| `docs/OVERSEER-KIT-SPEC.md` §5 | Opening sentence becomes: one entrypoint, **`ok`** (compatibility synonym **`overseer`**), runnable with no global install. **Command table rows must be rewritten to `ok …`** in Q2b (historical `overseer …` spellings do not remain in the live SPEC §5 table). Add one explicit note that `cli/overseer` remains the compatibility shim per this contract. Subcommand purposes / writes / idempotency columns are **unchanged**. |
| `docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` | Remains the freeze for the `app` **subcommand** and HTTP surface. Q2b does **not** rewrite Q0. After Q2b, operator invocation of that subcommand is `ok app` (compat: `overseer app` → deprecation line + same runtime). Q3 launches `ok app`. |

**Non-amendment (frozen):** exit-code taxonomy, repo/config resolution order, footprint membership
exclusions (engine still excluded), `version.lock` shape, and all gate wiring (KH2/KH3/etc.).

---

## §Q2A.8 — Explicit non-changes (frozen)

| Item | Status |
| --- | --- |
| Subcommand set (`init`, `sync`, `status`, `review`, `governance-sync`, `verify-step`, `honesty-status`, `ledger`, `route`, `app`, …) | Unchanged |
| Per-command flags and semantics | Unchanged |
| Exit codes `0–6` and all later extensions | Unchanged |
| `.overseer/config.yaml` path and schema keys | Unchanged |
| `.overseer/version.lock` path and shape | Unchanged |
| Footprint membership / digest algorithm | Unchanged (shims are **not** footprint members) |
| Adapter / tools engine APIs | Unchanged |
| Q0 `api/*` HTTP surface | Unchanged |

---

## §Q2A.9 — Q2b Auto build duties (frozen)

Q2b builds **mechanically** against this contract. Required deliverables:

1. **Add** `cli/ok` POSIX shim per §Q2A.3 (executable).
2. **Update** `cli/overseer` to emit the §Q2A.4 deprecation line once, then `exec` the same runtime
   as `cli/ok` (do not fork a second Python entry module).
3. **Set** `argparse` `prog="ok"` in `cli/main.py` (and align operator-facing remediation / banner
   strings per §Q2A.5).
4. **Update** operator docs / templates / skills / CI examples per §Q2A.6.
5. **Amend** SPEC §5 and K4.1 naming per §Q2A.7 (entrypoint naming only).
6. **Ship** the seven-tier test pack in §Q2A.10 (all green locally).
7. **Migrate existing tests** that invoke `./cli/overseer` (or assert empty stderr around that
   shim): either switch those invocations to `./cli/ok`, **or** update stderr assertions to expect
   exactly the §Q2A.4 deprecation line when the overseer shim is under test. Do not leave
   pre-deprecation "empty stderr" assumptions in place.
8. **Do not** add `cli/ok` or `cli/overseer` to `resolve_footprint` / `version.lock` footprint
   manifest rows.
9. **Do not** remove `cli/overseer`.
10. **Governance sync:** update `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` together; mark Q2b
    DONE only after `/build-verification-review` → `pass`.
11. **Clear Q3 gate:** after Q2b DONE, Tauri packaging may invoke `ok app` as the launcher command.

**Roadmap wording correction (frozen):** the ROADMAP Q2b row's phrase "footprint + `version.lock`
entry" is **superseded** by this contract — Q2b ships kit-engine shims + doc/CI pass, **not** a
new footprint manifest row. Q2b governance text must match this document.

---

## §Q2A.10 — Seven-tier test matrix for Q2b (frozen)

All seven tiers required before Q2b DONE (`policy/test-tiers.yaml`).

| Tier | Proves | Concrete cases (minimum) |
| --- | --- | --- |
| **unit** | Shim text + argparse prog + deprecation contract | `cli/ok` exists, is executable, contains `python -m cli.main` and does **not** contain the §Q2A.4 warning string; `cli/overseer` exists, is executable, contains the **exact** §Q2A.4 warning string (byte-identical) and `python -m cli.main`; `build_parser().prog == "ok"`; `format_usage()` / help text spells `ok` as the program name |
| **integration** | Both shims reach the same command dispatcher | Fixture repo: `./cli/ok status --json` and `./cli/overseer status --json` return structurally equivalent JSON (same keys / success path) with identical process exit code; overseer path places **exactly one** deprecation line on stderr (exact §Q2A.4 text); `ok` path places **zero** deprecation lines on stderr |
| **e2e** | Operator-doc spellings work end-to-end | Fixture: `./cli/ok status` → `./cli/ok review --freeze <artifact> --dry-run` (inert) → exit codes match pre-Q2b semantics for the same inputs; a deliberate fail-closed path's remediation string names `ok` (not `overseer`) as the primary action |
| **stress** | Deprecation does not amplify or leak across processes | M sequential `./cli/overseer status` processes (M ≥ 20): each emits exactly one warning line on stderr and nothing else attributable to the shim; no shim-created temp files under the repo; RSS/file-handle growth attributable to the shim remains flat across the M runs |
| **data-integrity** | Idempotency + non-footprint invariant + existing-test migration | Twice-run `./cli/ok status --json` → identical exit code + stable JSON fields that the status contract marks stable; `resolve_footprint(...)` destination set does **not** include `cli/ok` or `cli/overseer`; when a `version.lock` footprint list is present, it never lists those paths; the pre-Q2b test suite has no remaining assertions that require empty stderr from `./cli/overseer` (per §Q2A.9 item 7) |
| **performance** | Shim overhead bounded | `./cli/ok status --json` completes within the same wall-clock bound already enforced by the existing status performance tests (shim adds no unbounded work before `exec`) |
| **security** | No secret leak; stderr discipline; no path traversal via shim | Deprecation line contains no absolute machine paths, tokens, or identity; under `--json`, stdout remains exactly one JSON object (deprecation stays on stderr only); shims themselves perform no writes under `.overseer/`; shim does not expand or evaluate operator arguments (forwards `"$@"` only) |

**Definition of Done for Q2b (frozen):** §Q2A.9 items 1–11 complete; all seven tiers green; no
secrets committed; `/build-verification-review` → `pass`; ROADMAP + HANDOVER updated together.

---

## §Q2A.11 — Hard stops and tiers

| Stop | Rule |
| --- | --- |
| Silent breaking removal of `cli/overseer` | **Forbidden** in Q2b and afterward until a later freeze authorizes removal |
| Tier-3 merge / staging / live gate flips | **Not authorized** by this freeze |
| Q2b Auto start | **Blocked** until this artifact's freeze review → `pass` |
| Q3 Tauri start | **Blocked** until Q2b DONE (build-verified) |
| Security / irreversible / real_money findings in freeze review | Escalate to human; do not auto-fix |

**Authority:** feature-branch freeze + review fixes = Tier 1. Merge to `main` = Tier 3.

---

## §Q2A.12 — Thinking-phase Definition of Done (this phase)

- [x] This freeze artifact written under `docs/archive/phases/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md`
- [x] Freeze review → `pass` (`/freeze-review-loop` + `./cli/overseer review --freeze` on this artifact)
- [x] `docs/ROADMAP.md` Track Q / Q2a → DONE (Thinking); Q2b remains Auto TODO gated on this contract
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for Track Q / Q2b (SD-17)
- [x] **Spec-only** — no `cli/ok`, no shim edit, no template/CI edit in Q2a

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §5 (vendoring CLI), §6 (freeze review)
- `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` §K4.1 (global conventions), §K4.5 (engine excluded from footprint)
- `docs/archive/phases/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` (`app` subcommand freeze; invocation becomes `ok app` post-Q2b)
- `docs/ROADMAP.md` — Track Q / Q2a–Q3 rows
- `policy/test-tiers.yaml` — seven-tier contract
- `policy/tiers.yaml` — Tier 1 vs Tier 3

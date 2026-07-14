# Track O — Stage 3 upgrade operator runbook

Operator path for **`muse-only` → `muse+git-mirror`** using the kit ceremony
orchestrator. Ground truth: frozen
`docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md` (§O2.3–§O2.7).

**This is not product unlock.** Product Stage 3 one-click may wrap **only**
`ok upgrade-regime` after Track O / O3 build-verification → `pass` **and** the
§O2.6 checklist (explicit C6 consent; never auto C8).

**Hard stops:**

- Never edit only `vcs.regime` in `.overseer/config.yaml`
- Never `muse bridge git-export --git-dir .`
- Never `git push <remote> <main_branch>`
- Never merge `muse-mirror` → `main` without Tier-3 authorization (C8)
- No live consumer `ok init` from this runbook

---

## Prerequisites (C0)

| Check | Notes |
| --- | --- |
| Existing `.overseer/config.yaml` with `vcs.regime: muse-only` (or incomplete `muse+git-mirror` for repair) | Wrong start (`git-only` / missing) → refuse; use greenfield `ok init` or a later freeze |
| Muse substrate usable for the tree | Required for later live bridge |
| `muse` on PATH | For C7 only |
| Empty GitHub repo + `git remote add` for `vcs.git.remote` | Product/operator work before C7; enforced by G8 |

Work on a **feature branch**.

---

## Ceremony (C1–C8)

| Step | What | Writes? |
| --- | --- | --- |
| **C1** | Start-state gate (muse-only / complete / incomplete repair / refuse) | No |
| **C2** | Complete VCS write preserving `docs.*` / `repo.*` | Config |
| **C3** | Footprint re-seed (`ok sync` composition) | Bridge files + lock |
| **C4** | Footprint present in lock + disk | No |
| **C5** | Bridge dry-run gates G1–G8 (no live export) | No |
| **C6** | Explicit consent before live | No |
| **C7** | First live bridge via `./scripts/muse-bridge-deploy.sh` | Mirror + `muse-mirror` |
| **C8** | Merge PR → `main` | **Tier 3 — stop** |

---

## Commands

### Dry-run (default; product wrappers until live)

```bash
./cli/ok -C <repo> upgrade-regime --from muse-only --to muse+git-mirror --dry-run --json
```

Runs C0–C5 planning + G1–G8 report. Sets `ready_for_live_bridge: true` only when
**all** of G1–G8 pass. If G8 fails, footprint gates may still be OK separately.

### Apply (config + footprint; no live bridge)

```bash
./cli/ok -C <repo> upgrade-regime --from muse-only --to muse+git-mirror --apply
```

Performs C2–C4 writes and C5 gates. Does **not** run C7 unless `--live-bridge` is also set.

Shared-asset conflict on hand-tuned bridge files → exit `4` without `--force`. With
explicit consent:

```bash
./cli/ok -C <repo> upgrade-regime --from muse-only --to muse+git-mirror --apply --force
```

`--force` never implies `--include-preserved` (living docs stay preserved).

### Live bridge (C7 only after gates + consent)

```bash
./cli/ok -C <repo> upgrade-regime --from muse-only --to muse+git-mirror --apply --live-bridge -y
```

Requires G1–G8 pass **and** `-y` / `--yes`. Refuse `--yes` alone without gate success.
C7 failure does **not** auto-revert config/footprint to muse-only.

### Idempotent re-run

Already `muse+git-mirror` with bridge footprint OK → exit `0`, no rewrite.

### Incomplete upgrade repair

Already `muse+git-mirror` but bridge files missing/mismatched → skip C2 when VCS already
complete; continue C3–C5.

---

## After C5 / C7

1. Confirm `ok status --check-footprint`.
2. Open/update PR `muse-mirror` → `main` when `gh` available (deploy script does this).
3. **Stop before merge** — C8 is Tier 3.

Day-to-day publish remains: feature work → safe bridge → PR, never push canonical `main`.

---

## Cross-references

- Freeze: `docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`
- Product contract: `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`
- K7 dogfood: `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` / `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`
- Funnel: `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` §O0.3.3

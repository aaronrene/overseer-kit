# K7 Dogfood Operator Runbook — overseer-kit

Live Muse bind and bridge export on **this** repo are **operator-gated**. K7b kit work uses
fixtures only. Do not run live `muse bridge git-export` on the overseer-kit **development tree**.

**Hard stops (never during operator dogfood prep):**

- `muse bridge git-export --git-dir .` (or any path equal to the dev checkout)
- `git push origin main` (mirror via `muse-mirror` PR only)
- Merge `muse-mirror` → `main` without Tier-3 authorization
- Claim K7 **operational DONE** before K7.L1 (and K7.L2 when publishing) evidence is recorded

**Ground truth:** `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` (§K7.2, §K7.4).

K7b Auto ships footprint assets + tests while this repo stays **`git-only`** until the operator
flip (footprint-first per §K7.7).

---

## Prerequisites (K7.2.1)

| # | Check | Command / evidence |
| --- | --- | --- |
| 1 | `muse` on PATH | `muse --version` |
| 2 | `gh` authenticated | `gh auth status` |
| 3 | Git remote `origin` → GitHub overseer-kit | `git remote -v` |
| 4 | Muse staging remote provisioned (or defer staging push by operator decision) | `.muse/config.toml` / hub repo |
| 5 | Branch `muse-mirror` exists or may be created by first safe bridge | `gh api` / remote branch list — **not** by exporting onto `.` |
| 6 | K7b merged: bridge template + deploy script + resolver regime gate | `status --check-footprint` after config flip |

Prepared self-install config: `tests/fixtures/config-overseer-kit-dogfood.yaml` (§K7.2.3 matrix).

---

## Ordered flip steps (K7.2.2 — D1–D8)

Work on a **feature branch** unless noted Tier-3.

| Step | Action | Tier |
| --- | --- | --- |
| **D1** | Confirm clean working tree. **Do not** run any `muse bridge git-export` yet. | — |
| **D2** | Initialize / bind Muse for overseer-kit (`muse -C <abs-repo-root> …`). Writes `.muse/` locally. | 1 |
| **D3** | Flip `.overseer/config.yaml` to §K7.2.3 (`regime: muse+git-mirror`, `canonical: muse`, `mirror_branch: muse-mirror`, `coordination: null`, `working_dir: null`). | 1 |
| **D4** | Update `AGENTS.md`: regime **active** `muse+git-mirror`; SD-14 rules; remove “planned / not yet active”. | 1 |
| **D5** | `overseer sync` (or `init --migrate` if treating as migrate) — seeds `MUSE-BRIDGE-WORKFLOW.md` + `scripts/muse-bridge-deploy.sh`. | 1 |
| **D6** | Parity gate **K7.P1–K7.P10** (§K7.4) on fixtures + read-only adapter probes. | dry-run |
| **D7** | **First live bridge** only via `./scripts/muse-bridge-deploy.sh "mirror: …"` → `.muse/mirror/` → push `muse-mirror` → open/update PR to `main`. | 1 push; **Tier-3** merge |
| **D8** | Day-to-day: `muse commit` on feature branches; never `git push origin main`; mirror only via deploy script. | 1 / 3 |

### D5 example (after D3–D4)

```bash
./cli/overseer -C <repo-root> sync -y
./cli/overseer -C <repo-root> status --check-footprint
```

### D6 example

```bash
./cli/overseer -C <repo-root> governance-sync --dry-run
```

Evaluate K7.P1–P10 in `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` §K7.4.1.

### D7 example (K7.L1 — first live bridge)

```bash
./scripts/muse-bridge-deploy.sh "mirror: <summary>"
```

Uses isolated `.muse/mirror/` only. Never `--git-dir .`.

---

## Live evidence (K7.L1–L2 — not Auto-green)

| ID | Criterion | Notes |
| --- | --- | --- |
| **K7.L1** | First successful `./scripts/muse-bridge-deploy.sh` using `.muse/mirror/` only | Tier-1 remote `muse-mirror` |
| **K7.L2** | PR `muse-mirror` → `main` opened; merge only under Tier-3 | Never force-push `main` |

Record L1/L2 in `docs/OVERSEER-HANDOVER.md` change log when complete.

**K7b code DONE** ≠ **kit dogfood operational DONE** (§K7.4.2).

---

## Day-to-day after flip (K7.2.4)

1. Canonical history = MuseHub; GitHub `main` is mirror merge target only.
2. Feature work: `muse commit` on feature branches.
3. Publish: `./scripts/muse-bridge-deploy.sh "mirror: <summary>"` only.
4. Keep permanent branch `muse-mirror`.
5. **Never** `muse bridge git-export --git-dir .`.

---

## Parity quick reference (K7.P1–P10)

| ID | Check |
| --- | --- |
| P1 | Config matches §K7.2.3 |
| P2 | Footprint includes bridge workflow + deploy script; `status --check-footprint` OK |
| P3 | `AGENTS.md` active regime language |
| P4–P8 | Adapter probes + governance-sync dry-run (live or injected) |
| P9 | `git-only` still full CLI without Muse or bridge footprint |
| P10 | Rendered deploy script S3/S5/S7/S8/S11–S13 static safety |

---

## Cross-references

- `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`
- `docs/K6-PILOT-OPERATOR-RUNBOOK.md` — consumer pilots (separate)
- `AGENTS.md` — SD-14
- `docs/GIT-ONLY-QUICKSTART.md` — baseline promise (unchanged requirement)

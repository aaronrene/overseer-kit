# Public visibility checklist (maintainers · Tier 3)

Use this once before flipping `aaronrene/overseer-kit` from **private** to
**public** on GitHub. Flipping visibility is Tier 3 — a human operator action.

## Ready when all boxes are green

### Product surface

- [x] MIT `LICENSE` + matching SPDX on packaging/landing
- [x] `SECURITY.md` with private advisory path
- [x] Public landing under `docs/landing/`
- [x] Public docs index `docs/README.md`
- [x] Thin consumer boundary stubs (no private pilot trees required)
- [x] `CONTRIBUTING.md`
- [x] Migrate guide `docs/MIGRATE-EXISTING-REPO.md`

### Laundry removed from the public tree

- [x] No `docs/archive/personal/` operator paste dumps
- [x] No `docs/archive/operators/` private-tree runbooks
- [x] No `docs/archive/consumers/` detailed sister-product pilot packs
- [x] Maintainer archive limited to `phases/` + `thinking/` (kit contracts/vision)

### Secrets / history pass

- [x] Working tree scan: no PEM / private-key / `ghp_` / `sk-` / `.env*` matches
- [x] `desktop/keys/` holds **public** verifying material only
- [x] No tracked `.env*` history hits for credential filenames in this pass
- [ ] Operator spot-check: GitHub Settings → Secrets (Actions) contain only intended
      signing/API names — never commit secret values
- [ ] Operator spot-check: Issues/PR draft text has no private URLs or tokens

### Flip (operator only)

When the boxes above are acceptable:

1. GitHub → **Settings** → **General** → **Danger Zone** → **Change repository visibility** → **Public**.
2. Confirm Releases / Pages / Discussions settings match the public promise.
3. Optional follow-ups (still Tier 3): DNS cutover for `overseerkit.com` per
   `docs/landing/HOSTING.md`; enable GitHub Security advisories if not already on.

Do **not** automate this flip from CI or agent sessions.

# Muse + GitHub mirror workflow — overseer-kit

## Plain summary

**overseer-kit** uses **MuseHub** as canonical version history. GitHub receives updates only
through a **safe, isolated mirror checkout** — never by exporting onto your working tree.

## Technical summary

Regime: **`muse+git-mirror`** (`canonical: muse`). Muse branch
**`main`** is authoritative. Publish to GitHub via
`./scripts/muse-bridge-deploy.sh` → isolated `.muse/mirror/` →
**`origin/muse-mirror`** → PR → **`main`**.

```text
Muse main
    → ./scripts/muse-bridge-deploy.sh
    → .muse/mirror/
    → origin/muse-mirror
    → PR
    → main
```

## Hard rules (SD-14)

1. **Never** run `muse bridge git-export --git-dir .` (or any path equal to the development
   checkout). Bridge target is always isolated `.muse/mirror/`.
2. **Never** `git push origin main`. Mirror only via the deploy
   script → permanent **`muse-mirror`** branch → reviewed PR.
3. **`muse-mirror`** is permanent — do not delete it or hand-edit it as a
   substitute for Muse.

## Day-to-day

- Feature work: `muse commit` on feature branches in Muse.
- After merges to Muse **`main`**, publish with:

  ```bash
  ./scripts/muse-bridge-deploy.sh "mirror: <summary>"
  ```

- Staging (when used): `muse push staging` — operator-gated; deferral is
  operational, not a config change.

## Operator script

Run **`./scripts/muse-bridge-deploy.sh`** — the tokenized, cwd-safe bridge deploy script vendored
by overseer-kit for `muse+git-mirror` installs.

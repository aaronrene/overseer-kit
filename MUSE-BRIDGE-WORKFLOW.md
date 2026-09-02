# Muse + GitHub mirror workflow — overseer-kit

## Plain summary

**overseer-kit** uses **Muse** as canonical version history. **MuseHub staging**
(`staging.musehub.ai`) is the shared hub remote for that history (same posture as
Knowtation/Scooling). GitHub receives updates only through a **safe, isolated
mirror checkout** — never by exporting onto your working tree.

## Technical summary

Regime: **`muse+git-mirror`** (`canonical: muse`). Muse branch
**`main`** is authoritative. Hub: **`https://staging.musehub.ai`** → remote
**`staging`** (`aaronrene/overseer-kit`). Publish to GitHub via
`./scripts/muse-bridge-deploy.sh` → isolated `.muse/mirror/` →
**`origin/muse-mirror`** → PR → **`main`**.

```text
Muse main
    → muse push staging          (hub canonical remote)
    → ./scripts/muse-bridge-deploy.sh
    → .muse/mirror/
    → origin/muse-mirror
    → PR
    → GitHub main
```

## Hard rules (SD-14)

1. **Never** run `muse bridge git-export --git-dir .` (or any path equal to the development
   checkout). Bridge target is always isolated `.muse/mirror/`.
2. **Never** `git push origin main`. Mirror only via the deploy
   script → permanent **`muse-mirror`** branch → reviewed PR.
3. **`muse-mirror`** is permanent — do not delete it or hand-edit it as a
   substitute for Muse.
4. Do **not** leave `[hub] url` on dead `localhost:1337` for kit dogfood — use staging
   (or production when operator flips).

## Day-to-day

- Feature work: `muse commit` on feature branches in Muse.
- After merges to Muse **`main`**, publish hub + GitHub:

  ```bash
  muse push staging
  ./scripts/muse-bridge-deploy.sh "mirror: <summary>"
  ```

- First-time / catch-up hub bind (operator Tier 3): `muse hub connect https://staging.musehub.ai`,
  ensure remote repo exists, then `muse push -u staging main`.

## Operator script

Run **`./scripts/muse-bridge-deploy.sh`** — the tokenized, cwd-safe bridge deploy script vendored
by overseer-kit for `muse+git-mirror` installs.

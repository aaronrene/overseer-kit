# Muse + GitHub mirror workflow — {{repo.name}}

## Plain summary

**{{repo.name}}** uses **MuseHub** as canonical version history. GitHub receives updates only
through a **safe, isolated mirror checkout** — never by exporting onto your working tree.

## Technical summary

Regime: **`{{vcs.regime}}`** (`canonical: {{vcs.canonical}}`). Muse branch
**`{{vcs.muse.main_branch}}`** is authoritative. Publish to GitHub via
`./scripts/muse-bridge-deploy.sh` → isolated `.muse/mirror/` →
**`{{vcs.git.remote}}/{{vcs.git.mirror_branch}}`** → PR → **`{{vcs.git.main_branch}}`**.

```text
Muse {{vcs.muse.main_branch}}
    → ./scripts/muse-bridge-deploy.sh
    → .muse/mirror/
    → {{vcs.git.remote}}/{{vcs.git.mirror_branch}}
    → PR
    → {{vcs.git.main_branch}}
```

## Hard rules (SD-14)

1. **Never** run `muse bridge git-export --git-dir .` (or any path equal to the development
   checkout). Bridge target is always isolated `.muse/mirror/`.
2. **Never** `git push {{vcs.git.remote}} {{vcs.git.main_branch}}`. Mirror only via the deploy
   script → permanent **`{{vcs.git.mirror_branch}}`** branch → reviewed PR.
3. **`{{vcs.git.mirror_branch}}`** is permanent — do not delete it or hand-edit it as a
   substitute for Muse.

## Day-to-day

- Feature work: `muse commit` on feature branches in Muse.
- After merges to Muse **`{{vcs.muse.main_branch}}`**, publish with:

  ```bash
  ./scripts/muse-bridge-deploy.sh "mirror: <summary>"
  ```

- Staging (when used): `muse push {{vcs.muse.staging_remote}}` — operator-gated; deferral is
  operational, not a config change.

## Operator script

Run **`./scripts/muse-bridge-deploy.sh`** — the tokenized, cwd-safe bridge deploy script vendored
by overseer-kit for `muse+git-mirror` installs.

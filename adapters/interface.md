# VCS Adapter Interface

Canonical copy of `docs/OVERSEER-KIT-SPEC.md` §4. K2 implements these methods for three backends.

## Methods (fail-closed)

| Method | Purpose |
| --- | --- |
| `status()` | Regime, dirty tree, branch, notes |
| `read_head({ ref })` | SHA for a ref — never fabricated |
| `read_canonical_anchor()` | Muse↔Git anchor, muse tip, or origin/main |
| `realign({ dry_run, max_commits })` | Muse git-import recovery; no-op for single-history |
| `commit_feature({ branch, message, paths[] })` | Tier 1 feature-branch commit only |
| `mirror({ dry_run })` | Tier 3 mirror delta report; operator gate before push |

## Backends

| Regime | Consumers | Notes |
| --- | --- | --- |
| `muse+git-mirror` | Scooling, Knowtation | SD-14: never `git push origin main` |
| `muse-only` | MuseHub | git/mirror hard no-op |
| `git-only` | VideoFactory, external | Single-history; full governance still works |

## Backends (K2)

| Regime | Package | Notes |
| --- | --- | --- |
| `muse+git-mirror` | `adapters/muse_git_mirror/` | SD-14: never `git push origin main` |
| `muse-only` | `adapters/muse_only/` | git/mirror hard no-op |
| `git-only` | `adapters/git_only/` | Single-history; full governance still works |

Load at runtime:

```python
from adapters import load_adapter
adapter = load_adapter(repo_root)  # reads .overseer/config.yaml
```

## Cross-repo safety

Every Muse invocation uses explicit `muse -C <absolute-repo-root>` and confirms branch + HEAD before writes.

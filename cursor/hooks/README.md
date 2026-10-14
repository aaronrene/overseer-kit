# Bounded v1 hooks

Static historical hook templates are disabled. This development worktree has no
automatic hooks activated. For disposable fixtures only in this milestone,
`cli/ok -C ROOT init --hooks` or `sync --hooks` generates root/UUID-bound launchers
and read-only session hooks. Generated hook paths, cwd and workspace roots must
agree with the configured physical repository or the hook refuses without a
prompt. Hooks never regenerate NEXT, execute it, or call governance-sync.

The supported isolation matrix exercises copied hooks and foreign/multiple
workspace roots in both fixture directions. Consumer activation requires separate
authorization. See `docs/V1-QUICKSTART.md` and `docs/PRINT-NEXT.md`.

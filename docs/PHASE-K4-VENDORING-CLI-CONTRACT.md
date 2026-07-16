# Phase K4 — Vendoring CLI Contract (Frozen Thinking Outline, K4a)

Status: **Frozen contract for K4b (Auto Build). No CLI implementation in this step. No consumer
repo migration (that is K6). No live hooks/Automations. No `main` merge without review.** This doc
is the machine-checkable ground truth K4b implements mechanically against; it refines — and stays
compatible with — `docs/OVERSEER-KIT-SPEC.md` §5, and adds no code.

## Freeze-contract declaration (§6.1 schema)

```yaml
phase: K4a
outputs:
  - id: k4-cli-contract
    path: docs/PHASE-K4-VENDORING-CLI-CONTRACT.md
    frozen: true                     # K4b treats this as ground truth without re-deriving
frozen_inputs:
  - id: kit-spec-vendoring-cli
    path: docs/OVERSEER-KIT-SPEC.md#5
  - id: kit-config-schema
    path: adapters/config.py
  - id: kit-templating
    path: adapters/templating.py
  - id: kit-vcs-adapter-interface
    path: docs/OVERSEER-KIT-SPEC.md#4
  - id: kit-test-tiers
    path: policy/test-tiers.yaml
```

**Downstream edge:** K4b (Auto) → consumes `k4-cli-contract` as ground truth. Per §6, this is a
**mandatory reviewed freeze** before K4b builds. Human escalation is required only if a finding hits
`security | irreversible | real_money | gates_tier3` (this contract gates none of those — it writes
only into a consumer's own tree under Tier 1, and mirror/main are out of scope).

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-10) | Independent model (`gpt-5.3-codex`), Freeze-Step Reviewer; file+line citations | `blocked` (1 BLOCKER, 6 MAJOR, 2 MINOR) | 8 of 9 resolved this revision: init no-op/refuse rule + removed phantom `--from-config-to-same` (BLOCKER); `--only` full-lock semantics; exit-code precedence `2>6>3`; `last_governance_sync` added; exit `5` reworded to match §K4.8; absolute-path output banned; skills glob recursive; standing-decisions "(or standalone)" removed. **One MAJOR (footprint_digest trailing-newline) was missed in round 1** — see round 2. |
| 2 (2026-07-10) | Same reviewer, re-review of the revision | `blocked` (1 new BLOCKER + 1 new MINOR/security + 1 carried MAJOR) | Confirmed all 8 round-1 fixes hold. Resolved this revision: **NEW-1 (BLOCKER)** standing-decisions destination collision (all three fixtures); **NEW-2 (MINOR, security)** `--verbose` absolute-path carve-out removed — all streams repo-relative, aligned with §K4.9; **NEW-3 (carried MAJOR)** `footprint_digest` line-ending rule made normative for zero/one/many trailing newlines (§K4.7). |
| 3 (2026-07-10) | Same reviewer, confirming pass | `blocked` (1 new BLOCKER + 2 MINOR) | Confirmed NEW-1/2/3 resolved. Caught **NEW-4 (BLOCKER)**: the round-2 "skip SD on collision" rule silently dropped the ADR skeleton (SD-1/SD-3/SD-17 live only in `STANDING-DECISIONS.template.md`, not in the roadmap/coordination templates). **Resolved** by always vendoring the SD skeleton to the fixed unique path `.overseer/STANDING-DECISIONS.reference.md` and making `docs.standing_decisions` a pointer only (§K4.5). **NEW-5 (MINOR)** collision-with-handover edge — now covered by the "every footprint destination must be unique → `2`" rule. **NEW-6 (MINOR)** round-2 severity label corrected (above). |
| 4 (2026-07-10) | Same reviewer, confirming pass | **`pass`** | Confirmed NEW-4/5/6 resolved; full regression scan of §K4.1/§K4.5/§K4.6/§K4.7 + review record + test matrix found no new contradictions; SD skeleton guaranteed to ship for all fixtures with no collision. One pre-existing non-blocking `--only` ambiguity (source vs destination match) noted → pinned to **destination paths** in this revision. |

**Freeze status:** **reviewed → `pass` (round 4).** The contract is cleared for the K4b Auto build.

---

## Simple summary (no jargon)

This freezes exactly how the `overseer` command must behave for its three everyday actions — set a
repo up (`init`), pull the latest shared governance files into a repo (`sync`), and tell you where a
repo stands (`status`). It nails down every switch you can pass, every number the command hands back
when it finishes, the exact shape of the little "receipt" file (`version.lock`) that records what was
installed, and the precise, repeatable recipe for the fingerprint (`footprint_digest`) that lets the
tool notice when files have been changed. It also lists the full set of tests the build step must
write and pass before the work counts as done. Nothing here installs, edits, or merges anything —
it is the blueprint the next (mechanical) step follows.

## Technical summary

K4a freezes the argument contract, exit-code taxonomy, I/O and idempotency semantics for
`overseer init | sync | status`; the extended (spec-compatible, additive) `version.lock` shape with a
per-file manifest; the deterministic `footprint_digest` algorithm (sorted, LF-normalized,
`sha256sum`-style Merkle-of-manifest over the *rendered installed* footprint); the atomic-write /
lock-last durability rule; and the concrete seven-tier test matrix (module paths + cases) K4b must
turn green. The engine is Python (matching `adapters/`), fronted by the existing POSIX `cli/overseer`
shim. All commands are read-first and idempotent; every read is fail-closed; drift is warn-only.

---

## §K4.0 — Scope and hard stops (frozen)

**In scope for K4b (Auto Build):** implement `overseer init`, `overseer sync`, `overseer status`
exactly to this contract; the `version.lock` reader/writer; the `footprint_digest` computation; the
seven-tier tests below. Extend the existing `cli/overseer` shim to dispatch into a Python runtime
(`cli/` module) reusing `adapters/config.py`, `adapters/templating.py`, and the VCS adapter
`status()` only.

**Explicitly NOT in K4:**

| Out of scope | Belongs to |
| --- | --- |
| `overseer governance-sync` (doc patching, realign, feature-branch commit) | 9A-5 / K5 |
| `overseer review --freeze` (Freeze-Step Reviewer) | K5 |
| Any consumer-repo migration / running `init` against Scooling/Knowtation/MuseHub | K6 |
| Any live hook or Cursor Automation install | K5 |
| Any `mirror`/`realign`/write to `main` or canonical | out of kit runtime (Tier 3, human) |
| Any `main` merge of K4 work without review | governance gate |

**Adapter surface K4 may call:** only `adapter.status()` (read-only: regime, dirty, branch, notes).
`init`/`sync`/`status` never call `read_head`, `read_canonical_anchor`, `realign`, `commit_feature`,
or `mirror`. The CLI writes files into the consumer tree directly (Tier 1, no VCS commit); committing
the vendored footprint is the operator's normal feature-branch step, not the CLI's job.

---

## §K4.1 — Global conventions (frozen)

**Invocation:** `ok <command> [options]`. The canonical published entrypoint is the POSIX shim
`cli/ok`, which locates and execs the portable Python runtime. `cli/overseer` is the compatibility
shim per `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md` §Q2A.4 (same runtime; one-line stderr
deprecation per process). No global install is required; an optional packaged wrapper is a
convenience only (§5 of the spec), never the sole path.

**Repo/config resolution (frozen order):**

1. `--repo <path>` if given (absolute or relative); else
2. walk up from the current working directory to the first ancestor containing `.overseer/`
   (for `sync`/`status`) or use the current working directory (for `init`); else
3. current working directory.

The resolved repo root is always made absolute before any file operation (mirrors the cross-repo
cwd-safety rule in §4 of the spec — never act on an ambiguous relative root).
`--config <path>` overrides the config location; default is `<repo>/.overseer/config.yaml`.

**Global options (accepted by all three commands):**

| Option | Type | Meaning |
| --- | --- | --- |
| `-C, --repo <path>` | path | Repo root (see resolution order). |
| `--config <path>` | path | Config file path; default `<repo>/.overseer/config.yaml`. |
| `--json` | flag | Emit a single machine-readable JSON object on stdout; human text suppressed. |
| `-q, --quiet` | flag | Suppress non-essential stdout; errors still go to stderr. |
| `-v, --verbose` | flag | Extra diagnostic detail on stderr. |
| `--no-color` | flag | Disable ANSI color (also auto-off when stdout is not a TTY). |
| `-h, --help` | flag | Command/global help; exit 0. |
| `--version` | flag | Print kit version (from `VERSION`); exit 0. |

**Output discipline (frozen):** all human/report output goes to **stdout**; all diagnostics,
warnings, and errors go to **stderr**. `--json` prints exactly one JSON object to stdout and nothing
else on stdout. No command prints secrets, tokens, credentialed URLs, **absolute machine paths**, or
user identity (§9). **All file references in every stream — stdout, `--json`, `--verbose` stderr, and
`version.lock` — are repo-relative (POSIX);** the resolved repo root is referred to as `.`, never
printed as an absolute path. This is consistent with the blanket ban in §K4.9. Timestamps are
ISO-8601 UTC with a trailing `Z`.

**Exit-code taxonomy (frozen — shared across all commands):**

| Code | Name | Meaning |
| --- | --- | --- |
| `0` | OK | Success; clean; or "already current" no-op. |
| `1` | USAGE | Unknown command, bad/again conflicting flags, missing required arg. |
| `2` | CONFIG | Fail-closed: config missing/unparseable, unknown `overseer_config_version`, unsupported `vcs.regime`, or an adapter `ReadError` during a required read. Never guesses. |
| `3` | DRIFT | `status` only, and only with `--exit-code`: local footprint is behind/ahead of the CLI's kit version. Warn-only by default (exit 0). |
| `4` | REFUSED | A write was refused to protect existing state: existing config without `--force` (`init`), consumer-modified vendored file without `--force` (`sync`), or a would-be write to a protected/ambiguous path. |
| `5` | IO | A filesystem write failed. Per §K4.8, writes are atomic per file and `version.lock` is written last, so **no half-written file exists and the lock is never advanced on a failed run**; a partial set of footprint files may have been updated and is fully recoverable by re-running `init`/`sync` (idempotent). |
| `6` | INTEGRITY | `footprint_digest` mismatch on `--check-footprint` (with `--exit-code`), unknown `lock_version`, or `version.lock` unreadable/corrupt when required. |

**Exit-code precedence (frozen):** when more than one condition holds under `--exit-code`, the
highest-priority code wins: **`2` (fail-closed) > `6` (integrity) > `3` (drift) > `0`**. The report
payload still lists **every** condition detected (e.g. both `drift` and `footprint_integrity:
mismatch`), so a non-zero exit never hides a second finding.

**Fail-closed rule (frozen, from spec §3/§4):** if config is missing/unparseable, has an unknown
version, names an unimplemented regime, or any required adapter read errors, the command **stops and
reports the exact cause** and returns `2` — it never writes, never guesses a regime, never fabricates
state.

**Idempotency rule (frozen):** running any command twice with no external change produces the same
result and the same exit code; a second `init`/`sync` with a matching lock and identical rendered
footprint is a no-op that writes nothing.

**Dry-run rule (frozen):** `--dry-run` (supported by `init` and `sync`) reports every file it *would*
create/update/skip/conflict and writes nothing — including no `version.lock` write. This is the
inert-first default recommended for CI.

---

## §K4.2 — `overseer init` (frozen)

**Purpose:** first install into a repo — create `.overseer/config.yaml`, vendor the footprint, write
`.overseer/version.lock`.

**Options (in addition to global):**

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--regime <r>` | enum | *(detected/prompted)* | One of `muse+git-mirror \| muse-only \| git-only`; validated against `SUPPORTED_REGIMES`. |
| `--repo-name <name>` | string | *(dir name)* | `repo.name` token. |
| `--docs-dir <path>` | path | `docs` | `repo.root_relative_docs`. |
| `--from-config <path>` | path | — | Use a prepared, already-valid config verbatim instead of generating one. |
| `--force` | flag | off | Overwrite an existing `.overseer/config.yaml` and re-vendor over existing footprint files. |
| `--non-interactive` | flag | off | Never prompt; if a required value is neither supplied nor safely detectable, fail closed (`2`). |
| `--dry-run` | flag | off | Report planned writes; write nothing. |

**Behavior (frozen sequence):**

1. Resolve repo root (init uses cwd unless `-C`). If `.overseer/config.yaml` exists, apply this single
   canonical rule (in order): **(a)** if `--force` is set → re-initialize (overwrite config + re-vendor,
   subject to step 5); **(b)** else if the existing config **and** `version.lock` **and** the rendered
   footprint already match what `init` would produce → **no-op, exit `0`** ("already current"), writing
   nothing; **(c)** otherwise → **refuse, exit `4`** with a report of what differs. (There is no
   `--from-config-to-same` flag; `--from-config` only supplies the config source per its row above.)
2. Determine regime by precedence: `--regime` > `--from-config` value > detection > interactive prompt.
   Detection is advisory only (e.g. presence of a Muse bridge marker vs `.git`); **detection never
   overrides an explicit flag and never silently picks a regime in `--non-interactive` mode** — if it
   cannot be determined without guessing, exit `2`.
3. Build config from the frozen schema (`adapters/config.py`) using provided/detected values; validate
   via `load_config`. Any violation → exit `2`. Config holds **names and booleans only** — no secrets
   (§9).
4. Resolve the footprint (§K4.5): render `templates/*` with `adapters.templating.render_template`
   (fail-closed on unknown tokens), and stage `policy/*` + `cursor/*` verbatim, to their consumer
   destinations.
5. **Protect hand-authored docs:** if a destination file already exists and its bytes differ from what
   init would write, and `--force` is not set → record a **conflict** for that file and refuse the
   whole operation (exit `4`) with a per-file report. (No partial install.)
6. Write config, then all footprint files (atomic per file), then compute `footprint_digest` over the
   bytes actually written and write `version.lock` **last** (§K4.4 durability).
7. Report created/updated/skipped files and the new lock. Exit `0`.

**Idempotency:** this is exactly branch (b) of step 1 — re-running `init` when config + lock + rendered
footprint already match is a no-op (exit `0`, "already current") that writes nothing and never rewrites
`installed_at`.

**Writes:** `.overseer/config.yaml`, footprint files, `.overseer/version.lock`.

---

## §K4.3 — `overseer sync` (frozen)

**Purpose:** update the vendored footprint to the kit version the CLI carries; rewrite
`version.lock`; show a diff of changed template/policy/cursor files.

**Options (in addition to global):**

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--dry-run` | flag | off | Show the diff/plan; write nothing (recommended in CI). |
| `--diff` | flag | on (interactive) | Emit a unified diff per changed file. `--json` supersedes with structured diffs. |
| `--only <glob>` | glob | — | Restrict which footprint paths are *written* this run. **Globs match consumer *destination* (footprint) paths**, e.g. `.overseer/policy/*`, `.cursor/rules/*`, `docs/*`. Repeatable. Full-footprint classification/lock semantics defined below. |
| `--force` | flag | off | Overwrite consumer-modified vendored files (otherwise each is a refused conflict). |
| `-y, --yes` | flag | off | Apply without the interactive confirmation prompt. |

**Three-way classification per footprint file (frozen):** using the per-file `sha256` recorded in
`version.lock` as the "last vendored" baseline, the freshly rendered file as "new kit", and the
on-disk file as "current":

| current vs baseline | new-kit vs baseline | Classification | Action |
| --- | --- | --- | --- |
| same | same | unchanged | skip |
| same | different | kit-updated | update |
| different | same | consumer-modified | conflict → refuse unless `--force` (exit `4`) |
| different | different | both-changed | conflict → refuse unless `--force` (exit `4`) |
| *(file missing on disk)* | any | missing | restore (treated as update) |

**Behavior (frozen sequence):**

1. Load + validate config (fail closed → `2`). If no config exists → exit `2` with "run `overseer
   init` first".
2. Read `version.lock`; if unreadable/corrupt → exit `6`.
3. Re-render the footprint at the CLI's carried kit version.
4. Classify every footprint file (table above). Report the plan; if `--dry-run`, stop here (write
   nothing, exit `0` if no blocking conflict, else `4`).
5. If any conflict and not `--force` → refuse (exit `4`) after printing the full per-file report; no
   file is written.
6. Apply updates (atomic per file), then rewrite `version.lock` **last** with the new `kit_version`,
   recomputed `footprint_digest`, refreshed `synced_at` (unchanged `installed_at`).
7. Exit `0`.

**`--only <glob>` semantics (frozen):** globs are matched against **consumer destination (footprint)
paths** (not kit-source paths). The full footprint is always classified and reported (so the operator
sees the complete picture), but only files matching a `--only` glob are **written**. Files
outside the glob are never written and never block: an out-of-scope conflict is reported as a
**warning**, not a refusal. `version.lock` is **always rewritten over the full footprint** — in-scope
files get their new `sha256`/`source`; out-of-scope and unchanged files **retain their prior manifest
entries verbatim** — so the lock and aggregate `footprint_digest` never become partial or inconsistent.
When `--only` is used, only **in-scope** conflicts trigger the `4` refusal in step 5.

**Idempotency:** `sync` when already at the CLI's kit version with no in-scope file changes is a no-op
(exit `0`).

**Writes:** in-scope footprint files classified update/restore (all of them when `--only` is absent),
`.overseer/version.lock`.

---

## §K4.4 — `overseer status` (frozen)

**Purpose:** read-only report — kit version, lock version, drift, VCS regime, dirty tree, footprint
integrity. **Never writes.**

**Options (in addition to global):**

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--exit-code` | flag | off | Return `3` on drift / `6` on integrity mismatch (for CI). Default keeps warn-only exit `0`. |
| `--check-footprint` | flag | off | Recompute local `footprint_digest` and compare to `version.lock`; report `ok \| mismatch`. |

**Report fields (frozen — same keys in `--json` and human output):**

```json
{
  "initialized": true,
  "kit_version": "0.1.0",
  "lock": {
    "lock_version": 1,
    "kit_version": "0.1.0",
    "config_version": 1,
    "footprint_digest": "sha256:<hex>",
    "installed_at": "<iso-8601Z>",
    "synced_at": "<iso-8601Z>"
  },
  "drift": {
    "status": "current",
    "kit_version": "0.1.0",
    "lock_version": "0.1.0",
    "changed_files": []
  },
  "footprint_integrity": "ok",
  "vcs": {
    "regime": "git-only",
    "canonical": "git",
    "branch": "main",
    "dirty": false,
    "notes": []
  },
  "last_governance_sync": null,
  "warnings": []
}
```

**`last_governance_sync` (frozen):** ISO-8601Z timestamp of the last `overseer governance-sync` write,
read from a `.overseer/` marker; **`null`** until the marker exists (i.e. until 9A-5 ships or if
`governance-sync` has never run). Included for `docs/OVERSEER-KIT-SPEC.md` §5 compatibility; K4 only
*reads and reports* it and never writes it (writing the marker is 9A-5 scope).

**Drift computation (frozen):** compare `version.lock.kit_version` against the CLI-carried kit
`VERSION` using semver ordering → `current | behind | ahead`. When `behind`/`ahead`, `changed_files`
lists footprint paths that would change on `sync` (computed by dry re-render + classification, no
write). Per `thresholds.drift_warn_only`, drift is a **warning only** and exit stays `0` unless
`--exit-code` is passed.

**Footprint integrity (frozen):** with `--check-footprint`, recompute the digest over the on-disk
footprint bytes and compare to `version.lock.footprint_digest`. `ok` if equal; `mismatch` otherwise
(a file was hand-edited or the lock is stale). Reported as a warning; exit `6` only with
`--exit-code`.

**Fail-closed reads (frozen):** `status` calls `adapter.status()` for `branch`/`dirty`/`notes`. If it
returns a `ReadError`, `status` reports the exact failing command in `vcs` and exits `2` — it does not
fabricate a branch or dirty flag. If `.overseer/` is entirely absent, `status` reports
`{"initialized": false}` and exits `0` (an un-initialized repo is a valid, non-error state); a config
that is present but invalid is a fail-closed `2`.

---

## §K4.5 — Vendored footprint resolution (frozen)

The **footprint** is the exact set of files `init`/`sync` write into a consumer. Frozen membership:

| Kit source | Consumer destination | Rendering |
| --- | --- | --- |
| `templates/OVERSEER-HANDOVER.template.md` | `{{docs.handover_path}}` | token-substituted |
| `templates/ROADMAP.template.md` | `{{docs.roadmap_path}}` | token-substituted |
| `templates/STANDING-DECISIONS.template.md` | `.overseer/STANDING-DECISIONS.reference.md` (fixed, always unique) | token-substituted; **always vendored** — see SD rule below |
| `templates/CROSS-REPO-COORDINATION.template.md` | `{{docs.coordination_path}}` **only if `docs.coordination` is set** | token-substituted; skipped when coordination is null |
| `policy/*.yaml` (flat) | `.overseer/policy/*.yaml` | copied verbatim |
| `cursor/rules/*` (flat) | `.cursor/rules/*` | copied verbatim |
| `cursor/skills/**` (recursive) | `.cursor/skills/**` (structure preserved) | copied verbatim — skills are nested `cursor/skills/<name>/SKILL.md`, so the pattern is recursive and preserves each skill's subdirectory |

**Standing-Decisions rule (frozen — resolves the collision *and* guarantees the ADR skeleton ships):**
by design, `docs.standing_decisions` frequently resolves to the **same** path as `docs.roadmap` or
`docs.coordination` — the *live* SD/ADR log lives *inside* that host doc (spec §3; all three shipped
fixtures collide: `git-only`/`muse-only` set `standing_decisions == roadmap`, `muse+git-mirror` sets
`standing_decisions == coordination`). The kit ships **format only** (spec §2/§3). To deliver that
format deterministically without a destination collision:

1. `STANDING-DECISIONS.template.md` is **always vendored**, to the **fixed, always-unique** path
   `.overseer/STANDING-DECISIONS.reference.md` (a *reference skeleton*, sibling of `policy/`, never a
   live governance doc). It is never skipped and never targets a `docs/` path, so it cannot collide
   with the handover/roadmap/coordination docs. Its own "authoritative location" line still points the
   operator at `{{docs.standing_decisions_path}}`, where the **live** log is maintained (seeded from
   this reference by the operator or, later, `governance-sync`/9A-5).
2. `docs.standing_decisions` is therefore a **pointer only** (used by cross-references and governance
   tooling) — it is **not** a footprint destination, so it can freely equal `docs.roadmap` or
   `docs.coordination` with no conflict.
3. **Every actual footprint destination path MUST still be unique.** After the fixed SD reference and
   the null-coordination skip, any residual collision between two distinct templates (e.g. a config
   that set `handover == roadmap`) is a config error → **fail closed, exit `2`** (never write two
   sources to one path, never guess a winner). This keeps the `version.lock` manifest (one entry per
   `path`) and the `footprint_digest` (Merkle-of-manifest keyed by `path`) well-defined.

**Frozen exclusions from the footprint (and therefore from the digest):** `.overseer/config.yaml`
(per-repo variance), `.overseer/version.lock` (the receipt itself), the kit engine
(`adapters/`, `tools/`, `cli/` — carried by the CLI, pinned by version, not copied per-repo per
spec §5), any VCS metadata (`.git/`, Muse dirs), and any consumer file not listed above. `templates/`
support files that are not skeletons (`tokens.yaml`, `README.md`) are **not** vendored.

**Rendering is fail-closed:** unknown/unmapped tokens raise `ConfigError` (existing
`adapters.templating.substitute_tokens`) → exit `2`. Only the frozen `ALLOWED_TOKENS` set may appear.

---

## §K4.6 — `version.lock` shape (frozen)

Extends the spec §5 shape **additively** (all four original keys retained → forward/backward
spec-compatible; new keys are MINOR per §7 semver). Written at `.overseer/version.lock`, committed.

```yaml
lock_version: 1                      # schema version of THIS lock file; fail closed if unknown
kit_version: 0.1.0                   # semver of the kit at install/sync (matches VERSION)  [spec §5]
config_version: 1                    # mirrors overseer_config_version at write time         [spec §5]
installed_at: "2026-07-10T00:00:00Z" # first-init timestamp, UTC Z; stable across syncs       [spec §5]
synced_at: "2026-07-10T00:00:00Z"    # last init/sync write timestamp, UTC Z
footprint_digest: "sha256:<64-hex>"  # aggregate digest of the rendered footprint (§K4.7)     [spec §5]
footprint:                           # per-file manifest — the "last vendored" baseline for sync
  - path: docs/OVERSEER-HANDOVER.md            # consumer-relative POSIX path (rendered destination)
    source: templates/OVERSEER-HANDOVER.template.md
    sha256: "<64-hex>"                          # sha256 of the exact bytes written to `path`
  - path: .overseer/policy/tiers.yaml
    source: policy/tiers.yaml
    sha256: "<64-hex>"
  # ... one entry per vendored file, sorted by `path`
```

**Why the per-file manifest is required (frozen rationale):** `sync`'s three-way classification
(§K4.3) cannot distinguish a consumer edit from a kit update without a recorded baseline of what was
last vendored. The manifest is that baseline. It contains **digests and relative paths only** — no
secrets, no identity, no absolute paths (§9).

**No-identity rule (frozen):** the lock carries a timestamp and digests only; never a username, host,
email, token, or absolute machine path.

**Unknown `lock_version` → fail closed:** a CLI that does not understand the lock's `lock_version`
refuses to `sync` over it (exit `6`) and tells the operator to re-`init --force` or upgrade the CLI.

---

## §K4.7 — `footprint_digest` algorithm (frozen)

A deterministic, platform-independent, order-independent Merkle-of-manifest digest over the
**rendered, installed** footprint (the bytes actually written into the consumer). It identifies *this
install's* footprint content for tamper/integrity detection; drift *against the kit* is determined by
`kit_version` comparison plus dry re-render (§K4.4), not by comparing digests across repos.

**Canonical byte rules (applied before hashing — frozen):**

1. Encoding: **UTF-8, no BOM**.
2. Line endings (normative): replace **every** `\r\n` and every lone `\r` with `\n`, then hash the
   resulting bytes **exactly** — preserving **any number of trailing `\n`, including zero and two or
   more**. No trailing-whitespace stripping, no addition or removal of a final newline. (This fully
   defines the zero-, single-, and multiple-trailing-newline cases.)
3. File mode / ownership / mtime are **not** hashed (portability).

**Per-file record (frozen):** for each footprint file actually written,
`(path, sha256_hex)` where:

- `path` = destination path **relative to the repo root, POSIX separators** (`/`), never absolute.
- `sha256_hex` = lowercase hex `sha256` of the file's canonical bytes.

**Aggregate (frozen):**

1. Collect all per-file records for the resolved footprint (§K4.5). Exclude `version.lock`, config, and
   everything else outside the footprint set.
2. **Sort records by `path`** using byte-wise (code-point) ordering of the POSIX path.
3. Build the canonical manifest string — one line per record, `sha256sum`-style (two spaces between
   digest and path), LF-terminated:

   ```
   {sha256_hex}  {path}\n
   ```

4. `footprint_digest = "sha256:" + sha256(manifest_string.encode("utf-8")).hexdigest()`.
5. Empty footprint (no files) → digest of the empty manifest string (well-defined, non-error).

This yields the same digest on any OS for the same rendered content, is insensitive to filesystem
enumeration order (because sorted), and changes if any file's path or content changes. The per-file
`sha256` values in the manifest (§K4.6) are exactly the `sha256_hex` computed here.

---

## §K4.8 — Durability & atomicity (frozen)

- **Atomic per-file writes:** every file write goes to a temp file in the destination directory then
  `os.replace()` (atomic rename on the same filesystem) — no reader ever sees a half-written file.
- **Lock written last:** `version.lock` is written only **after** all footprint files (and, for
  `init`, the config) have been written successfully. A crash mid-operation therefore never leaves a
  lock whose digest disagrees with what is on disk.
- **No partial footprint on refusal:** if any file is a blocking conflict (§K4.2/§K4.3), the command
  writes **nothing** and exits `4` — all-or-nothing.
- **Dry-run writes nothing at all**, including the lock.

---

## §K4.9 — Security / privacy gate (frozen, inherits spec §9)

- No secrets, tokens, credentialed URLs, or absolute machine paths in config, lock, footprint, or any
  CLI output/log. Lock carries timestamps + digests only.
- **No hardcoded SHAs** in CLI code — the footprint digest is always computed at runtime.
- **Injection-safe:** templating uses the frozen `ALLOWED_TOKENS` fixed-key substitution; artifact/doc
  text is treated as **data**, never interpolated as shell. CLI args that become paths are validated
  and confined to the resolved repo root; no path may escape the repo root (`..` traversal rejected →
  exit `4`).
- **Least privilege:** `init/sync/status` invoke only `adapter.status()` (read-only) and local file
  writes into the consumer tree. They never call git/muse write paths, never `mirror`, never touch
  `main`/canonical. A `muse-only` regime consumer still gets full `init/sync/status` (they are
  VCS-write-free).
- **Fail-closed on every read** — config, lock, and adapter status errors all halt with the exact
  cause (`2` / `6`), never a guess.

---

## §K4.10 — Seven-tier test matrix for K4b (frozen)

Per RULE #0 and spec §10. All under `tests/` (pytest `testpaths=["tests"]`), using the existing
`RecordingRunner` (`adapters/runner.py`) to inject fail-closed adapter reads and `tmp_path` fixture
repos. No test performs a real VCS write, network call, `main` merge, or touches a real consumer repo.
All seven tiers must be green locally before K4b is DONE.

| Tier | Module(s) (new under `tests/`) | Cases that must pass |
| --- | --- | --- |
| **unit** | `tests/unit/test_cli_argparse.py`, `test_version_lock.py`, `test_footprint_digest.py`, `test_init.py`, `test_sync.py`, `test_status.py` | Arg parsing for every option/global incl. unknown flag → `1`, unknown command → `1`, `--help`/`--version` → `0`. `version.lock` read/write round-trips; unknown `lock_version` → `6`; missing keys → `6`. `footprint_digest`: determinism (same input → same hash), sort-order independence, LF/CRLF normalization equality, empty-footprint value, single-byte change flips digest. Each command's fail-closed branches (missing/invalid config → `2`; refuse-without-force → `4`). **init step-1 rule**: existing config → `--force` re-inits / matching state → `0` no-op / else → `4`. **Exit-code precedence** `2 > 6 > 3 > 0` when multiple conditions hold, with all conditions still in the payload. **`status` schema** includes `last_governance_sync: null` when the marker is absent. |
| **integration** | `tests/integration/test_cli_init_sync_status.py` | For **each** regime fixture (`git-only`, `muse-only`, `muse+git-mirror`): `init` on an empty `tmp_path` creates config + full footprint + lock; footprint destinations match §K4.5 (coordination skipped when `docs.coordination` null; **`STANDING-DECISIONS.template.md` always vendored to `.overseer/STANDING-DECISIONS.reference.md` — assert the file exists and contains the `SD-1` row**, proving the ADR skeleton actually ships even though all three fixtures set `standing_decisions` == roadmap/coordination); a synthetic config with a genuine two-distinct-template destination collision (e.g. `handover == roadmap`) → fail-closed `2`; `status` reports `current`, correct regime/branch/dirty from injected `adapter.status()`; `sync` at same version is a no-op. CLI↔templating↔config compose through the frozen interfaces. |
| **e2e** | `tests/e2e/test_full_install_cycle.py` | Full lifecycle on a fixture repo: `init` → hand-edit one vendored file → `status --check-footprint` reports `mismatch` → `sync` (kit bumped in a fixture `VERSION`) classifies files (unchanged/kit-updated/consumer-modified), refuses conflict without `--force`, applies with `--force`, rewrites lock; final `status` reports `current`. No `main`, no push, no network. |
| **stress** | `tests/stress/test_large_footprint.py` | Synthetic footprint with many `policy/`+`cursor/` files and very large rendered docs; digest + classification + status stay correct and complete without unbounded memory; `--only` over a large set writes only in-scope files yet rewrites the **full** lock, and an out-of-scope conflict is a warning (not a `4` refusal). |
| **data-integrity** | `tests/data_integrity/test_idempotency.py`, `test_atomic_writes.py` | Run-twice `init`/`sync` = identical files + identical lock (except no `installed_at` rewrite); `footprint_digest` matches an independently computed reference; simulated write failure mid-footprint (injected `OSError` on the Nth file) leaves **no** `version.lock` change and no half-written file (atomic-rename + lock-last verified); dry-run writes zero bytes. |
| **performance** | `tests/performance/test_status_bounded.py` | `status` and drift computation on a realistic-size fixture complete within a bounded wall-clock budget (assert an upper bound, e.g. sub-second on the CI fixture); no unbounded VCS scans (assert `adapter.status()` called at most once). |
| **security** | `tests/security/test_cli_injection.py`, `test_no_secret_leak.py`, `test_least_privilege.py` | Path-traversal args (`--repo`, `--config`, `--only`) cannot write outside the repo root (→ `4`); templating rejects unknown tokens (→ `2`) and never shell-interpolates doc text; no secret/identity/absolute-path string ever appears in stdout/stderr/lock (scan outputs); `init/sync/status` never invoke a VCS **write** command (assert `RecordingRunner.calls` contain no write verbs; `muse-only` fixture never invokes git); every simulated read failure fails closed (`2`). |

**Definition of Done for K4b (frozen):** all three commands behave exactly per §K4.1–§K4.9; all seven
tiers above green locally; `.overseer/version.lock` in the kit updated from `sha256:pending-k4` to the
real computed digest; no secrets/hardcoded SHAs; both governance docs updated together; feature-branch
→ commit → PR under the kit's own `git-only` rules; **no `main` merge without review** (this contract
is the reviewed freeze that gates K4b).

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §5 (vendoring CLI), §9 (security gate), §10 (seven-tier tests),
  §11 (K4 build phase) — the frozen parent spec this refines.
- `adapters/config.py`, `adapters/templating.py`, `adapters/runner.py`, `adapters/base.py` — the frozen
  engine K4b composes with (no forking).
- `policy/test-tiers.yaml` — the generic RULE #0 tier contract this matrix instantiates for K4.
- `templates/tokens.yaml` — the frozen token registry the footprint rendering obeys.

# Build verification review skill

Use **after** an Auto build phase (`{step}b`) claims deliverables are complete — **before** marking
the phase **DONE** in `{{docs.roadmap_path}}`. Invoke: **`/build-verification-review`**.

**Mandatory** in every overseer install: `.cursor/rules/build-verification-required.mdc` (alwaysApply).
Agents must not mark DONE until this skill returns **`pass`**.

This is the **honesty gate**: verify the implementation actually matches the frozen spec — not
merely that tests are green or the agent said "done."

## Purpose

Catch agent dishonesty: false completion claims, made-up behavior, tests that do not exercise real
paths, docs/marketing that overstate what shipped, and scope drift from the frozen contract.

**This did not get lost** — it was always the intent of SD-3 (`Thinking → Auto`). The kit shipped:

| Gate | When | Tool today |
| --- | --- | --- |
| **Freeze review** | Before Auto build (`{step}a`) | `freeze-review` / `freeze-review-loop` + `overseer review --freeze` |
| **Build verification** | After Auto build (`{step}b`) | **This skill** (thinking model; manual/opt-in) |
| **Mechanical proof** | During/after build | Seven-tier tests (`policy/test-tiers.yaml`) |

Tests prove code runs; **this skill** proves the code matches the **frozen spec** and the agent was
honest about what landed.

## When to use

- Auto phase `{step}b` complete; tests reported green
- Before ROADMAP row → **DONE**
- Before Tier-3 merge to `{{vcs.git.main_branch}}`
- Especially: video pipelines, billing, user-facing outputs — anywhere agents previously "approved" falsely

## Model

**Always `thinking-high`** — independent reviewer; **not** the same session that did the build if
possible (fresh chat or explicit "verifier" role). Never Auto for this gate.

## Inputs (read all)

1. Frozen spec artifact (`frozen: true` from `{step}a`) — ground truth
2. `{{docs.roadmap_path}}` — phase deliverable row
3. `{{docs.handover_path}}` — what the build session claims landed
4. **Git diff** vs feature-branch base (or `muse`/`git` log for the build commits)
5. Test files — do they assert real behavior or tautologies?
6. `overseer status` — footprint/drift if kit files touched

## Verification checklist (every item needs evidence)

| # | Check | Dishonesty signal |
| --- | --- | --- |
| V1 | Every frozen deliverable exists at the path the spec names | "Implemented" but file missing or stub |
| V2 | Public APIs match frozen interfaces (signatures, exit codes, fail-closed branches) | Spec says X; code does Y |
| V3 | Tests cover frozen test-matrix rows — not only happy path | `assert True`, empty tests, mock-only |
| V4 | No scope creep beyond frozen spec | Extra features not in contract |
| V5 | No silent deletion of frozen requirements | Spec requirement removed without spec update |
| V6 | Governance docs truthful | ROADMAP/HANDOVER say DONE but tests fail or deliverables missing |
| V7 | No secrets, injection surfaces, or unsafe defaults introduced | grep + read changed paths |
| V8 | Agent claims match verifiable git state | "All green" but diff empty or unrelated |

## Verdicts

| Verdict | Meaning | Next step |
| --- | --- | --- |
| `pass` | Implementation matches frozen spec; claims honest | Mark phase DONE; governance-sync; Tier-3 merge when ready |
| `findings` | Cited gaps — fix on feature branch | Fixer addresses citations only; **re-run this skill** |
| `blocked` | Escalating category or fundamental spec violation | Human required |

Use the same escalation categories as freeze review: `security`, `irreversible`, `real_money`,
`gates_tier3`.

## Loop (bounded)

Same pattern as `freeze-review-loop`:

- **Max rounds:** 5 (build fixes should be smaller than spec fixes)
- Reviewer → findings → fixer (cited lines only) → re-review until `pass` or stop
- Do **not** mark DONE in ROADMAP until `pass`

## Output format

```markdown
## Build verification — <phase-id> round <N>

**Verdict:** pass | findings | blocked
**Frozen spec:** <path>
**Diff scope:** <commits or file list>

### Findings
| ID | Sev | path:line | Claim vs reality |
| --- | --- | --- | --- |
| BV1 | MAJOR | src/foo.py:42 | Spec §3.2 requires fail-closed; returns success on error |

### Honest summary (only if pass)
One paragraph: what actually shipped, backed by paths in the diff.
```

## CLI helpers (non-substitute)

```bash
./cli/overseer status
# run the phase's seven-tier test command
./cli/overseer governance-sync --dry-run
```

CLI cannot replace thinking verification — run this skill after tests pass.

## Handover integration

When `{step}b` completes, NEXT block should say:

```text
Model: thinking-high.
Run build-verification-review against <frozen-spec-path> before marking <phase> DONE.
```

## Hard stops

- No merge to `{{vcs.git.main_branch}}` on `findings` or `blocked`
- No waiving V8 ("tests pass therefore done") without addressing citations
- Uncited findings invalid — re-review

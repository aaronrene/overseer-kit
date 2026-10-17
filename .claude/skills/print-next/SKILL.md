---
name: print-next
description: >-
  Display canonical NEXT through the repository-bound launcher at session entry
  and after the final local handoff/closing commit. This is an instruction-
  triggered bookend; it does not establish native host lifecycle delivery.
---

# Print canonical NEXT at entry and closeout

Before acting at session entry, verify the physical repository root and run its
bound `.overseer/bin/ok -C ROOT next`, using the actual absolute root in both
paths. At closeout repeat that command after the accepted NEXT publication and
final local closing commit. Include its validated `CURRENT NEXT — paste this`
fence verbatim in the final reply when it describes the pending task.

Use the exact bound command in `.overseer/instructions/bookends.md` where
installed. Never resolve `ok` through PATH, another checkout or an environment
override. If the command refuses, report the refusal without an actionable
fallback; a previous chat, open tab or HANDOVER fence cannot establish freshness.

Only canonical `docs/NEXT.md` supplies the prompt. Do not extract a task from
HANDOVER/ROADMAP, run governance-sync to regenerate one, or publish from a hook.
Only explicitly accepted `next-write` text with the expected prior digest may
replace NEXT. Summary updates and workspace relay checks are separate work.

When these instructions are adopted in Claude Code skills or Codex AGENTS,
label the output **instruction-triggered bookend**. They establish no native
lifecycle API or automatic host support. Generated Cursor `sessionStart`/`stop`
adapters use the same canonical reader; FPR-1 verifies fixture event handling,
with named client delivery validation deferred to FPR-4.

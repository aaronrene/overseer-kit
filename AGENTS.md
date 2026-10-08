# Overseer Kit — bounded v1 agent instructions

Owner clarification, 2026-10-08: there is no session-count ceiling. Complete the
planned local restoration, preserving a per-repository choice of Git/GitHub only
or MuseHub authority with a GitHub mirror. Git-only is a fully supported ongoing
mode; it must not require Muse installation, login, or migration. The kit project's
own intended publication flow remains Muse-first. OCI remains excluded. Read the
restoration audit in `docs/validation/V1-RECOVERY.md` before implementation. The
old budget stop is resolved; do not request a session extension again. Remote
publication, consumer access and hook activation retain their explicit boundaries.

The owner's recovery request and `docs/decisions/V1-SCOPE-RESET.md` supersede the
former v1 security prerequisites, old NEXT, and per-step freeze/approval chains.
Read that decision, ROADMAP, HANDOVER, and canonical `docs/NEXT.md`.

At each actionable turn report physical cwd, Git root, and branch/full HEAD. If the
checkout has been initialized, also report its `.overseer/config.yaml` repository
name. Current workspace identity overrides inherited instructions. Never access a
real consumer repository without explicit authorization; use disposable fixtures
for cross-repository checks.

Use the conventional `.venv` and deterministic `cli/ok` launcher. In an initialized
checkout run `ok -C ROOT status` and `ok -C ROOT next`; NEXT is read-only. Only
`next-write` publishes NEXT, with explicit context and expected prior digest. Do not
add competing prompts to ROADMAP or HANDOVER. Update both summaries together on
milestone closeout.

The supported v1 test matrix is in `docs/validation/V1-RECOVERY.md`; run the full
supported suite before a local feature commit. Preserve historical tests and
source. Do not revive OCI/native GSR/sole-writer machinery or new packet chains.

Use feature branches and review changes before merging. A feature-branch push and
pull request may be used when the owner authorizes publication; never push directly
to `main`, publish a release, deploy, initialize another consumer, or activate hooks
without explicit authority. Preserve original Muse refs and never export onto a
development tree. Restore Muse integration under the corrected scope; do not treat
the old bridge as validated for the new runtime. Bounded-v1 architecture/build
review, clean installation/rollback, and the authorized DINERO pilot are recorded in
`docs/validation/V1-RECOVERY.md`. Do not repeat closed milestones against unchanged
code or revive the superseded machinery.

At closeout report exact test counts and unresolved failures. Include the validated
CURRENT NEXT fence from disk. Do not claim independent review or final-v1 completion
from a green implementation suite alone.

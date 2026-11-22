# OverseerKit source authority and eventual MuseHub migration

Owner decision recorded November 21, 2026 (America/Los_Angeles).

The intended destination is **Muse-canonical development hosted on MuseHub** for
OverseerKit. Repository hygiene and migration qualification come first. GitHub
remains the accepted source and contribution/PR path until an explicit cutover
has passed the gates below. This decision approves the destination; it does not
change a live repository's authority, publish history, install a runtime or
activate a feature.

## Accepted compatibility prerequisite

[PR #98](https://github.com/aaronrene/overseer-kit/pull/98) merged the exact reviewed
source `887df4b81e86c579ce9a4eab721eaa80f14928c3` through merge commit
`4129ef1efd96bf67171cd039d90858dc3013b308`. The merge tree is
`23e63e5f03af139cff5acce1c6e8cdcc5983c2f5`, identical to the independently reviewed
candidate. Qualification recorded 221 passing tests, no failures or skips, one
explicit historical-fixture deselection with a tested successor, and a separate
bound disposable working fixture. This accepts the rc8 source change. It does not
install it into global or existing consumer launchers. See
[the exact compatibility contract](../MUSE-RC8-COMPATIBILITY.md).

## Required sequence

1. Preserve and disposition retained branches, stashes, dirty work and Muse
   histories. Unresolved material stays held; cleanup does not mean deletion.
2. Reconcile selected source/receipt changes and portable repository configuration
   on isolated feature branches. Existing tracked installation bindings and NEXT
   may describe the historical publication checkout; do not treat those paths or
   tasks as authority for a fresh clone. Correct portability through review, not
   by replacing original consumer state or inventing a canonical NEXT.
3. Qualify Git-to-Muse conversion and export/restore behavior across all retained
   history. Preserve provenance, complete parents/objects, executable modes and
   symlink semantics. A byte-equivalent tip or one-time chmod is insufficient.
   Retain the mode-faithful Git recovery source until replacement guarantees pass.
4. Reproduce and resolve incomplete clone delivery in disposable environments.
   Any client/server correction goes through tested review. Local recovery using
   extra objects does not establish complete server delivery.
5. Prepare exact publication and cutover manifests: source revisions, target
   identities/refs, privacy, expected live state, verification and rollback.
   Gabriel coordinates shared MuseHub publication and owns production execution.
6. Verify independent fresh clones without local fallback. Explicitly accept the
   authority cutover only after supported development, complete history and
   executable behavior are demonstrated. Decide and document GitHub's continuing
   mirror/recovery role in that cutover record.

Until step 6 is accepted, label any MuseHub representation as a publication copy
or archive with its actual limits. No automatic migration or forced ref update
follows from this roadmap. Installation into each existing consumer remains a
separate operation with preservation, dry run and a tested rollback. A global
installation is not a prerequisite to isolated repository preparation.

## Scope that remains unchanged

OverseerKit continues to support Git-only, Muse-only and controlled Git-mirror
consumer workflows. Moving the kit's own source does not make MuseHub a runtime
requirement for Git-only consumers. The hosted supported-v1 workflow remains a
manual rc5 job; local rc8 qualification is not a claim of hosted rc8 CI.

Historical decisions, reviews and releases retain their original scope. The
current roadmap and handover summarize this decision; they do not republish
canonical NEXT or authorize old embedded tasks.

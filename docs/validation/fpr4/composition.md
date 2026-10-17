# FPR-4 composition fixtures

Author validation of the integrated dispatcher/configuration/authority/bookend
boundary. This is part of the FPR-4 matrix, not independent FPR-5 review, host
lifecycle delivery, a selected integrated pilot or release acceptance.

Source opening HEAD: `6289d2823184a63e2968d2c5f6a76abab5818368`.
Runtime: `7d38764f026848d7d89d81abedfc62f1de5eefde6443d0032d770c2ff09a20d1`.
The new test file is `tests/fpr4/test_composition.py`; originals are unchanged.

The three authority cases each initialize two simultaneous disposable repositories,
with different model/default-lane settings and overlapping product/architecture
lanes. Git-only creates no Muse metadata; Muse-only and Muse+Git-mirror create no
Git checkout. Native cases use the separately installed rc5 interpreter and
verify version `0.2.1rc5` and source pin
`7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92`.
Missing prerequisites fail rather than skip.

Each pair checks both bound event adapters against exact manual canonical output
for both lanes, explicit lane selection, foreign-root refusal, and read-only
byte/mode/mtime inventories. Concurrent writers to different lanes contend on the
whole-file digest: exactly one succeeds. Git's exact closing commit remains
current, a later Git commit makes both entries stale, and any later native commit
makes both native entries stale. Republishing product leaves architecture stale;
the second repository remains byte/mode/mtime identical throughout.

The Git nested/linked fixture verifies three checkout UUIDs, explicit-root reads,
refusal of an inherited outer launcher from the initialized nested checkout, and
branch movement confined to the linked checkout's freshness. Existing native
linked-worktree and deterministic Git/native context-race tests remain selected
by the combined matrix.

The full legacy fixture combines every optional configuration section with both
docs-at-root and nested lane paths, a missing UUID, a HANDOVER-only draft, custom
rules/skills/policies and ledger bytes. Migration dry-run is read-only, all full
settings survive exact semantic comparison, the original config backup matches
byte-for-byte, and protected content remains unchanged. A draft acquires canonical
authority only through explicit `next-write --expect-next absent`; the unpopulated
second lane refuses. A subsequent sync preview remains read-only. This fixture
checks settings preservation; restored workflow engines and bounded schema-1/2
migrations are exercised by their separately selected maintained cases.

Exact focused command and results are recorded in `composition-results.json`;
raw pytest output and XML use the `composition-first` prefix. This focused check
does not replace the single combined source/dependency selection.

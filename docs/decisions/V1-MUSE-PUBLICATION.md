# Muse-first publication — completed rc.1 source delivery

The repaired source was accepted in staging Muse, mirrored to GitHub, and accepted
through [PR #86](https://github.com/aaronrene/overseer-kit/pull/86).
The owner accepted the existing squash merge. The separately authorized
[rc.1 prerelease](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1) is published. Neither decision is pending.

## Exact accepted identities

| Item | Identity |
| --- | --- |
| Frozen recovery Git | `32254cd939885d9d6f40634997ea5b9c37ea776c` |
| Logical Muse repository | `sha256:f5863e477e2f2caf510df731720976d3d91fdd821fd5657ec8da6b57c89a3bea` |
| Accepted staging Muse revision | `sha256:106ef9e12cca7f3be3ffb2a6bd3abfa76f032dce453c9e5010d732a8d86f2e14` |
| Muse snapshot | `sha256:36037a7bad29f82f50c7ea6442672dc5df306278859119da5c1e393fead3c0aa` |
| Actual Git mirror | `9c9db93b47ceabd9a021a1d0679cb696d65cc6c2` |
| Mirror parent 1 | `3e21496f7c4eab64b6d9ab3f868c5cdcaf8cfcde` |
| Mirror parent 2 / former GitHub main | `d47291d5d9030de5ebef713da95efa978c4d8c6e` |
| Accepted GitHub main / rc.1 tag | `293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30` |
| Accepted Git tree | `735b2eb9248148e5c11d377fa79fb1f4dc11b75f` |

## Completed sequence and evidence limits

1. The repaired Git feature passed [hosted CI 37983390020](https://github.com/aaronrene/overseer-kit/actions/runs/37983390020).
2. Native non-force publication to staging feature `feat/overseer-v1-restoration-r3`
   uploaded seven commits and 108 objects. Fresh readback verified the exact
   revision, snapshot and all 861 file bytes. Staging main then fast-forwarded
   from `sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`
   to that same revision; no additional objects were required.
3. The real mirror preserved both ordered parents above, all 861 files and ten
   executable modes. It was recorded before its non-force `muse-mirror` push.
4. PR #86 passed [hosted CI 37985479580](https://github.com/aaronrene/overseer-kit/actions/runs/37985479580).
   GitHub records the squash merge at `2026-10-09T21:54:16Z`. The owner subsequently
   accepted it; this does not retroactively expand the earlier delivery permission.
5. [Accepted-main CI 37996198972](https://github.com/aaronrene/overseer-kit/actions/runs/37996198972)
   passed for the exact tag target. Its tree matches the mirror. The two-parent
   mirror history remains preserved outside the squash commit's single-parent ancestry.

Each run passed **156 / 156 / 289 tests**, with zero reported failures/errors/skips.
Native push/readback details and owner statements are retained operator records,
not separately hosted raw logs. The public [release manifest](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/release-manifest.json)
binds the reported Muse identities to the released source; GitHub CI alone does
not prove native Muse writes. See [evidence classification](../validation/V1-PUBLIC-EVIDENCE.md).

The initial mirror authority read stopped before push with `HTTPError`; an unchanged
plan/candidate retry succeeded after a fresh matching read. Native rc5 clone omitted
19 empty directories while all 861 file bytes matched. Only approved metadata was
restored in isolated readbacks. General clone fidelity is not claimed; dirty-state
verification remains required. Muse snapshots lack POSIX modes, so the ten-path
executable policy remains explicit. No production trust reset occurred.

## Separate follow-up source

The proposed `docs/v1-publication-closeout` is a new documentation-only source
change from the accepted Muse revision above, paired with GitHub base
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`. It requires a fresh isolated source
checkout, explicit reviewed file/mode inventory, a new Muse revision/snapshot,
and an exact Git mirror/PR. No such refs or commits were created during local
planning. If live bases drift, reconcile before publication; do not substitute
moving main or mutate the preserved restoration feature/main.

The kit remains Muse-first; Git-only consumers remain supported indefinitely.
Preserve rc.1's tag/assets, recovery pins/artifact URL, original edits/refs and
held release `06f988e5a078ede81c9dc664520833980a9a19a3`. Main acceptance and rc.1
publication are closed. Later docs delivery, PR acceptance and any stable release
are separate decisions. This record makes no stable or complete-product claim.

The [frozen pre-publication decision](https://github.com/aaronrene/overseer-kit/blob/293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30/docs/decisions/V1-MUSE-PUBLICATION.md)
retains the earlier planning and failed-attempt narrative. Its pending language
is historical. Later operator-held closeouts are summarized here without exposing
machine paths or presenting local logs as public downloads.

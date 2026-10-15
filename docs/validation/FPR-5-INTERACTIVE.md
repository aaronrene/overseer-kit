# FPR-5 owner-assisted observations — 2026-10-15

**Desktop rendered content/NEXT passed; actual Cursor lifecycle acceptance remains
blocked.** These are owner observations and author/coordinator evidence, not
independent adjudication or release approval. The earlier
[acceptance checkpoint](FPR-5-ACCEPTANCE.md), its raw failures and inventories
remain unchanged; its then-pending desktop observation is resolved here.

Opening HEAD: `7ee9a372e478ad251c17d8e8fd1a4118811c01b2`, sole parent
`2e8ec694def9be4a0faa4a994bf2fff3f212ab23`. Physical/Git root, branch,
`overseer-kit` name/UUID, clean state, pinned runtime and canonical NEXT matched.
No production source, native configuration, test or dependency changed.
Runtime remains `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`;
the native candidate remains
`a515148a94ffebb88e7520fb194bc0287967484896c44900e6d7ab4e7b364551`.

| Requirement | Observed result |
| --- | --- |
| Actual native desktop rendering | Owner screenshot shows the native Overseer Kit application, Connected state, correct disposable repository and Next / Handover view. Passed. |
| Canonical NEXT inside desktop | Owner copied both product and validation action blocks. Both exactly match the bound pilot CLI readback; all nonempty lines match. Chat-paste blank lines outside the blocks differ, so whole-message byte equality is not claimed. Passed. |
| Desktop shutdown | Normal quit accepted; exit zero, empty process group and unchanged pilot NEXT. Passed. |
| Actual Cursor sessionStart | Isolated Cursor reached window readiness but the owner observed a keychain gate. No actual event request, script execution or successful hook receipt was found. Blocked. |
| Actual Cursor stop | No receipt. Installed Cursor source ties this event to a model turn; closing a chat uses the separate sessionEnd event. No permitted offline completion path has been established. Blocked. |

The first desktop observation ended normally at its three-minute time limit.
A separate ten-minute helper allowed the owner to complete the observation.
The initial Cursor helper failed because its temporary Unix socket path exceeded
the client's supported length. A separate helper shortened only that temporary
path; the original failed run remains preserved. The retry kept the same pinned
outer sandbox, disposable profile and restrictions and reached window readiness.

The owner then supplied a screenshot of **Keychain Not Found**, stating that no
keychain could be found to store **Cursor Key**, with Cancel and Reset To Defaults
buttons. The owner was advised to cancel and never reset defaults. This is an
observed gate under isolation that denies real-home/account reads and keychain
service access; it does not establish damage or absence of the user's normal
keychain. No keychain, privacy setting, real profile or external-provider access
was enabled. The test process did not close after normal quit and SIGTERM, so
only its verified disposable process group was terminated with SIGKILL. The
group was then empty. This is recorded as forced cleanup, not normal Cursor
shutdown acceptance.

The pilot remains clean at `4e394520262e1447ae8b5415ae36dc75dc05197e`, UUID
`20dd0872-c7a4-5fdf-81a5-27eefa0acc2e`, with NEXT digest
`489ded7be7f530ea242e1ed5dbdce96037ec752cc63c9359eaa778aa483ba055`.
Screenshots remain at their owner-provided paths and are hashed; they are not
copied into the repository because they include unrelated background windows.
The [new evidence inventory](fpr5-interactive/ARTIFACTS.json) identifies safe
durable records and external originals. Earlier evidence is not rewritten.

## Remaining decision and boundary

Keep the selected Cursor 3.24.18 lifecycle requirement explicit and unaccepted.
Do not repeat these isolated launches or the completed matrices, desktop check,
original FINDINGS review or old pilot. Before any dependent test, resolve an
approved environment for actual lifecycle evidence or obtain an explicit owner
decision for any necessary permission or acceptance-scope change. This checkpoint
authorizes neither an exception nor a waiver. Full integrated-pilot acceptance
remains blocked by these missing host events.

All other network/account/consumer/release restrictions remain. No fetch/push,
main merge, tags, signing, live export/delivery or deployment. Preserve older
worktrees, protected refs and Muse history. Only after complete required evidence:
one final independent adjudication by a non-author, then a separate owner release
decision. Continue with GPT-6 Astra, Max reasoning, as acceptance coordinator.

ROADMAP and HANDOVER are updated together; canonical NEXT is published only
through bound `next-write`, with explicit context and opening expected digest
`e02171ecc08a485ddc365870e3a64c657c17b283f4840bd87ece59dd2f47a00f`.
The local observation closing commit must have the opening HEAD as its sole
parent. Existing passing test evidence is retained against unchanged source;
this documentation/evidence closeout does not repeat the completed matrix.

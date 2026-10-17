# FPR5-R4 repair evidence

These are repair-author results. They neither replace the original FPR-5
FINDINGS verdict nor certify the complete repaired source or release acceptance.
The original report, resource probe and raw failure evidence remain unchanged.

`verify_tree` now compares the entire prepared tree with approved source and
runtime membership. Enumeration includes hidden files, empty directories,
symlinks and special files without following directory links. Source hashes,
sizes and modes must match; manifest symlinks and hardlinked files refuse.
Unapproved paths cannot pass merely because the manifested files still match.

The existing source archive still excludes virtual environments. For local
desktop resources, `provision-runtime` creates a new conventional `.venv` from
the current interpreter and the resource's exact manifested dependency pins.
It copies the declared local distribution files with RECORD verification, without
pip, test dependencies, activation scripts, bytecode or `.pth` files. A separate
`RESOURCE-RUNTIME.json` records the resulting bytes, modes, interpreter identity
and allowed links. Verification independently resolves the same exact local
prerequisites and membership; editing that inventory cannot enroll arbitrary
runtime files. Existing `.venv` trees are never silently adopted. This remains
within `tools/ci/source_package.py`; the existing desktop pre-build command uses
the repaired verifier without a bypass or change to Tauri's resource directory.

| Run | Result | Source boundary |
| --- | --- | --- |
| `failing-before` | 17 failed, one passed | Original runtime `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`; original source package SHA-256 `6a665a6793920842b276717a66ffe1937eb13fc800a14c621dc8b0255281afc4`. Fifteen assertions expose absent membership/manifest/size guards; two additionally show the explicit runtime provisioning helper does not yet exist. |
| `passing-after` | 18 passed | Shared repaired runtime `64a075b0eea2ca53beb8d18935c0a65630e1466388c00e1465293c8763b6de8d`, stable before and after this run. Same test file bytes as failing-before. |
| `integrated` | Five passed | One frozen disposable copy of that repaired runtime; source manifest SHA-256 `ef7ea2e8b6628e0e8a5e747a5736efdcf6b735a82b33b5e7abfc748578f0d3b5`. Complete source package determinism, traversal refusal, landing-copy checks, repeated desktop source preparation and fresh full-dependency standalone entrypoints. |

The requirement regressions cover the original `.overseer/config.yaml`,
`docs/NEXT.md` and `tools/.env` contamination, additional eligible/hidden files,
empty directories, file/directory/dangling links, manifest links, a FIFO, source
size tampering, and forbidden `.venv` additions. A complete archive is unpacked,
its runtime explicitly provisioned, and actual packaged `cli/ok init`, source
`status` and bound `status` are executed on a new disposable Git fixture. The
resource tree remains verifiable after those commands. A synthetic `.venv/.env`
is then refused both as an unlisted extra and after attempted self-enrollment
in the runtime inventory.

All runs use the conventional repository `.venv`, Python 3.14.4, pytest 9.1.1,
and fresh fixture parents under `/private/tmp`. The local runtime prerequisites
are PyYAML 6.0.3, cryptography 49.0.0, cffi 2.1.0 and pycparser 3.0. Each
`*-command.json` records exact argv, working directory where different, fixture,
initial HEAD, relevant file hashes, interpreter and exit code. Corresponding
`.log` and JUnit `.xml` files retain the raw outcomes. `frozen-source-identity.json`
also computes the frozen installation's own runtime identity.

The initial HEAD for these runs remains
`4c62c17cff6c606a5e1ddf565e12353973b3bcad`: after-results include authorized
uncommitted concurrent repairs, not that original commit's source. Subsequent
repairs elsewhere may change the aggregate runtime; the root closeout and final
integrated run record the final repaired identity. The resource implementation
used here has SHA-256
`9386f14e5a1e84da2118f66dd2e78b330e9e50aa7cadcef91e1fdc6c834c6b1e`.

No network, provider, consumer hook, live delivery, Tauri/native installer build,
signing or deployment ran here. The provisioned conventional venv uses the local
platform interpreter; it is not evidence of a portable interpreter bundle or
native installer acceptance. Python 3.11's missing pinned prerequisite, named
host/version acceptance, owner platform/distribution choices and the separately
authorized new pilot remain open. The resource tree must remain quiescent between
verification and packaging. Final independent adjudication and the separate
owner release decision are reserved.

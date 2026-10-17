# Standalone Git dependency contract

The original `tests/v1/test_adoption.py::test_fresh_standalone_git_install_without_muse`
is preserved byte-for-byte. Its standalone environment copies only `yaml`, the
earlier bounded runtime contract. The combined FPR-4 run exposed this outdated
fixture assumption; a targeted reproduction failed once in 3.42 seconds. Raw
evidence is retained in `standalone-before.log` and `standalone-before.xml`.

Initialization succeeds. The failure occurs when restored `status` imports the
routing, cost/governance and honesty/provenance engines, which import
`cryptography`. Both `requirements-v1.txt` and `pyproject.toml` declare this
dependency. The full pinned set is PyYAML 6.0.3, cryptography 49.0.0, cffi 2.1.0
and pycparser 3.0. This is a dependency-provisioning fixture replacement, not an
undeclared dependency or a Muse requirement; no production patch was needed.

The explicit successor is
`tests/fpr4/test_standalone_dependencies.py::test_fresh_full_dependency_git_install_without_muse`.
It builds a fresh conventional venv and provisions exactly those four distributions
from the installation's existing venv, offline, including native extensions and
distribution metadata. It verifies exact versions, isolated module paths and an
Ed25519 sign/verify operation, and confirms Muse, pip and pytest are absent.
The actual source and repository-bound launchers execute Git init/status/next/sync
with ambient Python/Muse paths poisoned. Runtime/root binding and preserved
config/NEXT bytes are checked.

The successor passed in 6.48 seconds, with zero errors/skips. Evidence is in
`standalone-after.log`, `standalone-after.xml` and `standalone-results.json`, which
records exact commands, exit codes, dependency versions, source/runtime/test hashes
and original-file preservation. The original failure remains a failure with an
explicit successor; it is not relabelled green. This same-platform offline
provisioning exercise is separate from source-artifact distribution validation,
independent review and any named platform acceptance.

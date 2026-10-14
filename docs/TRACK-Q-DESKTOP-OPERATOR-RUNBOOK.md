# Desktop operator runbook

The current full-product restoration is source-only pending combined validation
and independent review. Prior Track Q installer history is not a distribution of
this source. No current signed/notarized installer is claimed.

Use the conventional `.venv` in the exact bound kit installation. From the selected
repository, run its bound `.overseer/bin/ok -C /absolute/repository app --open` and
enter the session credential and CSRF token printed by that process. The server
accepts loopback peers and allowed origins only. The Next / Handover tab reads
canonical `docs/NEXT.md`; the handover is a summary.

For the Tauri shell, pass `--kit-root /absolute/kit --repo /absolute/repository`.
Packaged execution resolves its resource kit beside the executable and still
requires an explicit repository. Ambient root variables are not selectors. The
launcher verifies health repository UUID/root/runtime against preflight identity
and terminates its child on failure or exit.

Prepare resources with `sh scripts/bundle-desktop-kit.sh /new/resource/destination`.
Provision that installation's conventional venv from pinned local dependencies;
a source bundle does not contain an interpreter. See [source distribution](SOURCE-DISTRIBUTION.md)
and [desktop source](../desktop/README.md). The locked native dependency set
requires Rust 1.88 or later; the ambient compiler is 1.87, while the already-installed explicit Rust 1.88 toolchain passed an offline native build after preparing resources. The Python launcher/health check is separate
from native compilation, installer signing and platform certification.

#!/usr/bin/env sh
# Local portable engine resource bundle (cli, adapters, tools and assets).
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd -P)"
# New destination only; preserve previous bundles for inspection/rollback.
DEST="${1:?usage: bundle-desktop-kit.sh NEW_DESTINATION}"
# Reserve a private directory atomically. BSD mktemp requires terminal Xs;
# an unused-name probe neither reserves the archive nor randomizes that suffix.
ARCHIVE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/overseer-desktop-source.XXXXXXXX")"
ARCHIVE="${ARCHIVE_DIR}/source.tar.gz"
"${ROOT}/.venv/bin/python" "${ROOT}/tools/ci/source_package.py" build --output "$ARCHIVE"
"${ROOT}/.venv/bin/python" "${ROOT}/tools/ci/source_package.py" unpack --archive "$ARCHIVE" --destination "$DEST"
printf '%s\n' "bundled source at $DEST; provision its conventional .venv from pinned local prerequisites before launch"

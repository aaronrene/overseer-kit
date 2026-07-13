#!/usr/bin/env sh
# Bundle the Python engine into the Tauri desktop resources directory (Track Q / Q3).
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/desktop/src-tauri/resources/kit"

rm -rf "${DEST}"
mkdir -p "${DEST}"

copy_tree() {
  src="${ROOT}/$1"
  dest="${DEST}/$1"
  if [ -d "${src}" ]; then
    mkdir -p "$(dirname "${dest}")"
    cp -R "${src}" "${dest%/*}/"
  fi
}

copy_file() {
  src="${ROOT}/$1"
  dest="${DEST}/$1"
  if [ -f "${src}" ]; then
    mkdir -p "$(dirname "${dest}")"
    cp "${src}" "${dest}"
  fi
}

for dir in adapters cli tools policy templates cursor; do
  copy_tree "${dir}"
done

for file in VERSION pyproject.toml; do
  copy_file "${file}"
done

chmod +x "${DEST}/cli/ok" 2>/dev/null || true
chmod +x "${DEST}/cli/overseer" 2>/dev/null || true

echo "bundled kit → ${DEST}"

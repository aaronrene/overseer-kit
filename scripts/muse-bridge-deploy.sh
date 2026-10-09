#!/bin/sh
# Explicit bounded-v1 mirror entry point; preparation never publishes.
set -eu
PATH=/usr/bin:/bin
export PATH
ROOT=$(CDPATH= cd -P -- "$(/usr/bin/dirname -- "$0")/.." && pwd -P)
if [ ! -x "$ROOT/.overseer/bin/ok" ]; then
  echo 'refused: initialize and explicitly select Muse with the bounded-v1 runtime' >&2
  exit 2
fi
exec "$ROOT/.overseer/bin/ok" mirror "$@"

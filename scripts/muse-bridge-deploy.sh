#!/usr/bin/env bash
# Muse+git-mirror safe bridge deploy (SD-14). Token-substituted by overseer-kit.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIRROR_REL="${MUSE_BRIDGE_MIRROR_DIR:-.muse/mirror}"
GIT_REMOTE="origin"
MIRROR_BRANCH="muse-mirror"
MAIN_BRANCH="main"
MUSE_ROOT="${REPO_ROOT}"
COMMIT_MSG="${1:-mirror: overseer bridge deploy}"

_resolve_abs() {
  local base="$1"
  local rel="$2"
  if [[ "${rel}" = /* ]]; then
    (cd "$(dirname "${rel}")" && pwd)/$(basename "${rel}")
  else
    echo "${base%/}/${rel#./}"
  fi
}

REPO_ABS="$(cd "${REPO_ROOT}" && pwd -P)"
MIRROR_ABS="$(_resolve_abs "${REPO_ROOT}" "${MIRROR_REL}")"

# S3: refuse repo-root export (blocks --git-dir .)
if [[ "${MIRROR_ABS}" == "${REPO_ABS}" ]]; then
  echo "refused: mirror directory equals repo root (destructive export blocked)" >&2
  exit 1
fi

# S4: provision / update isolated mirror checkout on mirror_branch from remote
mkdir -p "$(dirname "${MIRROR_ABS}")"
if [[ ! -d "${MIRROR_ABS}/.git" ]]; then
  if git clone --branch "${MIRROR_BRANCH}" "${GIT_REMOTE}" "${MIRROR_ABS}" 2>/dev/null; then
    :
  else
    git clone "${GIT_REMOTE}" "${MIRROR_ABS}"
    git -C "${MIRROR_ABS}" checkout -B "${MIRROR_BRANCH}" 2>/dev/null \
      || git -C "${MIRROR_ABS}" checkout "${MIRROR_BRANCH}"
  fi
else
  git -C "${MIRROR_ABS}" fetch "${GIT_REMOTE}"
  git -C "${MIRROR_ABS}" checkout "${MIRROR_BRANCH}"
fi

# S5: non-secret sentinel under REPO_ROOT (prove dev tree untouched)
SENTINEL="${REPO_ROOT}/.overseer/.muse-bridge-sentinel"
mkdir -p "$(dirname "${SENTINEL}")"
echo "muse-bridge-sentinel" > "${SENTINEL}"

# S6: track .env files before export
ENV_WAS=0
ENV_LOCAL_WAS=0
[[ -f "${REPO_ROOT}/.env" ]] && ENV_WAS=1
[[ -f "${REPO_ROOT}/.env.local" ]] && ENV_LOCAL_WAS=1

# S7: cwd-safe muse bridge git-export to isolated mirror only
muse -C "${MUSE_ROOT}" bridge git-export \
  --git-dir "${MIRROR_ABS}" \
  --git-branch "${MIRROR_BRANCH}" \
  --git-remote "${GIT_REMOTE}" \
  --exclude ".muse/*" \
  --exclude ".env" \
  --exclude ".env.local" \
  --message "${COMMIT_MSG}"

# S5 post-export sentinel check
if [[ ! -f "${SENTINEL}" ]]; then
  echo "refused: dev-tree sentinel missing after export" >&2
  exit 1
fi

# S6 post-export env check
if [[ "${ENV_WAS}" -eq 1 && ! -f "${REPO_ROOT}/.env" ]]; then
  echo "refused: .env disappeared after export" >&2
  exit 1
fi
if [[ "${ENV_LOCAL_WAS}" -eq 1 && ! -f "${REPO_ROOT}/.env.local" ]]; then
  echo "refused: .env.local disappeared after export" >&2
  exit 1
fi

# S10: optional stack audit (skip when no package.json)
if [[ -f "${REPO_ROOT}/package.json" ]] && command -v pnpm >/dev/null 2>&1; then
  (cd "${REPO_ROOT}" && pnpm audit) || true
fi

# S13: publish mirror_branch on remote (never main_branch / S8)
if ! git -C "${MIRROR_ABS}" ls-remote --exit-code "${GIT_REMOTE}" "refs/heads/${MIRROR_BRANCH}" >/dev/null 2>&1; then
  git -C "${MIRROR_ABS}" push "${GIT_REMOTE}" "${MIRROR_BRANCH}"
fi

# S9: open or update PR mirror_branch → main_branch when gh is available
if command -v gh >/dev/null 2>&1; then
  if ! gh pr list --head "${MIRROR_BRANCH}" --base "${MAIN_BRANCH}" --state open --json number -q '.[0].number' 2>/dev/null | grep -q .; then
    gh pr create \
      --base "${MAIN_BRANCH}" \
      --head "${MIRROR_BRANCH}" \
      --title "Mirror: ${COMMIT_MSG}" \
      --body "Automated muse-mirror bridge PR (SD-14)." \
      2>/dev/null || true
  fi
else
  echo "warning: gh not found; mirror branch published but no PR opened" >&2
fi

exit 0

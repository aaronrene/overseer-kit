#!/bin/sh
# sessionStart / stop hook — print CURRENT NEXT from disk (§LT.4.5, fail-open).

find_ok() {
  if [ -n "$OVERSEER_OK" ] && [ -x "$OVERSEER_OK" ]; then
    printf '%s\n' "$OVERSEER_OK"
    return 0
  fi
  if [ -x "./cli/ok" ]; then
    printf '%s\n' "./cli/ok"
    return 0
  fi
  if command -v ok >/dev/null 2>&1; then
    printf '%s\n' "ok"
    return 0
  fi
  return 1
}

OK=$(find_ok) || {
  printf '%s\n' '{"additional_context":"ok CLI not found","followup_message":"ok CLI not found"}'
  exit 0
}

CONFIG=".overseer/config.yaml"

# Enumerate docs.lanes keys. `ok next` resolves exactly one lane (docs.default_lane
# when --lane is omitted), so on a multi-lane repo a bare `ok next` presents one
# lane's NEXT as if it were the whole repo and silently misdirects every session
# whose work lives in another lane. Emit every lane instead and let the reader pick.
lane_names() {
  [ -f "$CONFIG" ] || return 0
  awk '
    /^  lanes:[[:space:]]*$/ { in_lanes = 1; next }
    in_lanes {
      if ($0 ~ /^[[:space:]]*$/) { next }
      indent = match($0, /[^ ]/) - 1
      if (indent >= 4) {
        if (indent == 4 && $0 ~ /:[[:space:]]*$/) {
          name = substr($0, indent + 1)
          sub(/:[[:space:]]*$/, "", name)
          print name
        }
        next
      }
      in_lanes = 0
    }
  ' "$CONFIG" 2>/dev/null
}

LANES=$(lane_names)
# awk, not `grep -c`: grep prints 0 and exits 1 on no match, so a `|| echo 0`
# fallback would emit a second 0 and make the arithmetic test below fail.
LANE_COUNT=$(printf '%s\n' "$LANES" | awk 'NF { n++ } END { print n + 0 }')

if [ "$LANE_COUNT" -gt 1 ]; then
  # Accumulate with the separator leading each block: command substitution strips
  # trailing newlines, so a trailing separator would glue the fences together.
  NEXT=""
  for lane in $LANES; do
    LANE_BODY=$("$OK" next --lane "$lane" 2>&1) || true
    if [ -z "$NEXT" ]; then
      NEXT=$(printf '**Lane: %s**\n\n%s' "$lane" "$LANE_BODY")
    else
      NEXT=$(printf '%s\n\n**Lane: %s**\n\n%s' "$NEXT" "$lane" "$LANE_BODY")
    fi
  done
  LANE_LIST=$(printf '%s' "$LANES" | tr '\n' ' ' | sed 's/ $//')
  NEXT=$(printf '%s\n\n**This repo has %s lanes (%s).** Every lane is shown because one lane is not the whole repo. Pick the lane your task belongs to — the default lane is not necessarily the active one.' "$NEXT" "$LANE_COUNT" "$LANE_LIST")
else
  NEXT=$("$OK" next 2>&1) || true
fi

WORKSPACE='Open the repository root (the folder that contains `.overseer/`) as the IDE workspace. If you open a parent folder, project rules and skills under `.cursor/` often do not load. The CLI still works. The open editor tab is not the source of truth — run `ok next`.'

STALE='If an editor tab of the handover looks old, close it and reopen it. The kit cannot reload the tab. Trust `ok next`, not the tab. A NEXT block pasted from an earlier chat is not evidence — re-read it from disk before acting on it.'

export LT_HOOK_NEXT="$NEXT"
export LT_HOOK_WORKSPACE="$WORKSPACE"
export LT_HOOK_STALE="$STALE"

if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' || true
import json
import os

body = "\n\n".join(
    part
    for part in (
        os.environ.get("LT_HOOK_NEXT", ""),
        os.environ.get("LT_HOOK_WORKSPACE", ""),
        os.environ.get("LT_HOOK_STALE", ""),
    )
    if part
)
print(json.dumps({"additional_context": body, "followup_message": body}))
PY
else
  printf '%s\n' '{"additional_context":"ok next (python3 unavailable)","followup_message":"ok next (python3 unavailable)"}'
fi

exit 0

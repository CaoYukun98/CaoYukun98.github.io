#!/usr/bin/env bash
# Print the pending inbox content. Exit 0 = pending, 1 = empty.
set -euo pipefail
cd "$(dirname "$0")/.."

inbox="automation/inbox.md"
[[ -f "$inbox" ]] || { echo "MISSING: $inbox" >&2; exit 2; }

pending="$(
  awk '
    /^## 待处理[[:space:]]*$/ { inside=1; next }
    /^## / { inside=0 }
    inside { print }
  ' "$inbox" | sed '/^[[:space:]]*$/d'
)"

if [[ -n "$pending" ]]; then
  echo "PENDING"
  echo "$pending"
  exit 0
fi

echo "EMPTY"
exit 1

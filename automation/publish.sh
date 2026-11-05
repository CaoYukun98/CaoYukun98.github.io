#!/usr/bin/env bash
# Validate, commit, and (if a token is available) push the homepage.
# Exit codes: 0 = pushed/no-op, 2 = committed locally but no token, 1 = failure.
set -euo pipefail
cd "$(dirname "$0")/.."

message="${1:-Update homepage}"
token_file="${GITHUB_TOKEN_FILE:-automation/.github-token}"

python3 automation/validate.py
git diff --check

git add -A
if git diff --cached --quiet; then
  echo "NO_CHANGES"
  exit 0
fi
git diff --cached --check

if ! git config user.email >/dev/null 2>&1; then
  git config user.email "167003062+CaoYukun98@users.noreply.github.com"
fi
if ! git config user.name >/dev/null 2>&1; then
  git config user.name "CaoYukun98"
fi

git commit -m "$message" >/dev/null
hash="$(git rev-parse --short HEAD)"
echo "COMMITTED $hash"

token="${GITHUB_TOKEN:-}"
if [[ -z "$token" && -f "$token_file" ]]; then
  token="$(tr -d '\r\n' < "$token_file")"
fi

if [[ -z "$token" ]]; then
  echo "NO_TOKEN: committed locally ($hash); set $token_file to publish."
  exit 2
fi

askpass="$(mktemp "${TMPDIR:-/tmp}/homepage-askpass.XXXXXX")"
cleanup() { rm -f "$askpass"; }
trap cleanup EXIT
cat > "$askpass" <<'EOF'
#!/bin/sh
case "$1" in
  *sername*) printf '%s\n' "x-access-token" ;;
  *assword*) printf '%s' "$HOMEPAGE_GITHUB_TOKEN" ;;
  *) exit 1 ;;
esac
EOF
chmod 700 "$askpass"
export HOMEPAGE_GITHUB_TOKEN="$token"

if GIT_ASKPASS="$askpass" GIT_TERMINAL_PROMPT=0 \
   git -c credential.helper= push origin HEAD:main; then
  echo "PUSHED $hash"
  exit 0
fi

echo "PUSH_FAILED: committed locally ($hash); check the token and network."
exit 1

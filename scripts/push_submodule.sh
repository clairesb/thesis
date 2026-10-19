#!/bin/bash

#Edited version of claude output
# Bumps submodlule pointer in main repo 
# Usage: ./push_submodule.sh <submodule_path> "<commit message>" [branch]
# Example: ./push_submodule.sh external/mss-alt "my cool message <3"
set -Eeuo pipefail

MODULE_PATH="${1:-}"
MSG="${2:-}"
BRANCH="${3:-}"

if [[ -z "$MODULE_PATH" || -z "$MSG" ]]; then
  echo "Usage: $0 <submodule_path> \"<commit message>\" [branch]" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
SUB="${MODULE_PATH%/}"

if [[ ! -e "$SUB/.git" ]]; then
  echo "Error: '$SUB' is not an initialized submodule." >&2
  exit 1
fi

# refuse to bump if the submodule's HEAD isn't on the remote
git -C "$SUB" fetch origin --quiet
if ! git -C "$SUB" branch -r --contains HEAD | grep -q "origin/$BRANCH"; then
  echo "Error: $SUB's current commit isn't on origin/$BRANCH. Push it first." >&2
  exit 1
fi

cd "$ROOT"
git add "$SUB"
if git diff --cached --quiet -- "$SUB"; then
  echo "Parent repo already points at the latest $SUB commit."
else
  git commit -m "Bump $(basename "$SUB"): $MSG" -- "$SUB"
  git push
fi

echo "Done."
#!/bin/bash

#Edited version of claude output
# Bumps submodlule pointer in main repo 
# Usage: ./push_submodule.sh <submodule_path> "<commit message>" [branch]
# Example: ./push_submodule.sh external/mss-alt "my cool message <3"
set -Eeuo pipefail

MODULE_PATH="${ARGS[0]:-}"
MSG="${ARGS[1]:-}"
BRANCH="${ARGS[2]:-main}"

ARGS=()

if [[ -z "$MODULE_PATH" || -z "$MSG" ]]; then
  echo "Usage: $0 <submodule_path> \"<commit message>\" [branch]" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
SUB="${SUB%/}"

if [[ ! -e "$SUB/.git" ]]; then
  echo "Error: '$SUB' is not an initialized submodule." >&2
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
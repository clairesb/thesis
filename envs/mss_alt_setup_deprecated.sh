# # DEPRECATED
# # !/bin/bash
# set -euo pipefail

# REPO_PATH="${1:?Usage: $0 /path/to/repo}"
# REPO_PATH="${REPO_PATH%/}"

# cd "$REPO_PATH"
# export PIXI_FROZEN=true
# pixi install -e dev

# export DATA_ROOT="$REPO_PATH/audio"
# export OUTPUT_DIR="$REPO_PATH/outputs"
# mkdir -p "$DATA_ROOT" "$OUTPUT_DIR"

# pixi run -e dev pre-commit install

# echo "Current directory: $(pwd)"
# ls -d "$DATA_ROOT" "$OUTPUT_DIR"

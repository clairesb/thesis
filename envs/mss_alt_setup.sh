#!/bin/bash

set -euo pipefail
REPO_PATH="${1}"

cd $REPO_PATH
export PIXI_FROZEN=true
pixi install
pixi shell
export DATA_ROOT="$REPO_PATH/audio"
export OUTPUT_DIR="$REPO_PATH/outputs"
mkdir -p "$DATA_ROOT" "$OUTPUT_DIR"

pixi run pre-commit install

echo "Current directory: "
pwd

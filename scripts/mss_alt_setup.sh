#!/bin/bash

REPO_PATH="${1}"

export PIXI_FROZEN=TRUE
pixi install
pixi shell
export DATA_ROOT="$REPO_PATH/audio"
export OUTPUT_DIR="$REPO_PATH/outputs"
mkdir -p "$DATA_ROOT" "$OUTPUT_DIR"
pre-commit install
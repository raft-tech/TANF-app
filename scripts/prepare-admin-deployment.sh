#!/usr/bin/env bash
set -euo pipefail

if [[ $# != 1 || ! -d "$1" ]]; then
  echo "Usage: $0 <existing-empty-output-directory>" >&2
  exit 1
fi

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUTPUT_DIR=$(cd "$1" && pwd)
if [[ -n "$(ls -A "$OUTPUT_DIR")" ]]; then
  echo "The deployment output directory must be empty." >&2
  exit 1
fi

# Keep local environment files and host-specific dependencies out of the upload.
mkdir "$OUTPUT_DIR/app"
cp "$REPO_ROOT/tdp-admin/cloudgov/package.json" "$OUTPUT_DIR/package.json"
tar -C "$REPO_ROOT/tdp-admin" --exclude='.env*' --exclude='*.test.*' \
  -cf - package.json yarn.lock .yarnrc.yml next.config.ts tsconfig.json src public |
  tar -C "$OUTPUT_DIR/app" -xf -

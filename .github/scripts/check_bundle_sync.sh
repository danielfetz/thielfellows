#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"
HEAD_REF="${2:-HEAD}"

changed_files="$(git diff --name-only "$BASE_REF"..."$HEAD_REF")"

if [[ -z "$changed_files" ]]; then
  echo "No changed files detected between $BASE_REF and $HEAD_REF"
  exit 0
fi

oak_changed=false
bundle_changed=false

while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  if [[ "$path" == *.oak ]]; then
    oak_changed=true
  fi
  if [[ "$path" == "static/js/bundle.js" ]]; then
    bundle_changed=true
  fi
done <<< "$changed_files"

if [[ "$oak_changed" != true ]]; then
  echo "No Oak source changes detected; skipping bundle sync check."
  exit 0
fi

if command -v oak >/dev/null 2>&1; then
  echo "Oak found. Rebuilding bundle to verify sync..."
  make build
  if ! git diff --quiet -- static/js/bundle.js; then
    echo "Bundle is out of sync with Oak sources. Run 'make build' and commit static/js/bundle.js."
    git --no-pager diff -- static/js/bundle.js
    exit 1
  fi
  echo "Bundle is in sync."
  exit 0
fi

echo "Oak binary not available in CI/runtime. Falling back to changed-file enforcement."
if [[ "$bundle_changed" != true ]]; then
  echo "Oak source files changed but static/js/bundle.js was not updated."
  echo "Please run 'make build' and commit static/js/bundle.js."
  exit 1
fi

echo "Oak sources changed and bundle.js was updated in this change set."

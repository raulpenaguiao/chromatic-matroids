#!/usr/bin/env bash
set -euo pipefail

tag="frontend"

git push origin --delete "$tag" 2>/dev/null || true
git tag -d "$tag" 2>/dev/null || true

git tag "$tag"
git push origin "$tag"
echo "Pushed tag $tag — frontend deploy CI triggered"

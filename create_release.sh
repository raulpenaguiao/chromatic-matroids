#!/usr/bin/env bash
set -euo pipefail

PYPROJECT="package/pyproject.toml"

current=$(python3 -c "
import tomllib
with open('$PYPROJECT', 'rb') as f:
    print(tomllib.load(f)['project']['version'])
")

echo "Current version: $current"
read -rp "New version: " new_version

if ! [[ "$new_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be X.Y.Z"
    exit 1
fi

tag="release-$new_version"

if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "Error: tag $tag already exists"
    exit 1
fi

sed -i "s/^version = \"$current\"/version = \"$new_version\"/" "$PYPROJECT"
echo "Updated $PYPROJECT: $current → $new_version"

git add "$PYPROJECT"
git commit -m "Bump version to $new_version"
git push origin main

git tag "$tag"
git push origin "$tag"
echo "Pushed tag $tag — release CI triggered"
echo "Watch progress at: https://github.com/raulpenaguiao/chromatic-matroids/actions"

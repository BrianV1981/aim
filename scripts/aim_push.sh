#!/bin/bash
# A.I.M. Auto-Versioning Push Script
# Orchestrated by Semantic Release pipeline in aim_cli.py

if [ -z "$1" ]; then
  echo "Usage: ./scripts/aim_push.sh \"commit message\""
  exit 1
fi

# Read current version from VERSION file (updated by aim_cli.py)
VERSION="v1.0.0"
if [ -f VERSION ]; then
  VERSION=$(cat VERSION)
fi

# Phase 26 Hardening: Only add tracked files, plus our semantic release files explicitly
git add VERSION CHANGELOG.md 2>/dev/null || true
git add -u

# Commit with the user's message and append the Version
# Also check if it closes an issue
if [[ "$1" == *"Closes #"* ]] || [[ "$1" == *"Resolves #"* ]]; then
  git commit -m "$1" -m "Version: $VERSION"
else
  git commit -m "$1" -m "Version: $VERSION"
fi

# Push to origin
CURRENT_BRANCH=$(git branch --show-current)
git push origin "$CURRENT_BRANCH"

echo "Successfully pushed A.I.M. version: $VERSION"

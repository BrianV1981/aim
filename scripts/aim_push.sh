#!/bin/bash
# A.I.M. Auto-Versioning Push Script
# Ensures that every push gets a unique date/time based version.

if [ -z "$1" ]; then
  echo "Usage: ./scripts/aim_push.sh \"commit message\""
  exit 1
fi

# Generate Version: v1.<YYYYMMDD>.<HHMM>
VERSION="v1.$(date +'%Y%m%d').$(date +'%H%M')"

# Write to VERSION file
echo "$VERSION" > VERSION

# Automatically stage changes, including the new VERSION file
git add .

# Commit with the user's message and append the Version
git commit -m "$1" -m "Version: $VERSION"

# Push to origin main
git push origin main

echo "Successfully pushed A.I.M. version: $VERSION"

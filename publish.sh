#!/usr/bin/env bash
set -euo pipefail
REPO="${GITHUB_REPOSITORY:-https://github.com/$USER/information-security-practice.git}"
if [ ! -d .git ]; then git init; git checkout -b main; fi
git add .
git commit -m "chore: publish" || true
git remote remove origin >/dev/null 2>&1 || true
git remote add origin "$REPO"
git push -u origin main

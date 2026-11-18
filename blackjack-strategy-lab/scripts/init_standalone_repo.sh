#!/usr/bin/env bash
# Turn this folder into its own standalone git repository and push it to a NEW GitHub repo.
#
# Prerequisites: git, and the GitHub CLI `gh` (authenticated) OR create the empty repo
# yourself in the GitHub web UI first.
#
# Usage:
#   cd blackjack-strategy-lab
#   bash scripts/init_standalone_repo.sh YOUR_GITHUB_USERNAME blackjack-strategy-lab
set -euo pipefail

USER="${1:?Pass your GitHub username as arg 1}"
REPO="${2:-blackjack-strategy-lab}"

# Fresh history for the standalone repo.
rm -rf .git
git init -b main
git add .
git commit -m "Initial commit: Blackjack Strategy Lab"

if command -v gh >/dev/null 2>&1; then
  gh repo create "${USER}/${REPO}" --private --source=. --remote=origin --push
  echo "Created and pushed to https://github.com/${USER}/${REPO}"
else
  echo "gh CLI not found. Create an empty repo at https://github.com/new named '${REPO}', then:"
  echo "  git remote add origin https://github.com/${USER}/${REPO}.git"
  echo "  git push -u origin main"
fi

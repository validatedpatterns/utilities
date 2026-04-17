#!/usr/bin/env bash

ORG="$1"
TARGET_FOLDER="common"

if [[ -z "$ORG" ]]; then
  echo "Usage: $0 <github-org>"
  exit 1
fi

# Get all non archived repo names in the org
repos=$(gh repo list "$ORG" \
  --limit 1000 \
  --json name,isArchived \
  -q '.[] | select(.isArchived == false) | .name')

printf "\nChecking repos in org: %s\n\n" "$ORG"

for repo in $repos; do
  full_repo="$ORG/$repo"

  # Check if pattern.sh exists in root
  if gh api "repos/$full_repo/contents/pattern.sh" &>/dev/null; then

    # Now check if target folder exists
    if gh api "repos/$full_repo/contents/$TARGET_FOLDER" &>/dev/null; then
        printf "\033[31m✘ %-40s is not patternized yet \033[0m\n" "$repo"
    else
      printf "\033[32m✔ %-40s has been patternized \033[0m\n" "$repo"
    fi

  fi
done

echo ""

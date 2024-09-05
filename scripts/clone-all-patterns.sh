#!/bin/bash
set -e -o pipefail

# Lists all repos tagged with "pattern" in the two organizations:
# - validatedpatterns
# - validatedpatterns-sandbox

ORGS=("validatedpatterns" "validatedpatterns-sandbox")
TOPIC=${TOPIC:-pattern}
BASE=${BASE:-/tmp/pattern}

mkdir -p "${BASE}" || /bin/true

for org in ${ORGS[@]}; do
    REPOS=$(gh repo list "${org}" --no-archived --topic "${TOPIC}" --visibility public --limit 100 |awk '{ print $1 }' | sort)
    ret=$?
    if [ ${ret} -ne 0 ]; then
        echo "Error retrieving pattern list for ${org}"
        exit ${ret}
    fi
    while IFS= read -r repo; do
        echo "Cloning: ${repo} into ${BASE}/${repo}"
        mkdir -p "${BASE}/${org}" || /bin/true
        pushd "${BASE}/${org}"
        git clone git@github.com:${repo}
        pushd "${BASE}/${repo}"
        git checkout -b "scripted-changes"
        popd
        popd
    done <<< "$REPOS"
done

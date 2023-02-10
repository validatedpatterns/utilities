#!/bin/bash
# This script is just a template to run things on all the branches of every
# repo being tested in CI

set -e -o pipefail

ORG="hybrid-cloud-patterns"
GH_USER="mbaldessari"
CI_REPO="utilities"
COMMON_REPO="common"
TMPD="/tmp/ci-branches"

function prereqs() {
	if ! command -v yq &> /dev/null; then
	  echo "yq command not found. Please install it first"
	  exit 1
	fi
	if ! command -v git &> /dev/null; then
	  echo "git command not found. Please install it first"
	  exit 1
	fi
}

function clone_ci_repo() {
	rm -rf "${TMPD}"
	mkdir -p "${TMPD}"
	pushd "${TMPD}"
	git clone "https://github.com/${ORG}/${CI_REPO}"
	git clone "https://github.com/${ORG}/${COMMON_REPO}"
	popd
}

function clone_repo() {
	REPO=$1
	pushd "${TMPD}"
	git clone "https://github.com/${ORG}/${REPO}"
	pushd "${REPO}"
	git remote add fork -f "git@github.com:${GH_USER}/${REPO}"
	popd
	popd
}

function repo_action() {
	REPO=$1
	BRANCH=$2
	echo "-> ${REPO} -> ${BRANCH}"
	pushd "${TMPD}/${REPO}"
	# Add your custom actions to be done here and then the commands to commit to git
	# These are just an example used in the past
	if [ "${BRANCH}" != "main" ]; then
		git checkout "origin/${BRANCH}" -b "${BRANCH}"
		git am /tmp/symlink.patch
		cp "${TMPD}/common/scripts/pattern-util.sh" ./common/scripts
		git add ./common/scripts/pattern-util.sh
		git commit -a -m "Add latest pattern-util.sh"
		git push fork "${BRANCH}" -f
		git log --oneline "origin/${BRANCH}..${BRANCH}"
		read -r -p "About to create PR for ${REPO}:${BRANCH}. Is that okay (y/n)? : " ANSWER
		case "${ANSWER}" in
			y*|Y*)
				gh pr create -R "${ORG}"/"${REPO}" --base "${BRANCH}" --fill
				;;
			*)
				echo "Skipping"
				;;
		esac

	fi
	popd
}

clone_ci_repo

pushd "${TMPD}/${CI_REPO}/ci-triggers"
for r in *.yaml; do
	REPO="${r%.yaml}"
	clone_repo "${REPO}"
	for branch in $(yq eval '.triggers.branches[].name' "${r}"); do 
		repo_action "${REPO}" "${branch}"
	done
	echo ""
done
popd

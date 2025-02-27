#!/bin/bash
set -e -o pipefail

# Fixed organization for the common repository
COMMONORG="validatedpatterns"
# Default fork organization (can be overridden with -o)
FORKORG="validatedpatterns"
COMMONBRANCH="v1"
BRANCH="common-automatic-update" # name of the branch used locally and on the remote fork
TMPD=$(mktemp -d /tmp/commonrebase.XXXXX)
LOG="${TMPD}/log"

# Flag to automatically clean up the temporary directory (default: no)
AUTOCLEAN="n"

trap cleanup SIGINT

function cleanup {
  echo "Cleaning up"
  if [[ "${TMPD}" =~ /tmp.* ]]; then
    rm -rf "${TMPD}"
  fi
}

function usage {
  echo "Run: ${0} [-h|--help] [-p|--prcreate] [-c|--clean-tmp] [-o|--org <forkorg>] -u|--usergithub <githubusername> -r|--repos <repo1,repo2,...>"
  echo ""
  echo "Updates the common/ subtree in all the repos specified, working in a temporary directory."
  echo "The common repository is always pulled from the ${COMMONORG} organization, while"
  echo "forking and PR operations are performed against the specified fork organization (default: ${FORKORG})."
  echo ""
  echo "Usage:"
  echo "    -h|--help                   - Optional. Prints this help page"
  echo "    -p|--prcreate               - Optional. Without this, no actual PR is created; only preparation steps are run"
  echo "    -b|--branch                 - Optional. Which common branch to use when updating (defaults to ${COMMONBRANCH})"
  echo "    -o|--org                    - Optional. GitHub fork organization to use (defaults to ${FORKORG})"
  echo "    -u|--usergithub <user>      - Mandatory. The PR will be pushed into the ${BRANCH} branch of <user>'s fork"
  echo "                                  (the forked repo in the user's space must already exist)"
  echo "    -r|--repos <repo1,repo2,..> - Mandatory. List of repos to update the common/ subtree in, separated by commas"
  echo "    -s|--skip-common-check      - Optional. Won't error out if the project's common and upstream common differ"
  echo "    -c|--clean-tmp              - Optional. Automatically remove the temporary directory when done"
}

PRCREATE="n"
SKIPCOMMONCHECK="n"
GHREPOS=()
USERGITHUB=""

if ! command -v gh &> /dev/null; then
  echo "gh command not found. Please install it first."
  exit 1
fi

# Parse options. Note that options with required arguments are followed by a colon.
if ! getopt -o hpsu:r:b:o:c -l help,prcreate,skip-common-check,usergithub:,repos:,branch:,org:,clean-tmp -- "$@"; then
    usage
    exit 1
fi

# Normalize argument order
eval set -- "$(getopt -o hpsu:r:b:o:c -l help,prcreate,skip-common-check,usergithub:,repos:,branch:,org:,clean-tmp -- "$@")"

while [ $# -gt 0 ]; do
    case "$1" in
      -h|--help)
          usage
          exit 0
          ;;
      -p|--prcreate)
          PRCREATE="y"
          shift
          ;;
      -s|--skip-common-check)
          SKIPCOMMONCHECK="y"
          shift
          ;;
      -b|--branch)
          COMMONBRANCH="$2"
          shift 2
          ;;
      -o|--org)
          FORKORG="$2"
          shift 2
          ;;
      -u|--usergithub)
          USERGITHUB="$2"
          shift 2
          ;;
      -r|--repos)
          IFS=',' read -r -a GHREPOS <<< "$2"
          shift 2
          ;;
      -c|--clean-tmp)
          AUTOCLEAN="y"
          shift
          ;;
      --)
          shift
          break
          ;;
      *)
          break
          ;;
    esac
done

if [ -z "${USERGITHUB}" ]; then
  echo "You must specify a GitHub username."
  usage
  exit 1
fi

if [ ${#GHREPOS[@]} -eq 0 ]; then
  echo "You must specify at least one repository (multiple repos should be separated by commas)."
  usage
  exit 1
fi

# The common repository is fixed to the COMMONORG organization.
COMMON="https://github.com/${COMMONORG}/common.git"
# The fork base URL is determined by the FORKORG variable.
GITBASE="git@github.com:${FORKORG}"

pushd "$TMPD"
echo "Working in ${TMPD} on the following repos: ${GHREPOS[*]}" | tee "$LOG"
git clone "${COMMON}" >> "$LOG"
pushd common
git checkout "${COMMONBRANCH}" >> "$LOG"
popd

for i in "${GHREPOS[@]}"; do
  echo "Cloning $i"
  git clone "${GITBASE}/${i}.git" >> "$LOG"
  pushd "$i"
  git remote add common-upstream -f ../common | tee -a "$LOG"
  git remote add fork -f "git@github.com:${USERGITHUB}/${i}.git" | tee -a "$LOG"
  git checkout -b "${BRANCH}" | tee -a "$LOG"
  git merge --no-edit -s subtree -Xtheirs -Xsubtree=common "common-upstream/${COMMONBRANCH}" | tee -a "$LOG"

  # Check for merge conflicts
  if grep -IR -e '^<<<' -e '^>>>' . 2>/dev/null; then
    echo "Repo $i has conflicts after merge"
    exit 1
  fi

  # Verify that upstream common/ and the subtree common/ are identical
  set +e
  diff -urN --exclude='.git' --no-dereference ../common ./common 2>&1 | tee "$LOG"
  ret=$?
  set -e
  if [ $ret -ne 0 ]; then
    if [ "$SKIPCOMMONCHECK" == 'n' ]; then
      echo "The diff command returned $ret. ABORTING here."
      exit 1
    else
      echo "The diff command returned $ret. Not aborting here due to --skip-common-check being passed. Proceed with caution!"
    fi
  fi

  git push fork "${BRANCH}" -f | tee -a "$LOG"
  gh repo set-default "${FORKORG}/${i}"

  # Automatically create a PR if requested.
  if [ "$PRCREATE" == 'y' ]; then
    set +e
    gout=$(gh pr create --title "Automatic common/ update from branch ${COMMONBRANCH}" \
       --assignee "@me" \
       --body "This is part of an automatic process run by ${USERGITHUB} on $(date)" \
       --repo "${FORKORG}/${i}" --base "${COMMONBRANCH}" --head "${USERGITHUB}:${BRANCH}" 2>&1)
    ret=$?
    set -e
    if [ $ret -ne 0 ]; then
      if grep "No commits between ${FORKORG}:${COMMONBRANCH} and" <<< "$gout"; then
        echo "PR not created as there were no commits to push for"
        continue
      fi
      echo "Error while creating PR: ${gout}"
    else
      echo ""
      echo "PR created:"
      echo "${gout}"
      echo ""
    fi
  fi
  popd
done
popd

if [ "${AUTOCLEAN}" == "y" ]; then
  rm -rf "${TMPD}"
  echo ""
  echo "Finished and temporary directory ${TMPD} has been removed."
else
  echo ""
  echo "Finished. You may remove ${TMPD} manually."
fi

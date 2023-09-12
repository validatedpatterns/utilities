#!/bin/bash
set -e -o pipefail

ORG="validatedpatterns"
GITBASE="git@github.com:${ORG}"
COMMON="https://github.com/${ORG}/common.git"
BRANCH="common-automatic-update" # name of the branch being used locally and on the remote fork
MAINBRANCH="main"
TMPD=$(mktemp -d /tmp/commonrebase.XXXXX)
LOG="${TMPD}/log"

trap cleanup SIGINT

function cleanup {
  echo "Cleaning up"
  if [[ "${TMPD}" =~ /tmp.* ]]; then
    rm -rf "${TMPD}"
  fi
}

function usage {
  echo "Run: ${0} [-h|--help] [-p|--prcreate] -u|--usergithub <githubusername> -r|--repos <repositories to work on separated by commas>"
  echo ""
  echo "Updates common/ in all the repos specified,  does the work in a temporary directory"
  echo "This script requires the gh CLI utility installed and configued and"
  echo "also that the repo is forked from ${ORG} to the user space on GitHub"
  echo ""
  echo "Usage:"
  echo "    -h|--help                   - Optional. Prints this help page"
  echo "    -p|--prcreate               - Optional. Without this no actual PR is created, just the preparation steps are run"
  echo "    -u|--usergithub <user>      - Mandatory. The PR will be pushed into the ${BRANCH} of a fork belonging to <user>"
  echo "                                  The forked repo in the users space, must exist"
  echo "    -r|--repos <repo1,repo2,..> - Mandatory. List of repos to update the common/ subtree in. Separated by comma"
  echo "    -s|--skip-common-check      - Optional. Won't error out if project's common and upstream common differ"
}

PRCREATE=n
SKIPCOMMONCHECK=n
GHREPOS=()

if ! command -v gh &> /dev/null; then
  echo "gh command not found. Please install it first"
  exit 1
fi
# Parse options. Note that options may be followed by one colon to indicate
# they have a required argument
if ! getopt -o hpsu:r: -l help,prcreate,skip-common-check,usergithub:repos:; then
    # Error, getopt will put out a message for us
    usage
    exit 1
fi

while [ $# -gt 0 ]; do
    # Consume next (1st) argument
    case $1 in
    -h|--help)
      usage
      exit 0
      ;;
    -p|--prcreate)
      PRCREATE="y"
      ;;
    -s|--skip-common-check)
      SKIPCOMMONCHECK="y"
      ;;
    -u|--usergithub)
      USERGITHUB="$2"
      shift
      ;;
    -r|--repos)
      IFS=',' read -r -a GHREPOS <<< "$2"
      shift
      ;;
    (*)
      break
      ;;
    esac
    # Fetch next argument as 1st
    shift
done
shift $((OPTIND -1))

if [ -z "${USERGITHUB}" ]; then
  echo "You must specify a github username"
  usage
  exit 1
fi

if [ ${#GHREPOS[@]} -eq 0 ]; then
  echo "You must specify the repos to work on. Multiple repos should be separated by commas"
  usage
  exit 1
fi

pushd "$TMPD"
echo "Working in ${TMPD} on the following repos: ${GHREPOS[*]}" | tee "$LOG"
git clone "${COMMON}" >> "$LOG"
for i in "${GHREPOS[@]}"; do
  echo "Cloning $i"
  git clone "${GITBASE}/${i}.git" >> "$LOG"
  pushd "$i"
  git remote add common-upstream -f ../common | tee -a "$LOG"
  git remote add fork -f "git@github.com:${USERGITHUB}/${i}.git" | tee -a "$LOG"
  git checkout -b "${BRANCH}" | tee -a "$LOG"
  git merge --no-edit -s subtree -Xtheirs -Xsubtree=common "common-upstream/${MAINBRANCH}" | tee -a "$LOG"

  # Check that no commit left conflicts
  if grep -IR -e '^<<<' -e '^>>>' . 2>/dev/null; then
    echo "Repo $i has conflicts after merge"
    exit 1
  fi

  # Check that upstream common/ and the subtree common/ are identical (add --no-dereference due to our commmon -> symlink)
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
  gh repo set-default "${ORG}/${i}"

  # Automatically create a PR. This needs more testing and explaining before we enable it
  # The --head USERGITHUB:BRANCH is needed due to https://github.com/cli/cli/issues/2691
  if [ "$PRCREATE" == 'y' ]; then
    set +e
    gout=$(gh pr create --title "Automatic common/ update" \
       --assignee "@me" \
       --body "This is part of an automatic process run by ${USERGITHUB} on $(date)" \
       --repo "${ORG}/${i}" --base "${MAINBRANCH}" --head "${USERGITHUB}:${BRANCH}" 2>&1)
    ret=$?
    set -e
    if [ $ret -ne 0 ]; then
      if grep "No commits between ${ORG}:${MAINBRANCH} and" <<< "$gout"; then
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

echo ""
echo "Finished. You may remove ${TMPD} manually."

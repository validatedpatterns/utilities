#!/bin/bash
set -e -o pipefail

TEMP_FOLDER=${TEMP_FOLDER:-/tmp/gitea-sync-tmp}

function usage {
  echo "Run: ${0} -b|--branch <branch to sync from upstream to gitea>"
  echo ""
  echo "Makes sure that the in-cluster gitea repo is updated from upstream"
  echo "Assumes that a pattern is already deployed with in-cluster gitea and that"
  echo "oc can talk to the cluster. Needs: yq, jq, tea and oc"
  echo "Note: It uses /tmp/gitea-sync-tmp as a temporary folder"
  echo ""
  echo "Usage:"
  echo "    -h|--help            - Optional. Prints this help page"
  echo "    -b|--branch <branch> - Mandatory branch to sync from upstream to the in-cluster gitea"
}

function is_available {
  command -v "$1" >/dev/null 2>&1 || { echo >&2 "$1 is required but it's not installed. Aborting."; exit 1; }
}
readonly commands=(yq jq tea oc)
for cmd in "${commands[@]}"; do is_available "$cmd"; done

set +e
OUT=$(oc cluster-info 2>&1)
RET=$?
set -e
if [ $RET -ne 0 ]; then
    echo "Could not connect to the cluster:"
    echo "${OUT}"
    exit 1
fi
if ! getopt -o hb: -l help,branch:; then
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
    -b|--branch)
      BRANCH="$2"
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

if [ -z "${BRANCH}" ]; then
    echo "No branch specified"
    usage
    exit 1
fi

GITEA_USER=$(oc extract -n vp-gitea secret/gitea-admin-secret --to=- --keys=username 2>/dev/null)
GITEA_PASS=$(oc extract -n vp-gitea secret/gitea-admin-secret --to=- --keys=password 2>/dev/null)
echo "Got gitea credentials"

UPSTREAM_REPO=$(oc get patterns -n openshift-operators  -o yaml | yq '.items[0].spec.gitSpec.originRepo')
REPO_NAME=$(basename "${UPSTREAM_REPO}")
GITEA_REPO=$(oc get patterns -n openshift-operators  -o yaml | yq '.items[0].spec.gitSpec.targetRepo')
GITEA_ROUTE=$(oc get routes -n vp-gitea gitea-route -o yaml | yq '.spec.host')

if [ -z "${REPO_NAME}" ]; then
    echo "Error REPO_NAME was empty. Original upstream repo: ${UPSTREAM_REPO}"
    exit 1
fi

echo "Git repository name: ${REPO_NAME}"
echo "Gitea route: ${GITEA_ROUTE}"
echo "Gitea repo: ${GITEA_REPO}"
echo "Upstream repo: ${UPSTREAM_REPO}"

URL="https://${GITEA_ROUTE}"
AUTH_URL="https://${GITEA_USER}:${GITEA_PASS}@${GITEA_ROUTE}"
TOKEN_LIST=$(curl -k --silent --show-error --url "${AUTH_URL}/api/v1/users/${GITEA_USER}/tokens" | jq -r '.[] | select(.name == "vp-token-admin")')
if [ -z "${TOKEN_LIST}" ]; then
    echo "Creating new token"
    set +e
    TOKEN=$(curl -k --silent --show-error --fail-with-body -u "${GITEA_USER}:${GITEA_PASS}" -X POST -H "Content-Type: application/json" \
         -d '{"name": "vp-token-admin", "scopes": ["write:user", "write:issue", "write:repository"]}' "${URL}/api/v1/users/${GITEA_USER}/tokens" | jq -r .sha1)
    RET=$?
    set -e
    if [ ${RET} -ne 0 ]; then
        echo "Could not create token: ${TOKEN}"
        exit 1
    fi
    tea login add --url "${URL}" --user "${GITEA_USER}" --password "${GITEA_PASS}" --insecure --token "${TOKEN}"
else
    echo "Token already exists, skipping creation, assuming we're already logged in"
    echo "If tea commands are failing, please delete the 'vp-admin-token' from the web interface in gitea"
fi

mkdir -p "${TEMP_FOLDER}"
pushd "${TEMP_FOLDER}"
if [ ! -d "${REPO_NAME}" ]; then
    echo "Local git repo does not exist let's clone ${UPSTREAM_REPO} and branch ${BRANCH}"
    git clone --branch "${BRANCH}" --single-branch "${UPSTREAM_REPO}"
    pushd "${REPO_NAME}"
else
    echo "Local git repo exists, pulling branch ${BRANCH}"
    pushd "${REPO_NAME}"
    git pull origin "${BRANCH}"
fi
echo "Pushing ${BRANCH} to ${URL}"
git -c http.sslVerify=false push "${AUTH_URL}/${GITEA_USER}/${REPO_NAME}.git" "${BRANCH}:${BRANCH}"
popd
popd

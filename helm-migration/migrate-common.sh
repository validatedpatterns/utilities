#!/bin/bash
set -e -o pipefail

CHARTS="clustergroup acm hashicorp-vault golang-external-secrets"
COMMON="https://github.com/hybrid-cloud-patterns/common/"
GITBASE_URL=""

function usage {
  echo "Run: ${0} [-h|--help] -d|--destinationdir <folder in which to create all the chart repositories>"
  echo "          [-g|--gitbaseurl] <gitbase url to use to push repos out>"
  echo "          [-t|--templatedir <folder where optional github workflow templates are stored>]"
  echo ""
  echo "Reads common/ and splits of all the helm charts as separate git repos"
  echo "inside the specified desination dir"
  echo ""
  echo "Usage:"
  echo "    -h|--help                   - Optional. Prints this help page"
  echo "    -d|--destinationdir <dir>   - Mandatory. In which folder to create the helm chart git repos. Must not exist"
  echo "    -g|--gitbaseurl <name>      - Optional. When set it pushes out each chart to that org. E.g. 'git@github.com:mbaldessari/' will push to each repo like 'mbaldessari/acm-chart' etc"
  echo "    -t|--templatedir <dir>      - Optional. When specified it copies all the workflows contained in .github/workflow/"
}

if ! getopt -o hd:t:g: -l help,destinationdir:,templatedir:,gitbaseurl:; then
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
    -d|--destinationdir)
      DEST_DIR="$2"
      shift
      ;;
    -t|--templatedir)
      TEMPLATE_DIR="$2"
      shift
      ;;
    -g|--gitbaseurl)
      GITBASE_URL="$2"
      shift
      ;;
    *)
      break
      ;;
    esac
    # Fetch next argument as 1st
    shift
done

if [ -z "${DEST_DIR}" ]; then
    echo "You must specify the a destination dir"
    usage
    exit 1
fi

if [ -d "${DEST_DIR}" ]; then
    echo "${DEST_DIR} cannot exist, bailing out"
    exit 1
fi

mkdir -p "${DEST_DIR}"
pushd "${DEST_DIR}"
git clone "${COMMON}"
pushd "./common"
for i in ${CHARTS}; do
    echo "${i}"
    git subtree split -P "${i}" -b "${i}-splitoff"
    mkdir ../"${i}-chart"
    pushd ../"${i}-chart"
    git init
    git pull "${DEST_DIR}/common" "${i}-splitoff"
    if [ -n "${TEMPLATE_DIR}" ]; then
        echo "Copying templates..."
        mkdir -p .github/workflows
        cp -avf "${TEMPLATE_DIR}/.github/workflows/"* .github/workflows
        git add .github/workflows
        git commit -a -m "Added .github/workflows for helm chart"
    fi
    popd
done
popd # common
# Remove common
rm -rf ./common

# Push out the repos to the respective repositories
if [ -z "${GITBASE_URL}" ]; then
    echo "No gitbaseurl set. Exiting here"
    exit 0
fi

for i in $(ls -d *); do
    pushd "${i}"
    git remote add origin "${GITBASE_URL}/${i}.git"
    git branch -M main
    git push -f -u origin main
    CHARTVERSION=$(yq -r '.version' Chart.yaml)
    git tag "v${CHARTVERSION}"
    git push origin "v${CHARTVERSION}"
    popd
done
popd # dest_dir

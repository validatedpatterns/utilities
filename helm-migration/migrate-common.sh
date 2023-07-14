#!/bin/bash
set -ex -o pipefail

CHARTS="clustergroup acm hashicorp-vault golang-external-secrets"
COMMON="https://github.com/hybrid-cloud-patterns/common/"

function usage {
  echo "Run: ${0} [-h|--help] -d|--destinationdir <folder in which to create all the chart repositories>"
  echo "          [-t|--templatedir <folder where optional github workflow templates are stored>]"
  echo ""
  echo "Reads common/ and splits of all the helm charts as separate git repos"
  echo "inside the specified desination dir"
  echo ""
  echo "Usage:"
  echo "    -h|--help                   - Optional. Prints this help page"
  echo "    -d|--destinationdir <dir>   - Mandatory. In which folder to create the helm chart git repos. Must not exist"
  echo "    -t|--templatedir <dir>      - Optional. When specified it copies all the workflows contained in ./workflow-templates/helm/"
}

if ! getopt -o hd:t: -l help,destinationdir:,templatedir:; then
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
        cp -avf "${TEMPLATE_DIR}/workflow-templates/helm/*" .github/workflows
        git add .github/workflows
        git commit -a -m "Added .github/workflows for helm chart"
    fi
    popd
done
popd # common
popd # dest_dir

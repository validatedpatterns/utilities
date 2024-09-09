#!/bin/bash
set -e -o pipefail

QUAY="docker://quay.io/hybridcloudpatterns"
CHARTS=("clustergroup" "acm" "letsencrypt" "pattern-install" "hashicorp-vault" "golang-external-secrets")

function usage {
    echo "Run: ${0} [-h|--help]"
    echo ""
    echo "This prints out the latest versions of each VP chart as stored in ${QUAY}"
}

function is_available {
  command -v $1 >/dev/null 2>&1 || { echo >&2 "$1 is required but it's not installed. Aborting."; exit 1; }
}
readonly commands=(jq skopeo)
for cmd in "${commands[@]}"; do is_available "$cmd"; done

if ! getopt -o h -l help &>/dev/null; then
    usage
    exit 1
fi

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        (*)
            break
            ;;
    esac
    shift
done

shift $((OPTIND -1))

for CHART in "${CHARTS[@]}"; do
    OUT=$(skopeo list-tags "${QUAY}/${CHART}" | jq -r ".Tags[]" | sort --version-sort | tail -n1)
    RET=$?
    if [ $RET -ne 0 ]; then
        echo "Parsing tags failed for ${CHART}: ${OUT}"
        exit 1
    fi
    echo "${CHART}: ${OUT}"
done

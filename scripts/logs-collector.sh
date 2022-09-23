#!/bin/bash
# Collects logs in /tmp/acm/<clustername> of all pods+containers running in the open-cluster-managament
# namespace

set -eu

NS=""

function usage {
  echo "Run: ${0} [-h|--help] -n|--namespace <namespace to fetch logs from>"
  echo ""
  echo "Fetches all logs from all pods/containers in a specific namespace"
  echo "and copies them to /tmp/logs/<clustername>"
  echo ""
  echo "Usage:"
  echo "    -h|--help                   - Optional. Prints this help page"
  echo "    -n|--namespace <namespace>  - Mandatory. Namespace to fetch logs from"
}

# Parse options. Note that options may be followed by one colon to indicate
# they have a required argument
if ! getopt -o hn: -l help,namespace: >/dev/null 2>&1; then
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
    -n|--namespace)
      NS="$2"
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

if [ -z "${NS}" ]; then
  echo "You must specify a namespace"
  usage
  exit 1
fi

NAME=$(oc get ingresses.config/cluster -o jsonpath={.spec.domain} | cut -f2- -d\.)

if [ -z "${NAME}" ]; then
	echo "Cluster name empty stopping"
	exit 1
fi

DIR="/tmp/logs/${NAME}"
echo "Storing logs in: ${DIR}"
mkdir -p "${DIR}" 

for pod in $(oc get -n ${NS} pods --no-headers -o custom-columns=.:.metadata.name); do
	for container in $(oc get pods -n ${NS} "${pod}" -o jsonpath='{.spec.containers[*].name}'); do
		echo "${pod} -> ${container} -> ${DIR}/${pod}-${container}.log"
		oc logs -n ${NS} ${pod} -c ${container} > "${DIR}/${pod}-${container}.log"
	done
done

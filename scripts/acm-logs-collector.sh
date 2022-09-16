#!/bin/bash
# Collects logs in /tmp/acm/<clustername> of all pods+containers running in the open-cluster-managament
# namespace

set -eu

NS="${NS:-open-cluster-management}"
NAME=$(oc get ingresses.config/cluster -o jsonpath={.spec.domain} | cut -f2- -d\.)

if [ -z "${NAME}" ]; then
	echo "Cluster name empty stopping"
	exit 1
fi

DIR="/tmp/acm/${NAME}"
echo "Storing logs in: ${DIR}"
mkdir -p "${DIR}" 

for pod in $(oc get -n ${NS} pods --no-headers -o custom-columns=.:.metadata.name); do
	for container in $(oc get pods -n ${NS} "${pod}" -o jsonpath='{.spec.containers[*].name}'); do
		echo "${pod} -> ${container}"
		oc logs -n ${NS} ${pod} -c ${container} > "${DIR}/${pod}-${container}.log"
	done
done

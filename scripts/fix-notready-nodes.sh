#!/bin/sh


# Function log
# Arguments:
#   $1 are for the options for echo
#   $2 is for the message
#   \033[0K\r - Trailing escape sequence to leave output on the same line
function log {
    if [ -z "$2" ]; then
        echo -e "\033[0K\r\033[1;36m$1\033[0m"
    else
        echo -e $1 "\033[0K\r\033[1;36m$2\033[0m"
    fi
}

if [[ -z "${KUBECONFIG}" ]]; then
    log "Please set KUBECONFIG to connecto to OpenShift"
    exit
else
    log "Using [$KUBECONFIG] to connect to OpenShift"
fi


log "Getting the status of the nodes"
oc get nodes

log "Approving the CSRs that are Pending"
for i in `oc get csr | grep Pending | awk '{print $1}'`
do
    log "Certificate [$i] needs approval"
    oc adm certificate approve $i
done

log "Checking for additional Pending CSRs"
PENDING=`oc get csr | grep Pending | awk '{print $1}'`
if [ "$PENDING." != "." ]; then
    for i in `oc get csr | grep Pending | awk '{print $1}'`
    do
	log "Certificate [$i] needs approval"
	oc adm certificate approve $i
    done
fi

NUMNODES=$(oc get nodes | grep -v NAME | wc -l)
let READYNODES=0
log -n "Waiting for all nodes to be ready "
while ( true )
do
    READYNODES=$(oc get nodes | grep -v NAME | grep -vi NOTREADY | wc -l)
    log -n "Waiting for all nodes to be ready [$READYNODES/$NUMNODES]..."
    if [ $NUMNODES -eq $READYNODES ]; then
	    break;
    fi
    sleep 3
    log -n "Waiting for all nodes to be ready "
done
echo "done."
log "Getting the status of the nodes"
oc get nodes

while ( true )
do
  log -n "Waiting for routes ... "
  oc get routes -n openshift-console > /dev/null 2>&1
  if [ $? == 0 ]; then
    echo "done"
    echo "You should be able to get to the OpenShift console using the following routes"
    oc get routes -n openshift-console 
    break
  fi
  sleep 1
  log -n "Waiting for routes     "
  sleep 1
done

#!/bin/sh
#
#

function log {
    if [ -z "$2" ]; then
        echo -e "\033[0K\r\033[1;36m$1\033[0m"
    else
        echo -e $1 "\033[0K\r\033[1;36m$2\033[0m"
    fi
}

log -n "Retirevng namespaces for OpenShift GitOps DEX pods ... "
DEXNAMESPACES=$(oc get pods -A | grep -i 'dex-server' | awk '{print $1}')
log "Retirevng namespaces for OpenShift GitOps DEX pods ... ok"

for namespace in $DEXNAMESPACES; do
  DEXPOD=$(oc get pods -n $namespace | grep 'dex-server' | awk '{ print $1 }')
  log -n "Deleting pod [ $DEXPOD ] in namespace [ $namespace ] ... "
  RC=$(oc delete -n $namespace pod/$DEXPOD;echo $? > /tmp/rc)
  if [ $(cat /tmp/rc) -eq 0 ]; then
    log "Deleting pod [ $DEXPOD ] in namespace [ $namespace ] ... ok"
  else
    log "Deleting pod [ $DEXPOD ] in namespace [ $namespace ] ... failed"
  fi
done

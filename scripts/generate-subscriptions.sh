#!/bin/sh

#
# Generates a Validated Pattern subscription entry for an operator
# to be added to values-[hub | datacenter | factory].yaml file.
#
# The entries will have to be copied and pasted to the approriate 
# values file.
#
function generateSubscriptionEntry {
  for i in $subscriptions
  do
  PACKNAME=$(oc get packagemanifests | grep -i $i | awk '{ print $1}')
if [ ".$PACKNAME" == "." ]; then
echo "Package: $i unknown"
continue
 fi
  for j in $PACKNAME
  do 
    echo "Package Info for [$j]"
    OUT=$(oc get packagemanifest/$j -o json | jq '.metadata.name, .metadata.namespace, .metadata.labels.catalog, .status.defaultChannel, .status.channels[].currentCSV')
    let COUNT=1
    for k in $OUT
    do
      case $COUNT in 
      1) echo "    $k:" | tr -d '"'
         echo "      name: $k" | tr -d '"'
         ;;
      2) echo "      namespace: $k" | tr -d '"'
         ;;
      3) echo "      source: $k" | tr -d '"'
         ;;
      4) echo "      channel: $k" | tr -d '"'
         ;;
      5) echo "      csv: $k" | tr -d '"'
         ;;
      esac
      let COUNT++
    done
  done
  done
}

subscriptions="$@"

echo "Note: namespace might not be correct for some  operator entries."
echo "Make make sure that you update the namespace value to the desired targert value."
echo "The script will use your current namespace [`oc project -q`] unless specified by the package manifest"
generateSubscriptionEntry $subscriptions


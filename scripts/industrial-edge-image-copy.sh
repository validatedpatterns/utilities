#!/bin/sh

LOGFILE=/tmp/skopeo-copy.log
ASK=true

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

function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

#
# User login to registry
#
function registryLogin {
  let attempts=0
  while ( true )
  do
    log "Need to log in onto the target registry [ $global_imageregistry_hostname ]"
    skopeo login  $global_imageregistry_hostname
    if [ $? == 0 ]; then
      break
    else
      continue
      attempts++
      if [ $attempts -gt 3 ]; then
        log "Too many attempts ... try again"
	exit
      fi
    fi
  done
}

while getopts "d:l:" opt
do
    case $opt in
        (d) location=$OPTARG
	    ASK=false
            ;;
        (l) LOGFILE=$OPTARG
            ;;
        (*) printf "Illegal option '-%s'\n" "$opt" && exit 1
            ;;
    esac
done

while ( $ASK ) 
do
  log -n "Please enter location of values-global.yaml: "
  read location
  echo $location
  if [ "$location." == "." ]; then
    continue
  else
    if [ -d $location ]; then
      break;
    else
      log -n "Please enter location of values-global.yaml: LOCATION MUST BE A DIRECTORY. Press Enter to continue"
      read dummy
      continue
    fi
  fi
done
log -n "Reading imageregistry values from $location/values-global.yaml ... "
eval $(parse_yaml $location/values-global.yaml)
log "Reading imageregistry values from $location/values-global.yaml ... done"

# User needs to login to the registry
registryLogin

rm -f $LOGFILE
touch $LOGFILE

for image in iot-consumer iot-anomaly-detection iot-frontend iot-software-sensor
do
   log -n "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest ===>  " 
   echo "START: Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> $LOGFILE
   skopeo copy docker://quay.io/hybridcloudpatterns/$image:latest docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest >> $LOGFILE
   if [ $? == 0 ]; then
     log "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest ===> done" 
     echo "DONE: docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> $LOGFILE
   else
     log "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest: ERROR" 
     log "Please see $LOGFILE for ERROR"
     echo "ERROR: docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> $LOGFILE
   fi
done


#!/bin/sh

#
# This script uses skopeo to copy the industrial edge boostrap images for
# iot-consumer iot-anomaly-detection iot-frontend iot-software-sensor
# to the image registry that is defined in the values-global.yaml file.
#

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

#
# Parses a simple yaml file and returns
#
# It understands files such as:
#
#  ## global definitions
#  global:
#    debug: yes
#    verbose: no
#    debugging:
#      detailed: no
#      header: "debugging started"
#
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
# SCRIPT STARTS HERE
#

#
# We first ask for the location, or directory, where the values-global.yaml is located.
#
while ( true ) 
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

#
# Now we parse the values-global.yaml file
#
log -n "Reading values from $location/values-global.yaml ... "
eval $(parse_yaml values-global.yaml)
log "Reading values from $location/values-global.yaml ... done"

#
# Create the image-copy.log file
#
touch "image-copy.log"

#
# Loop through the image repos and copy to the destination defined in values-global.yaml
#
for image in iot-consumer iot-anomaly-detection iot-frontend iot-software-sensor
do
   log -n "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest ===>  " 
   echo "Copying: docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> skopeo-copy.log
   
   skopeo copy docker://quay.io/hybridcloudpatterns/$image:latest docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest >> skopeo-copy.log 2>&1
   
   if [ $? == 0 ]; then
     log "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest ===> done" 
     echo "DONE: docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> skopeo-copy.log
   else
     log "Copying docker://quay.io/hybridcloudpatterns/$image:latest to docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest: ERROR" 
     log "Please see skopeo-copy.log for ERROR"
     echo "ERROR: docker://$global_imageregistry_hostname/$global_imageregistry_account/$image:latest" >> skopeo-copy.log
   fi
done


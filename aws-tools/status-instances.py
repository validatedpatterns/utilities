#!/usr/bin/python

import boto3
import sys
import getopt

filter=""
regions=['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
allInstances={}

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hf:"

# Long options
long_options = ["help", "filter"]

def usage():
  msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -f or --filter \n" \
        "    Filter for cluster search. Will be added to the *master* and *worker* filter \n" \
        "    Example: -f *claudiol-dc1* \n" \
        " -h or --help \n" \
        "    Usage message"
  print(msg)
  exit()

def main():
    fFoundInstances = False
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        if len(arguments) == 0:
            usage()
            
        # checking each argument
        for currentArgument, currentValue in arguments:            
            if currentArgument in ("-h", "--help"):
                usage()
                break
            
            elif currentArgument in ("-f", "--filter"):
                print ("Adding filter: ", currentValue, " to describe_instances Filter")
                filter=currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()
        exit()
        
    # Go through each of the US regions
    for i in regions:
        instances=[]
        # Connect to the region
        region = i
        ec2 = boto3.client('ec2', region_name=region)

        masterFilter=filter + "-*master*"
        workerFilter=filter + "-*worker*"
        hostedClusterFilter= "*" + filter + "*"
        # Find the instances that are part of our clusters
        # The instances tag are tagged as 'master' and 'worker'
        # so we filter on that.
        response = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        masterFilter,
                        workerFilter,
                        hostedClusterFilter,
                    ],
                },
            ],
        )

        # Parse the Reservations response and find the instances queried
        for r in response['Reservations']:
            for i in r['Instances']:
                fFoundInstances = True
                item={}
                items = i['Tags'] #.get('Name')
                for x in items:
                  keys=x.keys()
                  if 'Name' in x['Key']:
                    item = x
                    break
                value=item['Value']
                # Append to the array of instances to be started
                print ("Region: [" + region + "] Tag: [" + item['Value'].ljust(44,' ') + "] " + "Instance id: [" + i['InstanceId'].ljust(15, ' ') + "] State: " + i['State']['Name']) 

      
    # Check to see if we found matching instances
    if fFoundInstances == False:
        strregions=','.join([str(region) for region in regions])
        print('No instances found in regions [' + strregions + '] that match filter [' + masterFilter + " and " + workerFilter + " or " + hostedClusterFilter + ']')

if __name__ == "__main__":
    main()

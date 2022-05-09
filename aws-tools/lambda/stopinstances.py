import boto3

# Array of regions we want to scan for running instances
regions=['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']

# Dictionary that holds the key/value pair for each region
# key = key e.g. 'us-west-1'
# value = array e.g. ['i-003cf2aedc58219bf', 'i-0852da9f9b599e873', 'i-06b7b658e21e5e726', 'i-00fa6d35fea24c33b', 'i-0f5746bb760cab75b', 'i-021ec39d1d4bf6c7e']
allInstances={}

# Array of instances that are running for a region and we want to stop
instances = []

# Go through each of the US regions
for i in regions:
  # Connect to the region
  region = i
  ec2 = boto3.client('ec2', region_name=region)

  # Find the instances that are part of our clusters
  # The instances tag are tagged as 'master' and 'worker'
  # so we filter on that.
  response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    '*master*',
                    '*worker*',
                ],
            },
        ],
    )

  # Parse the Reservations response and find the instances queried
  for r in response['Reservations']:
    for i in r['Instances']:
      # Append to the array of instances to be stopped.
      if i['State']['Name'] == 'running':
        instances.append(i['InstanceId'])
  # Add the instance array to the dictionary for the region
  allInstances[region] = instances
  # Reset the array
  instances=[]
  
# Lambda function to stop the instances in each region
def lambda_handler(event, context):
    for key, value in allInstances.items():
      ec2 = boto3.client('ec2', key)
      if len(value):
        ec2.stop_instances(InstanceIds=value)
        print('In Region [' + key + '] stopped your instances: ' + str(value))
      else:
        print('No instances to stop in region: ' + key)

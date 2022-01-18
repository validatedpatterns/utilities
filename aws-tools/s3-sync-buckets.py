#!/usr/bin/env python
import boto3
import os
import botocore
from botocore.exceptions import ClientError
import sys
import getopt
import os
import json

regions=['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

if aws_access_key_id == "" or aws_secret_access_key == "":
  print("Please make sure that you set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables for AWS access")
  exit()


# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hs:t:r:"

# Long options
long_options = ["help", "source", "target", "region"]

def usage():
  msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -s or --source \n" \
        "    S3 source bucket name to copy contents from \n" \
        "    Example: -s my-bucket \n" \
        " -t or --target \n" \
        "    S3 target bucket name to copy contents to \n" \
        "    Example: -t my-other-bucket \n" \
        " -r or --region \n" \
        "    AWS region for bucket \n" \
        "    Example: -r us-west-1 \n" \
        " -h or --help \n" \
        "    Usage message"
  print(msg)
  exit()


def getS3Session():
  try:
    #Creating Session With Boto3.
    session = boto3.Session( 
      aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
      aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    )
    return session
  except ClientError as e:
    print("Could not get S3 Session")
    print(e)
    raise
  
def getS3Resource():
  try:
    session = getS3Session()
    #Creating S3 Resource From the Session.
    s3 = session.resource('s3')
    return s3
  except ClientError as e:
    print("Could not get S3 resource")
    print(e)
    raise
  
def sync_buckets(s3, source_bucket, target_bucket):
  try: 
    srcbucket = s3.Bucket(source_bucket)
    destbucket = s3.Bucket(target_bucket)
    
    # Iterate All Objects in Your S3 Bucket Over the for Loop
    for file in srcbucket.objects.all():
      copy_source = {
        'Bucket': 'com.validated-patterns.xray-source',
        'Key': file.key
      }
      
      destbucket.copy(copy_source, file.key)
      print(file.key +'- File Copied')
    return True
  except ClientError as e:
    print("Could not sync buckets: [" + source_bucket + "] ==> [" + target_bucket + "]")
    print(e)
    raise
  
def main():
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
            elif currentArgument in ("-s", "--source"):
                print ("Source S3 Bucket: ", currentValue)
                source_bucket=currentValue
            elif currentArgument in ("-t", "--target"):
                print ("Target S3 Bucket: ", currentValue)
                target_bucket=currentValue
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()
        exit()

    if source_bucket == "":
        print("Missing required source bucket name")
        usage()
        
    if target_bucket == "":
        print("Missing required target bucket name")
        usage()

    s3 = getS3Resource()
    result = sync_buckets(s3, source_bucket, target_bucket)

    if result:
        print ("Sync successful!")

      
if __name__ == "__main__":
    main()
        

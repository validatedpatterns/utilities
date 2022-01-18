#!/usr/bin/python

import boto3
import botocore
from botocore.exceptions import ClientError
import sys
import getopt
import os

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
options = "hb:r:"

# Long options
long_options = ["help", "bucket", "region"]

def usage():
  msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -b or --bucket \n" \
        "    S3 bucket name to create \n" \
        "    Example: -b my-bucket \n" \
        " -r or --region \n" \
        "    AWS region for bucket \n" \
        "    Example: -r us-west-1 \n" \
        " -h or --help \n" \
        "    Usage message"
  print(msg)
  exit()

def getSTSClient ():
    try:
        sts = boto3.client('sts')
        return sts
    except ClientError:
        print ("Could not create STS client")
        raise
    
def getSTSSessionToken( sts ):
    try:
        token = sts.get_session_token()
        sessionToken = token['Credentials']['SessionToken']
        return sessionToken
    except ClientError:
        print("Could not retrieve STS Session Token")
        raise

def getS3Resource(region=None):
  """
    Get a Boto 3 Amazon S3 resource with a specific AWS Region or with your
    default AWS Region.
  """
  return boto3.resource('s3', region_name=region) if region else boto3.resource('s3')
  
def getS3Client():
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id = aws_access_key_id,
                          aws_secret_access_key = aws_secret_access_key,
                          config=botocore.client.Config(signature_version = 's3'))
        return s3
    except ClientError:
        print("Could not retrieve S3 client")
        raise

def list_my_buckets(s3):
    print('Buckets:\n\t', *[b.name for b in s3.buckets.all()], sep="\n\t")
    
def delete_bucket(s3, bucket_name):
    try:
      print ("Removing all objects from [" + bucket_name + "]")
      bucket = s3.Bucket(bucket_name)
      bucket.objects.all().delete()
      result = bucket.delete()
      print ("Bucket [" + bucket_name + "] removed")
      return result
    except ClientError as e:
      print("Could not delete bucket [" + bucket_name + "]")
      print(e)
      raise
  
def main():
    bucket=""
    region=""

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
            elif currentArgument in ("-b", "--bucket"):
                print ("Target S3 Bucket to be removed: ", currentValue)
                bucket=currentValue
            elif currentArgument in ("-r", "--region"):
                print ("Target S3 region: ", currentValue)
                region=currentValue
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()
        exit()
      
    if bucket == "":
      print ("Missing required bucket name")
      usage()

    if region == "":
      print ("Missing required region name")
      usage()
    
    s3 = getS3Resource(region)
    result = delete_bucket(s3, bucket)

    if result:
      print (result)
      
if __name__ == "__main__":
    main()

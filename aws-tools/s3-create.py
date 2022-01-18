#!/usr/bin/python

import boto3
import botocore
from botocore.exceptions import ClientError
import sys
import getopt
import os
import json

regions=['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']

try:
  aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
  aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
except:
  print("Please make sure that you set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables for AWS access")
  exit()

if aws_access_key_id == "" or aws_secret_access_key == "":
  print("Please make sure that you set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables for AWS access")
  exit()

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hpb:r:"

# Long options
long_options = ["help", "bucket", "region", "public"]

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
    
def getS3Client(region):
    endpoint_url = 'https://s3.' + region + '.amazonaws.com' 

    try:
        s3 = boto3.client('s3',
                          endpoint_url = endpoint_url,
                          aws_access_key_id = aws_access_key_id,
                          aws_secret_access_key = aws_secret_access_key,
                          region_name = region,
                          config=botocore.client.Config(signature_version = 's3'))
        return s3
    except ClientError:
        print("Could not retrieve S3 client")
        raise

def getSNSClient(region):
    endpoint_url = 'https://s3.' + region + '.amazonaws.com' 

    sts = getSTSClient()
    sessionToken = getSTSSessionToken(sts)
    try:
        sns = boto3.client('sns',
                           endpoint_url = endpoint_url,
                           aws_access_key_id = aws_access_key_id,
                           aws_secret_access_key= aws_secret_access_key,
                           aws_session_token=sessionToken,
                           region_name=region,
                           config=botocore.client.Config(signature_version = 's3'))
        return sns
    except ClientError:
        print ("Could not retrieve SNS client")
        raise
    
def create_bucket(s3, bucket_name, region, public=None):
    try:
        result = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        if public:
          arn=[]
          arn.append("arn:aws:s3:::" + bucket_name)
          arn.append("arn:aws:s3:::" + bucket_name + "/*")
          policy={
            "Version": "2012-10-17",
            "Statement": [
              {
                "Sid": "AllowALLStatement1",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": arn
              }
            ]
          }
          # Convert the policy from JSON dict to string
          bucket_policy = json.dumps(policy)
          myresult=getS3Client(region).put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
          AUTH_PUBLIC_ACL={ 
                "Grantee": { 
                  "Type": "Group", 
                  "URI": "http://acs.amazonaws.com/groups/global/AuthenticatedUsers" 
                }, 
                "Permission": "READ_ACP"
              }
          AUTH_READ_PUBLIC_ACL={ 
                "Grantee": { 
                  "Type": "Group", 
                  "URI": "http://acs.amazonaws.com/groups/global/AuthenticatedUsers" 
                }, 
                "Permission": "READ"
              }
          EVERYONE_PUBLIC_ACL={ 
                "Grantee": { 
                  "Type": "Group", 
                  "URI": "http://acs.amazonaws.com/groups/global/AllUsers" 
                }, 
                "Permission": "READ_ACP"
              }
          EVERYONE_READ_PUBLIC_ACL={ 
                "Grantee": { 
                  "Type": "Group", 
                  "URI": "http://acs.amazonaws.com/groups/global/AllUsers" 
                }, 
                "Permission": "READ"
              }
          bucket = s3.Bucket(bucket_name)
          bucket_acl = s3.BucketAcl(bucket_name)
          owner={}
          owner['ID']=bucket_acl.grants[0]['Grantee']['ID']
          owner['DisplayName']=bucket_acl.grants[0]['Grantee']['DisplayName']
          bucket_acl.grants.append(AUTH_PUBLIC_ACL)
          bucket_acl.grants.append(AUTH_READ_PUBLIC_ACL)
          bucket_acl.grants.append(EVERYONE_PUBLIC_ACL)
          bucket_acl.grants.append(EVERYONE_READ_PUBLIC_ACL)
          mydict={}
          mydict['Grants']=bucket_acl.grants
          mydict['Owner']=owner
          bucket_acl.put(AccessControlPolicy=mydict)
          return result
    except ClientError as e:
        print("Could not create bucket [" + bucket_name + "]")
        print(e)
        raise
  
def main():
    bucket=""
    region=""
    public=None

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
                print ("Creating S3 Bucket: ", currentValue)
                bucket=currentValue
            elif currentArgument in ("-r", "--region"):
                print ("Target S3 Bucket Region: ", currentValue)
                region=currentValue
            elif currentArgument in ("-p", "--public"):
                print ("WARNING: S3 Bucket will be made public.")
                public=True

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()
        exit()

    if region == "":
      print ("Missing required region")
      usage()
      
    if bucket == "":
      print ("Missing required bucket name")
      usage()
    
    s3Client = getS3Client(region)
    s3 = boto3.resource('s3')
    sns = getSNSClient(region)
    result = create_bucket(s3, bucket, region, public)

    if result:
      print ("Bucket [" + bucket + "] created successfully")

      
if __name__ == "__main__":
    main()

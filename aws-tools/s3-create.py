#!/usr/bin/python

import boto3
import botocore
from botocore.exceptions import ClientError
import sys
import getopt
import os
import json

regions = ["us-west-1", "us-west-2", "us-east-1", "us-east-2"]

try:
    aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
except KeyError:
    print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables for AWS access.")
    exit()

if not aws_access_key_id or not aws_secret_access_key:
    print("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables cannot be empty.")
    exit()

argumentList = sys.argv[1:]
options = "hpb:r:"
long_options = ["help", "bucket", "region", "public"]


def usage():
    msg = (
        "Usage: python " + sys.argv[0] + "\n"
        "Options: \n"
        " -b or --bucket \n"
        "    S3 bucket name to create \n"
        "    Example: -b my-bucket \n"
        " -r or --region \n"
        "    AWS region for bucket \n"
        "    Example: -r us-west-1 \n"
        " -h or --help \n"
        "    Usage message"
    )
    print(msg)
    exit()


def get_s3_client(region):
    endpoint_url = f"https://s3.{region}.amazonaws.com"
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region,
            config=botocore.client.Config(signature_version="s3v4"),
        )
        return s3
    except ClientError:
        print("Could not retrieve S3 client.")
        raise


def create_bucket(s3_client, bucket_name, region, public=None):
    try:
        # For us-east-1, do not include CreateBucketConfiguration
        if region == "us-east-1":
            result = s3_client.create_bucket(Bucket=bucket_name)
        else:
            result = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )

        if public:
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": False,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": False,
                    "RestrictPublicBuckets": False,
                },
            )
            arn = [f"arn:aws:s3:::{bucket_name}", f"arn:aws:s3:::{bucket_name}/*"]
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowALLStatement1",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "s3:*",
                        ],
                        "Resource": arn,
                    }
                ],
            }
            s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

        return result

    except ClientError as e:
        print(f"Could not create bucket [{bucket_name}]")
        print(e)
        raise


def main():
    bucket = ""
    region = ""
    public = None

    try:
        arguments, _ = getopt.getopt(argumentList, options, long_options)

        if not arguments:
            usage()

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--help"):
                usage()
            elif currentArgument in ("-b", "--bucket"):
                print("Creating S3 Bucket: ", currentValue)
                bucket = currentValue
            elif currentArgument in ("-r", "--region"):
                print("Target S3 Bucket Region: ", currentValue)
                region = currentValue
            elif currentArgument in ("-p", "--public"):
                print("WARNING: S3 Bucket will be made public.")
                public = True

    except getopt.error as err:
        print(str(err))
        usage()

    if not region:
        print("Missing required region.")
        usage()

    if not bucket:
        print("Missing required bucket name.")
        usage()

    s3_client = get_s3_client(region)
    result = create_bucket(s3_client, bucket, region, public)

    if result:
        print(f"Bucket [{bucket}] created successfully.")


if __name__ == "__main__":
    main()

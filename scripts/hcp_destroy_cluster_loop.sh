#!/bin/bash

REGION="us-west-2"
BASE_DOMAIN="aws.validatedpatterns.io"
ROLE_ARN="arn:aws:iam::296267305927:role/hypershift_cli_role"
STS_CREDS="$HOME/sts-creds/sts-creds.json"

for i in {1..10}; do
    CLUSTER="studentcluster-$i"
    
    echo "Refreshing STS credentials..."
    aws sts get-session-token --output json > "$STS_CREDS"

    if [ $? -ne 0 ]; then
        echo "Failed to refresh STS credentials. Aborting..."
        exit 1
    fi

    echo "Destroying cluster: $CLUSTER in region: $REGION"

    trap "echo 'Aborting script...'; exit 1" SIGINT

    RETRIES=3
    while [ $RETRIES -gt 0 ]; do
        hcp destroy cluster aws --destroy-cloud-resources \
            --name "$CLUSTER" \
            --infra-id "$CLUSTER" \
            --region="$REGION" \
            --sts-creds "$STS_CREDS" \
            --base-domain "$BASE_DOMAIN" \
            --role-arn "$ROLE_ARN"

        if [ $? -eq 0 ]; then
            echo "Successfully destroyed $CLUSTER"
            break
        else
            echo "Failed to destroy $CLUSTER, retrying... ($((RETRIES-1)) attempts left)"
            ((RETRIES--))
        fi
    done

    if [ $RETRIES -eq 0 ]; then
        echo "Failed to destroy $CLUSTER after multiple attempts. Moving to the next cluster..."
    fi
done


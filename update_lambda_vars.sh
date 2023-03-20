#!/bin/bash

clear
echo "Set Lambda environment variables..."

# Read environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Send environment variables to AWS Lambda
aws lambda update-function-configuration --function-name LOOD_GADS_SHOPIFY_DOCKER --environment Variables="{REFRESH_TOKEN=$REFRESH_TOKEN,CLIENT_ID=$CLIENT_ID,CLIENT_SECRET=$CLIENT_SECRET,CLIENT_CUSTOMER_ID=$CLIENT_CUSTOMER_ID,ENV=$ENV,CONVERSION_ACTION_ID=$CONVERSION_ACTION_ID,ACCESS_TOKEN=$ACCESS_TOKEN,DEVELOPER_TOKEN=$DEVELOPER_TOKEN}"

echo "Vars: $REFRESH_TOKEN, $CLIENT_ID, $CLIENT_SECRET, $CLIENT_CUSTOMER_ID, $ENV, $CONVERSION_ACTION_ID, $ACCESS_TOKEN, $DEVELOPER_TOKEN"

echo "Done!"
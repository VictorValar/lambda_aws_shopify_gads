# lambda_aws_shopify_gads


## Overview
The app.py file contains the lambda function that is triggered by AWS Event Bridge when a new order is created in Shopify. The function then calls the Google Ads API to create a conversion event for the order.
## Setup
### 1. Create .env file
You must have an .env file in the root directory of the project with the variables described in update_env_vars.py.
Please refer to the [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/oauth/overview) for more information on how to create the Google Ads API credentials.
The google ads functions code comes from [Google's documentation](https://developers.google.com/google-ads/api/docs/conversions/upload-clicks).

### 2. Create a fuction in AWS Lambda
You may create the function either via AWS UI or via the AWS CLI.
```shell
 aws lambda create-function --function-name test-python-lambda --code ImageUri=<registry URI>:<image version> --role <IAM Role> --package-type Image
```

### 3. Modfy upload_to_aws.sh
Modify the update_env_vars.py file to include the correct values for yout application. Then run the following command to update the .env file with the correct values:
```bash
 /.upload_to_aws.sh
```

The script will:
 - Build the Docker image
 - Tag the image
 - Push the image to AWS ECR
 - Update the AWS Lambda function with the new image


 ### 4. Update the Lambda environment variables
 Run the following command to update the AWS Lambda function with the values from the .env file:
 ```shell
 /.update_lambda_vars.sh
```
The script will:
 - Read the .env file
 - Update the AWS Lambda function with the values from the .env file


#!/bin/bash

clear
echo "Building docker image..."
docker -t "$DOCKER_IMAGE_NAME" .

echo 'Tagging image...'
docker tag "$DOCKER_IMAGE_NAME" "$DOCKER_REGISTRY/$DOCKER_IMAGE_NAME"

echo "Pushing image to AWS ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${DOCKER_TAG}

echo "Updating lambda function..."
aws lambda update-function-code --function-name "$FUNCTION_NAME" --image-uri "$DOCKER_REGISTRY/$DOCKER_IMAGE_NAME:latest"

echo "Done!"
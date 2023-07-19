#!/bin/bash

clear
echo "Building docker image..."
docker -t "$DOCKER_IMAGE_NAME" .

echo 'Tagging image...'
docker tag "$DOCKER_IMAGE_NAME" "$DOCKER_REGISTRY/$DOCKER_IMAGE_NAME"

echo "Pushing image to Docker registry..."
docker push "$DOCKER_REGISTRY/$DOCKER_IMAGE_NAME"

echo "Updating lambda function..."
aws lambda update-function-code --function-name "$FUNCTION_NAME" --image-uri "$DOCKER_REGISTRY/$DOCKER_IMAGE_NAME:latest"

echo "Done!"
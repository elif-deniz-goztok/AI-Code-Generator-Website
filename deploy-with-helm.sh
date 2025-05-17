#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t code-generator:latest .

# Deploy using Helm
echo "Deploying with Helm..."
helm install my-codegen ./codegen-chart

echo "Deployment initiated. Use the following commands to check status:"
echo "kubectl get pods -n codegen"
echo "kubectl get svc -n codegen"

echo "To access the application, check the service details:"
echo "kubectl get svc code-generator-service -n codegen" 
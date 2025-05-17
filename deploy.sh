#!/bin/bash

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Minikube is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install it first."
    exit 1
fi

# Start minikube if it's not running
if ! minikube status | grep -q "Running"; then
    echo "Starting minikube..."
    minikube start
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t code-generator:latest .

# Load the image into minikube
echo "Loading image into minikube..."
minikube image load code-generator:latest

# Apply Kubernetes configurations
echo "Deploying Ollama..."
kubectl apply -f k8s/ollama.yaml

echo "Deploying code-generator..."
kubectl apply -f k8s/code-generator.yaml

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=ollama --timeout=300s
kubectl wait --for=condition=ready pod -l app=code-generator --timeout=300s

# Get the service URL
echo "Getting service URL..."
SERVICE_URL=$(minikube service code-generator-service --url)
echo "Code generator service is available at: $SERVICE_URL"

# Show pod status
echo "Pod status:"
kubectl get pods

# Show service status
echo "Service status:"
kubectl get services 
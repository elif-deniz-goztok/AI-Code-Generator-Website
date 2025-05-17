@echo off
setlocal enabledelayedexpansion

:: Check if minikube is installed
where minikube >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Minikube is not installed. Please install it first.
    exit /b 1
)

:: Check if kubectl is installed
where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo kubectl is not installed. Please install it first.
    exit /b 1
)

:: Start minikube if it's not running
minikube status | findstr "Running" >nul
if %ERRORLEVEL% neq 0 (
    echo Starting minikube...
    minikube start
)

:: Build the Docker image
echo Building Docker image...
docker build -t code-generator:latest .

:: Load the image into minikube
echo Loading image into minikube...
minikube image load code-generator:latest

:: Apply Kubernetes configurations
echo Deploying Ollama...
kubectl apply -f k8s\ollama.yaml

echo Deploying code-generator...
kubectl apply -f k8s\code-generator.yaml

:: Wait for pods to be ready
echo Waiting for pods to be ready...
kubectl wait --for=condition=ready pod -l app=ollama --timeout=300s
kubectl wait --for=condition=ready pod -l app=code-generator --timeout=300s

:: Get the service URL
echo Getting service URL...
for /f "tokens=*" %%a in ('minikube service code-generator-service --url') do set SERVICE_URL=%%a
echo Code generator service is available at: %SERVICE_URL%

:: Show pod status
echo Pod status:
kubectl get pods

:: Show service status
echo Service status:
kubectl get services 
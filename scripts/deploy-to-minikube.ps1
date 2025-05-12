# Verify Minikube is running
$minikubeStatus = (minikube status --format='{{.Host}}' 2>&1)
if ($minikubeStatus -ne 'Running') {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow
    minikube start --driver=docker
}

# Get the root directory of the project
$rootDir = Join-Path $PSScriptRoot ".."

# Configure Docker to use Minikube's Docker daemon
Write-Host "Configuring Docker to use Minikube's Docker daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env | Invoke-Expression

# Build Docker image directly in Minikube
Write-Host "Building Docker image in Minikube..." -ForegroundColor Yellow
docker build --no-cache -t muhammadhaziq123/mlops-project:latest $rootDir

# Apply Kubernetes configuration
Write-Host "Applying Kubernetes deployments and services..." -ForegroundColor Yellow
kubectl apply -f "$rootDir\k8s\deployment.yaml"
kubectl apply -f "$rootDir\k8s\service.yaml"
kubectl apply -f "$rootDir\k8s\mlflow-deployment.yaml"
kubectl apply -f "$rootDir\k8s\mlflow-service.yaml"

# Wait for deployments to be ready
Write-Host "Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/mlops-project
kubectl rollout status deployment/mlflow

# Display information about accessing the service
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "To access the application, run:" -ForegroundColor Yellow
Write-Host "kubectl port-forward service/mlops-project-service 8000:8000" -ForegroundColor Green
Write-Host "Then open http://localhost:8000 in your browser" -ForegroundColor Yellow
Write-Host "To access MLflow, run:" -ForegroundColor Yellow
Write-Host "kubectl port-forward service/mlflow-service 5000:5000" -ForegroundColor Green
Write-Host "Then open http://localhost:5000 in your browser" -ForegroundColor Yellow
Write-Host "To view the Kubernetes dashboard, run: minikube dashboard" -ForegroundColor Yellow 
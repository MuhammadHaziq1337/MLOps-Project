# Verify Minikube is running
$minikubeStatus = (minikube status --format='{{.Host}}' 2>&1)
if ($minikubeStatus -ne 'Running') {
    Write-Host "Minikube is not running." -ForegroundColor Yellow
    exit 0
}

# Get the root directory of the project
$rootDir = Join-Path $PSScriptRoot ".."

# Delete all resources
Write-Host "Deleting Kubernetes resources..." -ForegroundColor Yellow
kubectl delete -f "$rootDir\k8s\deployment.yaml" --ignore-not-found
kubectl delete -f "$rootDir\k8s\service.yaml" --ignore-not-found
kubectl delete -f "$rootDir\k8s\mlflow-deployment.yaml" --ignore-not-found
kubectl delete -f "$rootDir\k8s\mlflow-service.yaml" --ignore-not-found

Write-Host "All Kubernetes resources have been deleted." -ForegroundColor Green
Write-Host "To stop Minikube completely, run: minikube stop" -ForegroundColor Yellow 
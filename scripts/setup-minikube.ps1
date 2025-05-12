# Start Minikube if not running
$minikubeStatus = (minikube status --format='{{.Host}}' 2>&1)
if ($minikubeStatus -ne 'Running') {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow
    minikube start --driver=docker
} else {
    Write-Host "Minikube is already running." -ForegroundColor Green
}

# Enable ingress addon
Write-Host "Enabling Minikube ingress addon..." -ForegroundColor Yellow
minikube addons enable ingress

# Configure Docker to use Minikube's Docker daemon
Write-Host "To configure Docker to use Minikube's Docker daemon, run:" -ForegroundColor Yellow
Write-Host "& minikube -p minikube docker-env | Invoke-Expression" -ForegroundColor Green

Write-Host "Minikube setup complete! Use deploy-to-minikube.ps1 to deploy your application." -ForegroundColor Green 
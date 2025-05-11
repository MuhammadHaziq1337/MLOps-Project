# PowerShell script for Kubernetes deployment

# Default values
$Environment = "dev"
$Version = "latest"
$Namespace = "mlops"
$KubeContext = ""

# Parse command line arguments
for ($i = 0; $i -lt $args.Count; $i++) {
    switch ($args[$i]) {
        "--env" {
            $Environment = $args[$i+1]
            $i++
        }
        "--version" {
            $Version = $args[$i+1]
            $i++
        }
        "--namespace" {
            $Namespace = $args[$i+1]
            $i++
        }
        "--context" {
            $KubeContext = $args[$i+1]
            $i++
        }
        default {
            Write-Error "Unknown option: $($args[$i])"
            exit 1
        }
    }
}

# Set Kubernetes context if provided
if ($KubeContext) {
    Write-Host "Setting Kubernetes context to $KubeContext"
    kubectl config use-context $KubeContext
}

Write-Host "Deploying to environment: $Environment"
Write-Host "Using image version: $Version"
Write-Host "Using namespace: $Namespace"

# Create namespace if it doesn't exist
$namespaceExists = $false
try {
    $namespaceExists = kubectl get namespace $Namespace -o json | ConvertFrom-Json
}
catch {
    Write-Host "Namespace $Namespace doesn't exist. Creating..."
    kubectl create -f k8s/namespace.yaml
}

# Replace the VERSION placeholder in yaml files
Write-Host "Replacing version placeholder..."
Get-ChildItem -Path k8s -Filter "*.yaml" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace '{{VERSION}}', $Version | Set-Content $_.FullName
}

# Apply Kubernetes resources
Write-Host "Applying Kubernetes resources..."
kubectl apply -k k8s/

# Wait for deployments to be ready
Write-Host "Waiting for deployments to be ready..."
kubectl rollout status deployment/mlops-project -n $Namespace
kubectl rollout status deployment/mlflow -n $Namespace

Write-Host "Deployment completed successfully!" 
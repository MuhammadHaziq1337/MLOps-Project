# PowerShell script for Docker operations in the MLOps project

# Configuration
$REPO_NAME = "innovateanalytics"
$PROJECT_NAME = "mlops-project"
$DEFAULT_VERSION = "latest"

# Helper function for usage
function Show-Usage {
    Write-Host "Usage: .\$($MyInvocation.MyCommand.Name) [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build       Build Docker images"
    Write-Host "  push        Push Docker images to Docker Hub"
    Write-Host "  buildpush   Build and push Docker images"
    Write-Host "  run         Run a specific container"
    Write-Host "  stop        Stop all containers"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Version    Image version tag (default: latest)"
    Write-Host "  -Service    Service to build/push (default: all)"
    Write-Host "              Values: app, mlflow"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\$($MyInvocation.MyCommand.Name) build"
    Write-Host "  .\$($MyInvocation.MyCommand.Name) push -Version v1.0.0"
    Write-Host "  .\$($MyInvocation.MyCommand.Name) buildpush -Service app -Version v1.0.0"
}

# Parse command line arguments
$Command = $args[0]
$Service = "all"
$Version = $DEFAULT_VERSION

# Check if a command was provided
if (-not $Command) {
    Show-Usage
    exit 1
}

# Parse parameters
for ($i = 1; $i -lt $args.Count; $i++) {
    switch ($args[$i]) {
        "-Version" {
            $Version = $args[$i+1]
            $i++
        }
        "-Service" {
            $Service = $args[$i+1]
            $i++
        }
        default {
            Write-Host "Unknown option: $($args[$i])"
            Show-Usage
            exit 1
        }
    }
}

# Function to build Docker images
function Build-Images {
    param (
        [string]$Service,
        [string]$Version
    )
    
    Write-Host "Building Docker images with tag: $Version"
    
    if ($Service -eq "all" -or $Service -eq "app") {
        Write-Host "Building app image..."
        docker build -t "$REPO_NAME/$PROJECT_NAME:$Version" .
        if (-not $?) {
            Write-Host "Error building app image" -ForegroundColor Red
            exit 1
        }
    }
    
    if ($Service -eq "all" -or $Service -eq "mlflow") {
        Write-Host "Building MLflow image..."
        docker build -t "$REPO_NAME/$PROJECT_NAME-mlflow:$Version" -f mlflow/Dockerfile .
        if (-not $?) {
            Write-Host "Error building MLflow image" -ForegroundColor Red
            exit 1
        }
    }
}

# Function to push Docker images
function Push-Images {
    param (
        [string]$Service,
        [string]$Version
    )
    
    Write-Host "Pushing Docker images with tag: $Version"
    
    if ($Service -eq "all" -or $Service -eq "app") {
        Write-Host "Pushing app image..."
        docker push "$REPO_NAME/$PROJECT_NAME:$Version"
        if (-not $?) {
            Write-Host "Error pushing app image" -ForegroundColor Red
            exit 1
        }
    }
    
    if ($Service -eq "all" -or $Service -eq "mlflow") {
        Write-Host "Pushing MLflow image..."
        docker push "$REPO_NAME/$PROJECT_NAME-mlflow:$Version"
        if (-not $?) {
            Write-Host "Error pushing MLflow image" -ForegroundColor Red
            exit 1
        }
    }
}

# Validate command
switch ($Command) {
    "build" {
        Build-Images -Service $Service -Version $Version
    }
    "push" {
        Push-Images -Service $Service -Version $Version
    }
    "buildpush" {
        Build-Images -Service $Service -Version $Version
        Push-Images -Service $Service -Version $Version
    }
    "run" {
        Write-Host "Starting $Service service in container..."
        docker-compose up -d $Service
    }
    "stop" {
        Write-Host "Stopping all containers..."
        docker-compose down
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Usage
        exit 1
    }
}

Write-Host "Operation completed successfully!" -ForegroundColor Green 
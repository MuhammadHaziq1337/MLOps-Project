# PowerShell script to run the ML pipeline in Docker

# Display the help message
function Show-Help {
    Write-Host "Innovate Analytics MLOps Pipeline"
    Write-Host "=================================="
    Write-Host ""
    Write-Host "Usage: .\run_pipeline.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start         Start the Docker services (MLflow, App)"
    Write-Host "  stop          Stop the Docker services"
    Write-Host "  process       Run data processing step"
    Write-Host "  train         Run model training step"
    Write-Host "  serve         Start the model API server"
    Write-Host "  pipeline      Run the complete ML pipeline"
    Write-Host "  airflow       Start Airflow services"
    Write-Host "  logs          View logs for a service"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Dataset      Dataset to use (iris, california_housing) [default: iris]"
    Write-Host "  -ModelType    Model type (classification, regression) [default: classification]"
    Write-Host "  -Service      Service name for 'logs' command (app, mlflow, airflow)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_pipeline.ps1 start                  # Start all services"
    Write-Host "  .\run_pipeline.ps1 process -Dataset iris  # Process the iris dataset"
    Write-Host "  .\run_pipeline.ps1 train                  # Train a model with default settings"
    Write-Host "  .\run_pipeline.ps1 pipeline               # Run the complete pipeline"
    Write-Host "  .\run_pipeline.ps1 logs -Service app      # View logs for the app service"
}

# Start Docker services
function Start-Services {
    Write-Host "Starting Docker services..."
    docker-compose up -d
    Write-Host "Services started. MLflow UI available at http://localhost:5000"
}

# Stop Docker services
function Stop-Services {
    Write-Host "Stopping Docker services..."
    docker-compose down
    Write-Host "Services stopped."
}

# Run a command in the dev container
function Run-InContainer {
    param (
        [string]$Command,
        [string[]]$Arguments
    )
    
    Write-Host "Running command in dev container: $Command $Arguments"
    docker-compose run --rm dev python -m scripts.ml_pipeline $Command $Arguments
}

# View logs for a service
function View-Logs {
    param (
        [string]$Service
    )
    
    if ([string]::IsNullOrEmpty($Service)) {
        Write-Host "Error: Service name is required" -ForegroundColor Red
        Write-Host "Example: .\run_pipeline.ps1 logs -Service app"
        exit 1
    }
    
    Write-Host "Viewing logs for $Service service..."
    docker-compose logs -f $Service
}

# Start Airflow services
function Start-Airflow {
    Write-Host "Starting Airflow services..."
    Push-Location airflow
    docker-compose up -d
    Pop-Location
    Write-Host "Airflow started. UI available at http://localhost:8081"
}

# Parse command line arguments
param (
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter()]
    [string]$Dataset = "iris",
    
    [Parameter()]
    [string]$ModelType = "classification",
    
    [Parameter()]
    [string]$Service = ""
)

# Execute the requested command
switch ($Command) {
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "process" {
        Run-InContainer -Command "process" -Arguments @("--dataset", $Dataset)
    }
    "train" {
        Run-InContainer -Command "train" -Arguments @("--dataset", $Dataset, "--model-type", $ModelType, "--use-mlflow")
    }
    "serve" {
        Write-Host "Starting model serving..."
        docker-compose up -d app
        Write-Host "Model API is available at http://localhost:8000"
        Write-Host "API documentation: http://localhost:8000/docs"
    }
    "pipeline" {
        Run-InContainer -Command "pipeline" -Arguments @("--dataset", $Dataset, "--model-type", $ModelType, "--use-mlflow")
    }
    "airflow" {
        Start-Airflow
    }
    "logs" {
        View-Logs -Service $Service
    }
    default {
        Show-Help
        exit 1
    }
}

exit 0 
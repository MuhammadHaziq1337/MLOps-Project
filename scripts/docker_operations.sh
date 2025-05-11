#!/bin/bash
# Utility script for Docker operations in the MLOps project

set -e

# Configuration
REPO_NAME="innovateanalytics"
PROJECT_NAME="mlops-project"
DEFAULT_VERSION="latest"

# Helper function for usage
function show_usage {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker images"
    echo "  push        Push Docker images to Docker Hub"
    echo "  buildpush   Build and push Docker images"
    echo "  run         Run a specific container"
    echo "  stop        Stop all containers"
    echo ""
    echo "Options:"
    echo "  --version   Image version tag (default: latest)"
    echo "  --service   Service to build/push (default: all)"
    echo "              Values: app, mlflow"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 push --version v1.0.0"
    echo "  $0 buildpush --service app --version v1.0.0"
}

# Parse command line arguments
COMMAND=$1
shift

VERSION=$DEFAULT_VERSION
SERVICE="all"

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to build Docker images
function build_images {
    local service=$1
    local version=$2
    
    echo "Building Docker images with tag: $version"
    
    if [[ "$service" == "all" || "$service" == "app" ]]; then
        echo "Building app image..."
        docker build -t $REPO_NAME/$PROJECT_NAME:$version .
    fi
    
    if [[ "$service" == "all" || "$service" == "mlflow" ]]; then
        echo "Building MLflow image..."
        docker build -t $REPO_NAME/$PROJECT_NAME-mlflow:$version -f mlflow/Dockerfile .
    fi
}

# Function to push Docker images
function push_images {
    local service=$1
    local version=$2
    
    echo "Pushing Docker images with tag: $version"
    
    if [[ "$service" == "all" || "$service" == "app" ]]; then
        echo "Pushing app image..."
        docker push $REPO_NAME/$PROJECT_NAME:$version
    fi
    
    if [[ "$service" == "all" || "$service" == "mlflow" ]]; then
        echo "Pushing MLflow image..."
        docker push $REPO_NAME/$PROJECT_NAME-mlflow:$version
    fi
}

# Validate command
case $COMMAND in
    build)
        build_images $SERVICE $VERSION
        ;;
    push)
        push_images $SERVICE $VERSION
        ;;
    buildpush)
        build_images $SERVICE $VERSION
        push_images $SERVICE $VERSION
        ;;
    run)
        echo "Starting $SERVICE service in container..."
        docker-compose up -d $SERVICE
        ;;
    stop)
        echo "Stopping all containers..."
        docker-compose down
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

echo "Operation completed successfully!"
exit 0 
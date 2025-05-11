#!/bin/bash
# Script to run the ML pipeline in Docker

set -e

# Display the help message
function show_help {
    echo "Innovate Analytics MLOps Pipeline"
    echo "=================================="
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start         Start the Docker services (MLflow, App)"
    echo "  stop          Stop the Docker services"
    echo "  process       Run data processing step"
    echo "  train         Run model training step"
    echo "  serve         Start the model API server"
    echo "  pipeline      Run the complete ML pipeline"
    echo "  airflow       Start Airflow services"
    echo "  logs          View logs for a service"
    echo ""
    echo "Options:"
    echo "  --dataset     Dataset to use (iris, california_housing) [default: iris]"
    echo "  --model-type  Model type (classification, regression) [default: classification]"
    echo "  --service     Service name for 'logs' command (app, mlflow, airflow)"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 process --dataset iris   # Process the iris dataset"
    echo "  $0 train                    # Train a model with default settings"
    echo "  $0 pipeline                 # Run the complete pipeline"
    echo "  $0 logs --service app       # View logs for the app service"
}

# Start Docker services
function start_services {
    echo "Starting Docker services..."
    docker-compose up -d
    echo "Services started. MLflow UI available at http://localhost:5000"
}

# Stop Docker services
function stop_services {
    echo "Stopping Docker services..."
    docker-compose down
    echo "Services stopped."
}

# Run a command in the dev container
function run_in_container {
    CMD=$1
    shift
    
    echo "Running command in dev container: $CMD $@"
    docker-compose run --rm dev python -m scripts.ml_pipeline $CMD "$@"
}

# View logs for a service
function view_logs {
    SERVICE=$1
    
    if [ -z "$SERVICE" ]; then
        echo "Error: Service name is required"
        echo "Example: $0 logs --service app"
        exit 1
    fi
    
    echo "Viewing logs for $SERVICE service..."
    docker-compose logs -f $SERVICE
}

# Start Airflow services
function start_airflow {
    echo "Starting Airflow services..."
    cd airflow && docker-compose up -d
    echo "Airflow started. UI available at http://localhost:8081"
}

# Parse command line arguments
COMMAND=$1
shift

# Default values
DATASET="iris"
MODEL_TYPE="classification"
SERVICE=""

# Parse options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --model-type)
            MODEL_TYPE="$2"
            shift 2
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute the requested command
case $COMMAND in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    process)
        run_in_container "process" "--dataset" "$DATASET"
        ;;
    train)
        run_in_container "train" "--dataset" "$DATASET" "--model-type" "$MODEL_TYPE" "--use-mlflow"
        ;;
    serve)
        echo "Starting model serving..."
        docker-compose up -d app
        echo "Model API is available at http://localhost:8000"
        echo "API documentation: http://localhost:8000/docs"
        ;;
    pipeline)
        run_in_container "pipeline" "--dataset" "$DATASET" "--model-type" "$MODEL_TYPE" "--use-mlflow"
        ;;
    airflow)
        start_airflow
        ;;
    logs)
        view_logs $SERVICE
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0 
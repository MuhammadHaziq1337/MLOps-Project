# Docker Guide

This guide explains how to use Docker for development, testing, and deployment of the Innovate Analytics MLOps project.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

## Docker Services

Our project uses Docker Compose to define and run multiple services:

1. **app**: The FastAPI application that serves model predictions
2. **mlflow**: MLflow tracking server for experiment tracking
3. **dev**: Development environment for running training jobs and utilities

## Getting Started

### Building and Starting Services

```bash
# Build and start all services
docker-compose up -d

# Build and start specific services
docker-compose up -d app mlflow
```

### Accessing Services

- **FastAPI App**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)

### Using the Development Container

The development container provides an environment for running model training, tests, and other development tasks.

```bash
# Execute commands in the dev container
docker-compose exec dev python -m src.models.run_training --dataset iris

# Run DVC commands in the container
docker-compose exec dev dvc repro

# Run tests in the container
docker-compose exec dev pytest
```

## Building Custom Images

To build and push custom Docker images:

```bash
# Build the API image
docker build -t innovateanalytics/mlops-project:latest .

# Push to Docker Hub (requires authentication)
docker push innovateanalytics/mlops-project:latest
```

## Environment Variables

Key environment variables that control the Docker services:

| Variable | Description | Default |
|----------|-------------|---------|
| MODEL_PATH | Path to the model directory | models |
| MLFLOW_TRACKING_URI | URI for MLflow tracking server | http://mlflow:5000 |

## Production Deployment

For production, we recommend:

1. Building specific version-tagged images
2. Using Kubernetes for orchestration (see [kubernetes_guide.md](kubernetes_guide.md))
3. Using proper secrets management for sensitive configuration

## Troubleshooting

### Common Issues

- **Model loading errors**: Ensure model files are correctly placed in the mounted volumes
- **Permission issues**: Check file permissions in mounted volumes
- **Network errors**: Verify that services can communicate with each other

For more help, check container logs:

```bash
docker-compose logs app
docker-compose logs mlflow
``` 
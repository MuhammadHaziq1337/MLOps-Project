# MLOps Project for Innovate Analytics Inc.

[![Continuous Integration](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml)
[![Build and Push Docker Image](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml)

This repository contains an end-to-end MLOps implementation for a machine learning system that processes large datasets, trains predictive models, and deploys them in a scalable and reliable manner.

## Project Structure

```
├── .github/workflows        # GitHub Actions workflows for CI/CD
├── .github/ISSUE_TEMPLATE   # Templates for GitHub issues
├── airflow/                 # Airflow DAGs for data pipelines
├── data/                    # Data directory (with .gitignore for DVC)
│   ├── raw/                 # Raw data
│   ├── processed/           # Processed data
├── docs/                    # Project documentation
├── k8s/                     # Kubernetes deployment files
├── metrics/                 # Model metrics tracked by DVC
├── models/                  # Model storage
├── monitoring/              # Monitoring infrastructure (Prometheus, Grafana)
│   ├── prometheus/          # Prometheus configurations
│   ├── grafana/             # Grafana dashboards and configurations
├── notebooks/               # Jupyter notebooks for exploration
├── scripts/                 # Utility scripts
├── src/                     # Source code
│   ├── data/                # Data processing modules
│   ├── features/            # Feature engineering
│   ├── models/              # Model training and evaluation
│   ├── visualization/       # Data visualization
│   └── app/                 # Model serving application
├── tests/                   # Unit and integration tests
│   ├── test_metrics.py      # Tests for monitoring metrics module
│   ├── test_monitoring_k8s.py # Tests for Kubernetes monitoring configs
│   ├── test_docker_monitoring.py # Tests for Docker monitoring integration
├── .dvc/                    # DVC configuration
├── dvc.yaml                 # DVC pipeline definition
├── .gitignore               # Git ignore file
├── Dockerfile               # Dockerfile for containerization
├── Jenkinsfile              # Jenkins pipeline definition
├── docker-compose.yml       # Docker compose for local development
├── requirements.txt         # Python dependencies
└── setup.py                 # Package installation
```

## Sprint Planning and Team Collaboration

We follow an agile development process with 2-week sprints. Our team collaboration workflow is built around GitHub Issues and Projects.

### Agile Process

- **Sprint Planning**: Monday (Day 1) - Plan tasks for the next 2 weeks
- **Daily Standups**: Every weekday at 10:00 AM
- **Sprint Review**: Friday (Day 10) - Demo completed work
- **Sprint Retrospective**: Friday (Day 10) - Review and improve process

### Issue Templates

We use standardized templates for different types of work:

- **[Feature Request](/.github/ISSUE_TEMPLATE/feature_request.md)**: For proposing new features
- **[Bug Report](/.github/ISSUE_TEMPLATE/bug_report.md)**: For reporting bugs or issues
- **[Sprint Task](/.github/ISSUE_TEMPLATE/sprint_task.md)**: For specific tasks within a sprint
- **[Technical Debt](/.github/ISSUE_TEMPLATE/tech_debt.md)**: For tracking technical debt

### Creating Sprint Tasks

1. Go to the [Issues](../../issues) tab
2. Click "New Issue"
3. Select the "Sprint Task" template
4. Fill in the details including description, acceptance criteria, and estimation
5. Assign to a team member
6. Add to the appropriate sprint milestone

### Branch Management for Development

Our project uses a structured branch strategy:

1. **main**: Production-ready code
2. **test**: Integration testing branch
3. **dev**: Development branch where features are integrated
4. Feature branches: Created from dev for specific tasks

### Pull Request Process

All code changes follow our [Pull Request Template](/.github/PULL_REQUEST_TEMPLATE.md):

1. Create a feature branch from dev
2. Make your changes in small, logical commits
3. Create a PR targeting the dev branch
4. Ensure CI checks pass
5. Get approval from at least one team member
6. Merge to dev

### Project Board

Our [Project Board](../../projects) tracks the status of all issues:

- **Backlog**: Tasks for future sprints
- **To Do**: Tasks scheduled for the current sprint
- **In Progress**: Tasks currently being worked on
- **Review**: Tasks ready for review/testing
- **Done**: Completed tasks

## Data Versioning with DVC

We use Data Version Control (DVC) to manage datasets and ML pipelines. DVC allows us to track large data files without storing them in Git.

### Basic DVC Commands

```bash
# Track a dataset
python -m scripts.data_versioning track data/raw/iris.csv

# Update a dataset 
python -m scripts.data_versioning update data/raw/iris.csv --tag v1.0

# Run the ML pipeline
python -m scripts.data_versioning run
```

For detailed instructions, see our [Data Versioning Guide](docs/data_versioning.md).

## MLOps Workflow

1. **Development**: Feature branches -> Dev branch
2. **Testing**: Dev branch -> Test branch (after PR approval)
3. **Production**: Test branch -> Main branch (after testing)

## CI/CD Pipeline

The project includes a CI/CD pipeline that automates building, testing, and deploying the application. The pipeline is implemented using GitHub Actions and Jenkins.

### GitHub Actions CI Workflow

The GitHub Actions workflow performs the following steps:
1. Runs linting and code quality checks
2. Runs unit tests
3. Runs monitoring tests
4. Runs integration tests
5. Builds and pushes Docker images

### Setting up GitHub Secrets for Docker Authentication

To enable Docker image push to DockerHub in the GitHub Actions workflow, you need to set up the following repository secrets:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `DOCKERHUB_USERNAME`: Your DockerHub username
   - `DOCKERHUB_TOKEN`: Your DockerHub Personal Access Token (not your password)

To create a DockerHub Personal Access Token:
1. Log in to your DockerHub account
2. Go to Account Settings → Security → New Access Token
3. Give your token a description (e.g., "GitHub Actions")
4. Select appropriate permissions (at least "Read & Write")
5. Copy the generated token and add it as the `DOCKERHUB_TOKEN` secret in GitHub

### Jenkins Pipeline

The Jenkins pipeline complements GitHub Actions and performs additional deployment steps:
1. Checks out the code
2. Builds and tests the application
3. Builds Docker images 
4. Pushes Docker images to registry
5. Deploys to target environments

## Tools Used

- **Version Control**: Git, GitHub
- **Data Version Control**: DVC
- **Experiment Tracking**: MLflow
- **Pipeline Orchestration**: Airflow
- **Containerization**: Docker, Docker Hub
- **CI/CD**: GitHub Actions, Jenkins
- **Deployment**: Kubernetes (Minikube)
- **ML Framework**: Scikit-learn
- **Monitoring**: Prometheus, Grafana

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Pull data files: `dvc pull`
4. Run the ML pipeline: `dvc repro`
5. Run the development server: `docker-compose up`

## Docker Development

We use Docker and Docker Compose for containerized development, testing, and deployment:

### Docker Services
- **FastAPI App**: Machine learning model serving API
- **MLflow**: Experiment tracking server
- **Development Container**: For data processing and model training

### Running with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Run commands in the dev container
docker-compose exec dev python -m src.models.run_training --dataset iris
```

For more details, see our [Docker Guide](/docs/docker_guide.md).

## Kubernetes Deployment

The project can be deployed to a Kubernetes cluster using the provided manifests and scripts.

### Prerequisites

- A running Kubernetes cluster
- `kubectl` configured to connect to your cluster
- Docker images pushed to a container registry

### Deployment Steps

1. **Check deployment prerequisites**:

```bash
# Check if your setup is ready for deployment
python scripts/k8s_deploy.py --check-only
```

2. **Deploy to Kubernetes**:

```bash
# Deploy all components to a 'mlops' namespace
python scripts/k8s_deploy.py --namespace mlops
```

3. **Deploy specific components**:

```bash
# Deploy only monitoring components
python scripts/k8s_deploy.py --namespace mlops --component monitoring
```

## Monitoring & Observability

We've implemented comprehensive monitoring for ML model performance and system health using Prometheus and Grafana:

### Key Metrics Being Tracked

- **API Performance**: Request counts, latencies, error rates
- **ML Model Metrics**: Prediction counts by class, prediction latencies
- **Feature Statistics**: Mean and standard deviation of features in predictions
- **Data Drift**: Metrics to track drift between training and production data

### Running Monitoring Tests

We have extensive test coverage for our monitoring infrastructure:

```bash
# Run all monitoring-related tests
python scripts/run_monitoring_tests.py
```

This will test:
- Metrics collection module functionality
- Kubernetes configurations for Prometheus and Grafana
- Docker integration with monitoring

### Prometheus Configuration

Prometheus is configured to scrape metrics from:
- The FastAPI application (ML model metrics)
- Kubernetes pods with appropriate annotations
- Node exporter for system metrics

### Grafana Dashboards

Pre-configured dashboards provide visualization for:
- API request statistics
- Prediction counts by class
- Feature distribution and drift
- System resource utilization

## Troubleshooting

### Feature Name Mismatch Error

If you encounter an error like:
```
ERROR:__main__:Prediction error: The feature names should match those that were passed during fit.
```

This indicates a mismatch between the feature names used during model training and those provided in prediction requests. The issue occurs because:

1. Scikit-learn models (from version 1.0+) track feature names used during training
2. When making predictions, the order and names of features must match exactly

To fix this issue, we've implemented a solution in the FastAPI prediction endpoint:
- The endpoint checks if the model has a `feature_names_in_` attribute
- It ensures all required features are present in the request
- It reorders the input features to match the order expected by the model

If you modify the model training or feature engineering, make sure to:
- Maintain consistent feature names throughout the pipeline
- Update the prediction input schema in `src/app/main.py` if feature names change
- Run tests on the API to verify compatibility after model updates

## Team Collaboration

We use GitHub Issues for sprint planning, task allocation, and progress tracking. See the [Issues](../../issues) tab for current tasks and milestones.

## ML Pipeline Usage

The ML pipeline can be run using the provided scripts:

### Using the Shell Script (Linux/macOS)

```bash
# Start Docker services
./scripts/run_pipeline.sh start

# Process the iris dataset
./scripts/run_pipeline.sh process --dataset iris

# Train a model
./scripts/run_pipeline.sh train --dataset iris --model-type classification

# Start the model API server
./scripts/run_pipeline.sh serve

# Run the complete pipeline (process, train, and serve)
./scripts/run_pipeline.sh pipeline

# Start Airflow for workflow orchestration
./scripts/run_pipeline.sh airflow

# View logs for a service
./scripts/run_pipeline.sh logs --service app
```

### Using PowerShell (Windows)

```powershell
# Start Docker services
.\scripts\run_pipeline.ps1 start

# Process the iris dataset
.\scripts\run_pipeline.ps1 process -Dataset iris

# Train a model
.\scripts\run_pipeline.ps1 train -Dataset iris -ModelType classification

# Start the model API server
.\scripts\run_pipeline.ps1 serve

# Run the complete pipeline (process, train, and serve)
.\scripts\run_pipeline.ps1 pipeline

# Start Airflow for workflow orchestration
.\scripts\run_pipeline.ps1 airflow

# View logs for a service
.\scripts\run_pipeline.ps1 logs -Service app
```

### Available Endpoints

Once the services are running, you can access:

- **FastAPI App**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)
- **Airflow UI**: [http://localhost:8081](http://localhost:8081)

### Using the API

```bash
# Test prediction endpoint with curl
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2}}'
``` 
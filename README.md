# MLOps Project for Innovate Analytics Inc.

[![Continuous Integration](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml)
[![Build and Push Docker Image](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml)

This repository contains an end-to-end MLOps implementation for a machine learning system that processes large datasets, trains predictive models, and deploys them in a scalable and reliable manner.

## Project Structure

```
├── .github/workflows        # GitHub Actions workflows for CI/CD
├── airflow/                 # Airflow DAGs for data pipelines
├── data/                    # Data directory (with .gitignore for DVC)
│   ├── raw/                 # Raw data
│   ├── processed/           # Processed data
├── docs/                    # Project documentation
├── k8s/                     # Kubernetes deployment files
├── models/                  # Model storage
├── notebooks/               # Jupyter notebooks for exploration
├── scripts/                 # Utility scripts
├── src/                     # Source code
│   ├── data/                # Data processing modules
│   ├── features/            # Feature engineering
│   ├── models/              # Model training and evaluation
│   ├── visualization/       # Data visualization
│   └── app/                 # Model serving application
├── tests/                   # Unit and integration tests
├── .gitignore               # Git ignore file
├── Dockerfile               # Dockerfile for containerization
├── Jenkinsfile              # Jenkins pipeline definition
├── docker-compose.yml       # Docker compose for local development
├── requirements.txt         # Python dependencies
└── setup.py                 # Package installation
```

## MLOps Workflow

1. **Development**: Feature branches -> Dev branch
2. **Testing**: Dev branch -> Test branch (after PR approval)
3. **Production**: Test branch -> Main branch (after testing)

## CI/CD Pipeline

- **GitHub Actions**: Linting, unit testing on PR/push to dev
- **Jenkins**: Build Docker image and push to Docker Hub
- **Kubernetes**: Deployment to Minikube cluster

## Tools Used

- **Version Control**: Git, GitHub
- **Data Version Control**: DVC
- **Experiment Tracking**: MLflow
- **Pipeline Orchestration**: Airflow
- **Containerization**: Docker, Docker Hub
- **CI/CD**: GitHub Actions, Jenkins
- **Deployment**: Kubernetes (Minikube)
- **ML Framework**: Scikit-learn

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up local environment variables
4. Run the development server: `docker-compose up`

## Team Collaboration

We use GitHub Issues for sprint planning, task allocation, and progress tracking. See the [Issues](../../issues) tab for current tasks and milestones. 
# MLOps Project for Innovate Analytics Inc.

[![Continuous Integration](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/ci.yml)
[![Build and Push Docker Image](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml/badge.svg)](https://github.com/MuhammadHaziq1337/MLOps-Project/actions/workflows/docker.yml)

An end-to-end MLOps implementation for machine learning systems that processes large datasets, trains predictive models, and deploys them in a scalable and reliable manner.

## Project Components

- **FastAPI Application**: Model serving with RESTful endpoints for predictions
- **MLflow**: Experiment tracking and model registry
- **Docker**: Containerization of all components
- **Jenkins**: CI/CD pipeline for automated builds and deployments
- **GitHub Actions**: Automated testing and linting
- **Kubernetes**: Scalable deployment on Minikube

## Project Structure

```
├── .github/workflows/       # GitHub Actions workflows for CI/CD
├── airflow/                 # Airflow DAGs for data pipelines
├── data/                    # Data directory (with .gitignore for DVC)
│   ├── raw/                 # Raw data
│   ├── processed/           # Processed data
├── k8s/                     # Kubernetes deployment files
├── models/                  # Model storage
├── scripts/                 # Utility scripts
├── src/                     # Source code
│   ├── data/                # Data processing modules
│   ├── features/            # Feature engineering
│   ├── models/              # Model training and evaluation
│   ├── visualization/       # Data visualization
│   └── app/                 # Model serving application
├── tests/                   # Unit and integration tests
├── Dockerfile               # Dockerfile for containerization
├── Dockerfile.jenkins       # Custom Jenkins Docker image
├── Jenkinsfile              # Jenkins pipeline definition
├── docker-compose.yml       # Docker compose for local development
├── requirements.txt         # Python dependencies
└── setup.py                 # Package installation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Minikube (for Kubernetes deployment)
- kubectl
- Python 3.9+

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MuhammadHaziq1337/MLOps-Project.git
   cd MLOps-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Train a demo model:
   ```bash
   python scripts/train_demo_model.py
   ```

4. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Access the services:
   - FastAPI application: http://localhost:8000
   - MLflow: http://localhost:5000
   - FastAPI Swagger documentation: http://localhost:8000/docs

### Setting Up Jenkins CI/CD

1. Build and run the custom Jenkins container:
   ```powershell
   .\scripts\start-custom-jenkins.ps1
   ```

2. Access Jenkins at http://localhost:8082
   - Get the initial admin password with:
     ```powershell
     docker exec jenkins-docker cat /var/jenkins_home/secrets/initialAdminPassword
     ```

3. Configure Jenkins with your DockerHub credentials:
   - Add credentials with ID 'dockerhub'

### Deploying to Kubernetes (Minikube)

1. Start Minikube:
   ```powershell
   .\scripts\setup-minikube.ps1
   ```

2. Deploy the application to Minikube:
   ```powershell
   .\scripts\deploy-to-minikube.ps1
   ```

3. Access the services:
   ```powershell
   # For the main application
   kubectl port-forward service/mlops-project-service 8000:8000
   # For MLflow
   kubectl port-forward service/mlflow-service 5000:5000
   ```

4. To view the Kubernetes dashboard:
   ```bash
   minikube dashboard
   ```

5. To clean up resources:
   ```powershell
   .\scripts\cleanup-minikube.ps1
   ```

## API Endpoints

- **GET /health**: Health check endpoint
- **POST /predict**: Make predictions with JSON data
- **GET /model/info**: Get information about the loaded model

### Example Prediction Request

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}}'
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

## Troubleshooting

- **"This site can't be reached"**: If port forwarding fails, try a different local port:
  ```powershell
  kubectl port-forward service/mlops-project-service 8001:8000
  ```

- **Model not loading**: Ensure you've run the train_demo_model.py script and rebuilt the Docker image.

- **Jenkins Docker integration issues**: Make sure Docker socket is correctly mounted and Jenkins has permission to access it.

## Contributors

- Your Name
- Collaborator Names

## License

MIT 
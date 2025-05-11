pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    
    environment {
        DOCKER_HUB_CREDS = credentials('dockerhub-credentials')
        REPO_NAME = 'innovateanalytics'
        PROJECT_NAME = 'mlops-project'
        VERSION = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                
                // Install dependencies for CI/CD
                sh 'apt-get update && apt-get install -y docker.io git'
                sh 'pip install pytest pytest-cov pylint black isort flake8 dvc requests'
            }
        }
        
        stage('Linting & Code Style') {
            steps {
                // Run linting checks
                sh 'flake8 src/ tests/ scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics'
                
                // Check code formatting
                sh 'black --check src/ tests/ scripts/'
                sh 'isort --check-only src/ tests/ scripts/'
            }
        }
        
        stage('Unit Tests') {
            steps {
                // Run unit tests with coverage
                sh 'python -m pytest tests/ --cov=src --cov=scripts --cov-report=xml:coverage.xml'
                
                // Archive test results
                archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
            }
        }
        
        stage('Monitoring Tests') {
            steps {
                // Verify monitoring configurations
                sh 'python scripts/run_monitoring_tests.py'
                
                // Verify Prometheus config contains ML metrics
                sh '''
                if ! grep -q "ml-model-metrics" monitoring/prometheus/prometheus.yml; then
                    echo "Prometheus configuration is missing ML model metrics job"
                    exit 1
                fi
                '''
                
                // Verify Grafana dashboards contain model prediction metrics
                sh '''
                if ! grep -q "model_prediction_count" monitoring/grafana/grafana-k8s.yaml; then
                    echo "Grafana dashboard is missing model prediction metrics"
                    exit 1
                fi
                '''
                
                // Run monitoring test script in Docker
                sh 'python scripts/test_monitoring_in_docker.py --skip-cleanup'
            }
        }
        
        stage('Data Versioning') {
            steps {
                // Pull data from DVC remote
                sh 'dvc pull'
                
                // Run DVC pipeline to process data and train model
                sh 'dvc repro'
                
                // Capture and archive metrics
                sh 'dvc metrics show --json > metrics_report.json'
                archiveArtifacts artifacts: 'metrics_report.json', fingerprint: true
            }
        }
        
        stage('Build Docker Images') {
            steps {
                // Log in to Docker Hub
                sh 'echo $DOCKER_HUB_CREDS_PSW | docker login -u $DOCKER_HUB_CREDS_USR --password-stdin'
                
                // Build FastAPI app image
                sh "docker build -t ${REPO_NAME}/${PROJECT_NAME}:${VERSION} -t ${REPO_NAME}/${PROJECT_NAME}:latest ."
                
                // Build MLflow image
                sh "docker build -t ${REPO_NAME}/${PROJECT_NAME}-mlflow:${VERSION} -t ${REPO_NAME}/${PROJECT_NAME}-mlflow:latest -f mlflow/Dockerfile ."
                
                // Build Prometheus image
                sh "docker build -t ${REPO_NAME}/${PROJECT_NAME}-prometheus:${VERSION} -t ${REPO_NAME}/${PROJECT_NAME}-prometheus:latest -f monitoring/prometheus/Dockerfile monitoring/prometheus/"
                
                // Build Grafana image
                sh "docker build -t ${REPO_NAME}/${PROJECT_NAME}-grafana:${VERSION} -t ${REPO_NAME}/${PROJECT_NAME}-grafana:latest -f monitoring/grafana/Dockerfile monitoring/grafana/"
            }
        }
        
        stage('Push Docker Images') {
            when {
                branch 'main'
            }
            steps {
                // Push images to Docker Hub
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}:${VERSION}"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}:latest"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-mlflow:${VERSION}"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-mlflow:latest"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-prometheus:${VERSION}"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-prometheus:latest"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-grafana:${VERSION}"
                sh "docker push ${REPO_NAME}/${PROJECT_NAME}-grafana:latest"
            }
        }
        
        stage('Update Kubernetes Manifests') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Update image tags in Kubernetes manifests
                    sh "sed -i 's|image: ${REPO_NAME}/${PROJECT_NAME}:.*|image: ${REPO_NAME}/${PROJECT_NAME}:${VERSION}|g' k8s/deployment.yaml"
                    sh "sed -i 's|image: ${REPO_NAME}/${PROJECT_NAME}-mlflow:.*|image: ${REPO_NAME}/${PROJECT_NAME}-mlflow:${VERSION}|g' k8s/mlflow-deployment.yaml"
                    sh "sed -i 's|image: ${REPO_NAME}/${PROJECT_NAME}-prometheus:.*|image: ${REPO_NAME}/${PROJECT_NAME}-prometheus:${VERSION}|g' k8s/prometheus-deployment.yaml"
                    sh "sed -i 's|image: ${REPO_NAME}/${PROJECT_NAME}-grafana:.*|image: ${REPO_NAME}/${PROJECT_NAME}-grafana:${VERSION}|g' k8s/grafana-deployment.yaml"
                    
                    // Commit the updated manifests
                    sh 'git config --global user.name "Jenkins CI"'
                    sh 'git config --global user.email "jenkins@example.com"'
                    sh 'git add k8s/deployment.yaml k8s/mlflow-deployment.yaml k8s/prometheus-deployment.yaml k8s/grafana-deployment.yaml'
                    sh "git commit -m 'Update Kubernetes manifest to version ${VERSION}' || echo 'No changes to commit'"
                    
                    // Push the updated manifests to the repository
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        sh "git push https://$GIT_USERNAME:$GIT_PASSWORD@github.com/MuhammadHaziq1337/MLOps-Project.git HEAD:main || echo 'Nothing to push'"
                    }
                }
            }
        }
        
        stage('Deploy to Test Environment') {
            when {
                branch 'test'
            }
            steps {
                // Check connection to Kubernetes
                sh 'kubectl version --client'
                
                // Deploy to test namespace
                sh 'python scripts/k8s_deploy.py --namespace mlops-test'
                
                // Run tests against the deployed API
                sh 'sleep 30' // Wait for deployment
                sh 'python -m scripts.test_api --api-url http://mlops-app.mlops-test.svc.cluster.local:8000 || echo "API Tests failed but continuing"'
                
                // Verify monitoring services are running
                sh 'kubectl get pods -n mlops-test | grep prometheus'
                sh 'kubectl get pods -n mlops-test | grep grafana'
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                // Deploy to production namespace
                sh 'python scripts/k8s_deploy.py --namespace mlops-prod'
                
                // Verify deployment
                sh 'kubectl get pods -n mlops-prod'
            }
        }
    }
    
    post {
        always {
            // Clean up Docker containers from monitoring tests
            sh 'docker rm -f mlops-app-test mlops-prometheus-test mlops-grafana-test || true'
            sh 'docker network rm mlops-test-network || true'
            
            // Clean up
            sh 'docker logout'
            
            // Notify
            emailext (
                subject: "${currentBuild.result}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>${currentBuild.result}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
} 
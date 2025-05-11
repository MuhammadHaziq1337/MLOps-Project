pipeline {
    agent {
        docker {
            image 'python:3.9'
        }
    }
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = 'muhammadhaziq123/mlops-project'
    }
    
    stages {
        stage('Install dependencies') {
            steps {
                sh 'pip install -e .[dev]'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'flake8 src tests'
                sh 'black --check src tests'
                sh 'isort --check-only --profile black src tests'
                sh 'mypy src'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest tests --cov=src'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:$BUILD_NUMBER .'
            }
        }
        
        stage('Push Docker Image') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push ${IMAGE_NAME}:$BUILD_NUMBER'
                sh 'docker tag ${IMAGE_NAME}:$BUILD_NUMBER ${IMAGE_NAME}:latest'
                sh 'docker push ${IMAGE_NAME}:latest'
            }
        }
        
        stage('Deploy to K8s') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    sed -i "s/{{VERSION}}/$BUILD_NUMBER/g" k8s/deployment.yaml
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker logout'
        }
    }
} 
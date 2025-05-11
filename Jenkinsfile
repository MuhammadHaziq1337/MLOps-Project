pipeline {
    agent {
        docker {
            image 'python:3.9'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        IMAGE_NAME = 'innovateanalytics/mlops-project'
        VERSION = "${env.BUILD_NUMBER}"
        BUILD_TIMESTAMP = sh(script: 'date +%Y%m%d%H%M%S', returnStdout: true).trim()
    }
    
    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install dependencies') {
            steps {
                sh 'pip install --upgrade pip'
                sh 'pip install -e .[dev]'
            }
        }
        
        stage('Lint') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh 'flake8 src tests'
                    sh 'black --check src tests'
                    sh 'isort --check-only --profile black src tests'
                    sh 'mypy src'
                }
            }
        }
        
        stage('Test') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh 'pytest tests --cov=src --cov-report xml:coverage.xml --junitxml=test-results.xml'
                }
            }
            post {
                always {
                    junit 'test-results.xml'
                    recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build image with multiple tags
                    sh "docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest -t ${IMAGE_NAME}:${BUILD_TIMESTAMP} ."
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    // Login to DockerHub
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                    
                    // Push all tags
                    sh "docker push ${IMAGE_NAME}:${VERSION}"
                    sh "docker push ${IMAGE_NAME}:latest"
                    sh "docker push ${IMAGE_NAME}:${BUILD_TIMESTAMP}"
                    
                    // Tag as stable for non-dev branches
                    if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'test') {
                        sh "docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:${env.BRANCH_NAME}-stable"
                        sh "docker push ${IMAGE_NAME}:${env.BRANCH_NAME}-stable"
                    }
                }
            }
        }
        
        stage('Deploy to Dev K8s') {
            when {
                branch 'dev'
            }
            steps {
                withKubeConfig([credentialsId: 'kubeconfig-dev']) {
                    sh '''
                        sed -i "s|{{IMAGE_NAME}}|${IMAGE_NAME}|g" k8s/deployment.yaml
                        sed -i "s|{{VERSION}}|${VERSION}|g" k8s/deployment.yaml
                        sed -i "s|{{ENV}}|dev|g" k8s/deployment.yaml
                        
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        
                        # Wait for deployment to complete
                        kubectl rollout status deployment/mlops-api -n mlops
                    '''
                }
            }
        }
        
        stage('Deploy to Test K8s') {
            when {
                branch 'test'
            }
            steps {
                withKubeConfig([credentialsId: 'kubeconfig-test']) {
                    sh '''
                        sed -i "s|{{IMAGE_NAME}}|${IMAGE_NAME}|g" k8s/deployment.yaml
                        sed -i "s|{{VERSION}}|${VERSION}|g" k8s/deployment.yaml
                        sed -i "s|{{ENV}}|test|g" k8s/deployment.yaml
                        
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        
                        # Wait for deployment to complete
                        kubectl rollout status deployment/mlops-api -n mlops
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                // Manual approval step for production deployment
                input message: 'Deploy to production?', ok: 'Approve'
                
                withKubeConfig([credentialsId: 'kubeconfig-prod']) {
                    sh '''
                        sed -i "s|{{IMAGE_NAME}}|${IMAGE_NAME}|g" k8s/deployment.yaml
                        sed -i "s|{{VERSION}}|${VERSION}|g" k8s/deployment.yaml
                        sed -i "s|{{ENV}}|prod|g" k8s/deployment.yaml
                        
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml
                        kubectl apply -f k8s/secrets.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/ingress.yaml
                        kubectl apply -f k8s/hpa.yaml
                        
                        # Wait for deployment to complete
                        kubectl rollout status deployment/mlops-api -n mlops
                        
                        # Tag the Docker image as production
                        docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:production
                        docker push ${IMAGE_NAME}:production
                    '''
                }
            }
        }
        
        stage('Run Smoke Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'test'
                    branch 'main'
                }
            }
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh 'python scripts/smoke_tests.py'
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker logout'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 
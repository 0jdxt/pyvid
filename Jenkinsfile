pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
                python --version
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
                pytest
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}

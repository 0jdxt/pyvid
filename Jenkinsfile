pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                python '--version'
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

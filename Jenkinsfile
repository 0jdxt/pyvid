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
                bash 'pytest'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}

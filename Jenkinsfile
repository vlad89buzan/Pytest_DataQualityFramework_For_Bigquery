pipeline {
    agent any

    environment {
        // Example: set environment variables if needed
        PYTHONPATH = "${WORKSPACE}"
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        sh '''
                            . venv/bin/activate
                            mkdir -p reports
                            pytest
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Check HTML reports in Jenkins."
        }
    }
}

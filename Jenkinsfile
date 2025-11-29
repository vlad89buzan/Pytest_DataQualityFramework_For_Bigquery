pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}/venv/bin"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python Env') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                // Inject Jenkins Secret File
                withCredentials([
                    file(credentialsId: 'GSA_NPD', variable: 'GSA_NPD'),
                    file(credentialsId: 'GSA_PPD', variable: 'GSA_PPD'),
                    file(credentialsId: 'GSA_PRD', variable: 'GSA_PRD')
                    ]) {
                    sh '''
                        . venv/bin/activate
                        mkdir -p reports
                        pytest || true
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html'
        }
    }
}

pipeline {
    agent any

    environment {
        ENVIRONMENT = "npd5" // your environment name
        REPORT_DIR = "reports"
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python Environment') {
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
                // Use the secret file from Jenkins
                withCredentials([file(credentialsId: 'GSA_NPD', variable: 'GCP_KEYFILE')]) {
                    sh '''
                        . venv/bin/activate
                        export GOOGLE_APPLICATION_CREDENTIALS=$GCP_KEYFILE
                        mkdir -p ${REPORT_DIR}
                        pytest --html=${REPORT_DIR}/report_$(date +%Y%m%d_%H%M%S).html
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${REPORT_DIR}/*.html", allowEmptyArchive: true
        }
        success {
            echo "Pipeline succeeded!"
        }
        failure {
            echo "Pipeline failed. Check the HTML report for details."
        }
    }
}

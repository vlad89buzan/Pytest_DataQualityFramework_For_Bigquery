pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd5', 'ppd', 'prd'], description: 'Environment to run tests')
        string(name: 'MARKERS', defaultValue: '', description: 'Pytest markers')
    }

    environment {
        // Determine which GSA creds to use
        CREDS_FILE = "${params.ENV.toLowerCase().startsWith('npd') ? 'GSA_NPD' : params.ENV.toLowerCase().startsWith('ppd') ? 'GSA_PPD' : 'GSA_PRD'}"
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    echo "Selected environment: ${params.ENV}"
                    echo "Using credentials: ${CREDS_FILE}"
                }

                // Inject the secret file from Jenkins credentials
                withCredentials([file(credentialsId: "${CREDS_FILE}", variable: 'GCP_KEYFILE')]) {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        echo "GCP credentials file: $GCP_KEYFILE"
                    '''
                }
            }
        }

        stage('Run Pytest') {
            steps {
                withCredentials([file(credentialsId: "${CREDS_FILE}", variable: 'GCP_KEYFILE')]) {
                    sh '''
                        . venv/bin/activate
                        export GOOGLE_APPLICATION_CREDENTIALS=$GCP_KEYFILE
                        pytest ${MARKERS:+-m $MARKERS}
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
        }
    }
}

pipeline {
    agent any

    parameters {
        string(name: 'ENV', defaultValue: 'npd5', description: 'Environment: npd5, ppd, prd')
        string(name: 'MARKERS', defaultValue: '', description: 'Pytest markers (optional)')
    }

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                """
            }
        }

        stage('Determine GCP Credentials') {
            steps {
                script {
                    // Select correct Jenkins secret file based on ENV prefix
                    def envPrefix = params.ENV.toLowerCase()
                    def gsaCreds = envPrefix.startsWith('npd') ? 'GSA_NPD' :
                                   envPrefix.startsWith('ppd') ? 'GSA_PPD' :
                                   envPrefix.startsWith('prd') ? 'GSA_PRD' : null

                    if (gsaCreds == null) {
                        error "Unknown ENV prefix: ${params.ENV}"
                    }

                    env.GSA_CREDS = gsaCreds
                }
            }
        }

        stage('Run Tests') {
            steps {
                withCredentials([file(credentialsId: env.GSA_CREDS, variable: 'CREDS_FILE')]) {
                    sh """
                        set -euo pipefail
                        . ${VENV_DIR}/bin/activate
                        echo "Using credentials file: \$CREDS_FILE"

                        # Run pytest with or without markers
                        if [ -z "${params.MARKERS}" ]; then
                            pytest
                        else
                            pytest -m "${params.MARKERS}"
                        fi
                    """
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
        }
        failure {
            echo "❌ FAILURE — DQ checks failed. Check HTML reports in artifacts."
        }
        success {
            echo "✅ SUCCESS — DQ checks passed."
        }
    }
}

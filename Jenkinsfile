pipeline {
    agent any

    parameters {
        string(name: 'ENV', defaultValue: 'npd5', description: 'Environment to run tests on (npd5, ppd, prd, etc.)')
        string(name: 'MARKERS', defaultValue: '', description: 'Optional pytest markers')
    }

    environment {
        VENV_DIR = "venv"
    }

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Select the proper GSA creds based on ENV prefix
                    def envPrefix = params.ENV?.toLowerCase() ?: ''
                    def gsa_creds = ''
                    if (envPrefix.startsWith('npd')) {
                        gsa_creds = 'GSA_NPD'
                    } else if (envPrefix.startsWith('ppd')) {
                        gsa_creds = 'GSA_PPD'
                    } else if (envPrefix.startsWith('prd')) {
                        gsa_creds = 'GSA_PRD'
                    } else {
                        error "Unknown environment prefix: ${params.ENV}"
                    }

                    withCredentials([file(credentialsId: gsa_creds, variable: 'GSA_')]) {
                        withEnv(["MARKERS=${params.MARKERS ?: ''}"]) {
                            sh """
                                set -euo pipefail
                                . ${VENV_DIR}/bin/activate
                                mkdir -p reports
                                echo "Running tests on ${params.ENV}"
                                echo "Using credentials file: \$GSA_"
                                pytest tests/ \$MARKERS --html=reports/report.html
                            """
                        }
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                publishHTML(target: [
                    reportName: 'Test Report',
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

    }

    post {
        always {
            sh "rm -rf ${VENV_DIR}"
        }
        success {
            echo "✅ Tests completed successfully."
        }
        failure {
            echo "❌ Tests failed — see HTML report for details."
        }
    }
}

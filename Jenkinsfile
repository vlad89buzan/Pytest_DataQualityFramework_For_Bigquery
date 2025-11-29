pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'], description: 'Environment to run tests against')
        string(name: 'MARKERS', defaultValue: '', description: 'Pytest markers to filter tests (optional)')
    }

    environment {
        REPORTS_DIR = 'reports'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def credsId = params.ENV.startsWith('npd') ? 'GSA_NPD' :
                                  params.ENV.startsWith('ppd') ? 'GSA_PPD' :
                                  params.ENV == 'prd' ? 'GSA_PRD' : error("Unknown environment: ${params.ENV}")
                    def credsEnvVar = credsId

                    withCredentials([file(credentialsId: credsId, variable: credsEnvVar)]) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            pytest --env ${params.ENV} -v --tb=short ${params.MARKERS:+-m "$MARKERS"}
                        """
                    }
                }
            }
        }

        stage('Archive and Show Latest Report') {
            steps {
                script {
                    sh 'mkdir -p ${REPORTS_DIR}'
                    archiveArtifacts artifacts: 'reports/*.html', fingerprint: true
                    def latestReport = sh(script: "ls -t reports/*.html | head -1", returnStdout: true).trim()
                    echo "Latest HTML report: ${latestReport}"
                }
            }
        }
    }

    post {
        always {
            junit '**/reports/*.xml'
        }
    }
}

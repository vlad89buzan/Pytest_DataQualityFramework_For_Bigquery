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
                    # Create virtual environment
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    # Upgrade pip
                    pip install --upgrade pip
                    # Install dependencies
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Map ENV to credentials
                    def credsId = params.ENV.startsWith('npd') ? 'GSA_NPD' :
                                  params.ENV.startsWith('ppd') ? 'GSA_PPD' :
                                  params.ENV == 'prd' ? 'GSA_PRD' : error("Unknown environment: ${params.ENV}")

                    def credsEnvVar = credsId

                    withCredentials([file(credentialsId: credsId, variable: credsEnvVar)]) {
                        // Build pytest command
                        def pytestCmd = "pytest --env ${params.ENV} -v --tb=short"
                        if (params.MARKERS) {
                            pytestCmd += " -m \"${params.MARKERS}\""
                        }

                        // Activate virtual environment and run tests
                        sh """
                            source ${VENV_DIR}/bin/activate
                            ${pytestCmd}
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
            // Optionally publish junit XML if your tests generate it
            junit '**/reports/*.xml'
        }
    }
}

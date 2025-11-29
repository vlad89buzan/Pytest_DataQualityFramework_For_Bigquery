pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'], description: 'Environment to run tests against')
        string(name: 'MARKERS', defaultValue: '', description: 'Pytest markers to filter tests (optional)')
    }

    environment {
        REPORTS_DIR = 'reports'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Set Credentials and Run Tests') {
            steps {
                script {
                    // Map environment to credential ID and env var
                    def credsId = ''
                    def credsEnvVar = ''
                    if (params.ENV.startsWith('npd')) {
                        credsId = 'GSA_NPD'
                        credsEnvVar = 'GSA_NPD'
                    } else if (params.ENV.startsWith('ppd')) {
                        credsId = 'GSA_PPD'
                        credsEnvVar = 'GSA_PPD'
                    } else if (params.ENV == 'prd') {
                        credsId = 'GSA_PRD'
                        credsEnvVar = 'GSA_PRD'
                    } else {
                        error "Unknown environment: ${params.ENV}"
                    }

                    // Inject the secret file as environment variable
                    withCredentials([file(credentialsId: credsId, variable: credsEnvVar)]) {
                        // Run pytest with environment parameter and optional markers
                        def pytest_cmd = "pytest --env ${params.ENV} -v --tb=short"
                        if (params.MARKERS) {
                            pytest_cmd += " -m \"${params.MARKERS}\""
                        }
                        sh pytest_cmd
                    }
                }
            }
        }

        stage('Archive and Show Latest Report') {
            steps {
                script {
                    sh 'mkdir -p reports'
                    archiveArtifacts artifacts: 'reports/*.html', fingerprint: true
                    def latestReport = sh(script: "ls -t reports/*.html | head -1", returnStdout: true).trim()
                    echo "Latest HTML report: ${latestReport}"
                }
            }
        }
    }

    post {
        always {
            junit '**/reports/*.xml'  // optional if generating XML
        }
    }
}

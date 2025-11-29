pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'],
               description: 'Target BigQuery environment')
        string(name: 'MARKERS', defaultValue: '', trim: true,
               description: 'Pytest markers (e.g. smoke or "critical and not slow")')
        booleanParam(name: 'CLEAN_WORKSPACE', defaultValue: true,
                     description: 'Clean workspace before build')
    }

    environment {
        VENV_DIR    = "venv"
        REPORTS_DIR = "reports"
    }

    options {
        timeout(time: 90, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timestamps()
    }

    stages {
        stage('Prepare Workspace') {
            when { expression { params.CLEAN_WORKSPACE } }
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def credsId = params.ENV.startsWith('npd') ? 'GSA_NPD' :
                                  params.ENV == 'ppd' || params.ENV == 'ppd1' ? 'GSA_PPD' :
                                  params.ENV == 'prd' ? 'GSA_PRD' :
                                  error("Invalid environment: ${params.ENV}")

                    withCredentials([file(credentialsId: credsId, variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                        sh """
                            #!/usr/bin/env bash
                            set -euo pipefail

                            . ${VENV_DIR}/bin/activate
                            mkdir -p ${REPORTS_DIR}

                            MARKER_CMD=""
                            if [ -n "${params.MARKERS}" ]; then
                                MARKER_CMD="-m ${params.MARKERS}"
                            fi

                            echo "Running tests against environment: ${params.ENV}"
                            echo "Markers: ${params.MARKERS ?: '<none>'}"

                            pytest --env ${params.ENV} \\
                                   -v \\
                                   --tb=short \\
                                   --junitxml=${REPORTS_DIR}/junit_${params.ENV}_${BUILD_NUMBER}.xml \\
                                   \$MARKER_CMD
                        """
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**', fingerprint: true, allowEmptyArchive: false

                script {
                    def latest = sh(script: "ls -t reports/report_*.html 2>/dev/null | head -1 || echo ''",
                                    returnStdout: true).trim()
                    if (latest) {
                        echo "Latest HTML report: ${env.BUILD_URL}artifact/${latest}"
                    }
                }

                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report_*.html',
                    reportName: 'Data Quality HTML Report'
                ])
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/junit_*.xml', allowEmptyResults: true
            sh 'rm -rf ${VENV_DIR}'
        }
        success {
            echo "All tests PASSED on ${params.ENV}!"
        }
        failure {
            echo "Tests FAILED on ${params.ENV} — check the HTML report"
        }
    }
}
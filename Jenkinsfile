pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'],
               description: 'Target BigQuery environment')
        string(name: 'MARKERS', defaultValue: '', trim: true,
               description: 'Pytest markers (e.g. smoke or "critical and not slow")')
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

        stage('Checkout') {
            steps {
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
                    // Map environment to Jenkins credential ID
                    def credId = params.ENV.startsWith('npd') ? 'GSA_NPD' :
                                 params.ENV in ['ppd','ppd1'] ? 'GSA_PPD' :
                                 params.ENV == 'prd' ? 'GSA_PRD' :
                                 error("Unknown environment: ${params.ENV}")

                    withCredentials([file(credentialsId: credId, variable: 'CREDS_FILE')]) {
                        def envVars = [
                            "GSA_NPD=${ params.ENV.startsWith('npd') ? CREDS_FILE : '' }",
                            "GSA_PPD=${ params.ENV in ['ppd','ppd1'] ? CREDS_FILE : '' }",
                            "GSA_PRD=${ params.ENV == 'prd' ? CREDS_FILE : '' }"
                        ]

                        withEnv(envVars) {
                            sh '''
                                #!/usr/bin/env bash
                                set -euo pipefail
                                . ${VENV_DIR}/bin/activate
                                mkdir -p ${REPORTS_DIR}

                                echo "Running tests on ${ENV}"
                                echo "Using credentials file for ${ENV}: $(eval echo \$GSA_${ENV^^} 2>/dev/null || echo 'NOT FOUND')"

                                MARKER_ARG=""
                                [ -n "${MARKERS}" ] && MARKER_ARG="-m '${MARKERS}'"

                                pytest --env ${ENV} \
                                       -v \
                                       --tb=short \
                                       --junitxml=${REPORTS_DIR}/junit_${ENV}_${BUILD_NUMBER}.xml \
                                       $MARKER_ARG
                            '''
                        }
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**', fingerprint: true

                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report_*.html',
                    reportName: 'Data Quality HTML Report'
                ])

                junit testResults: 'reports/junit_*.xml', allowEmptyResults: true
            }
        }
    }

    post {
        always {
            sh 'rm -rf ${VENV_DIR}'
        }
        success {
            echo "✅ SUCCESS — All DQ checks passed on ${params.ENV}!"
        }
        failure {
            echo "❌ FAILURE — DQ checks failed on ${params.ENV} — see HTML report"
        }
    }
}

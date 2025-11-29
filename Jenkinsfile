pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'],
               description: 'Target BigQuery environment')
        string(name: 'MARKERS', defaultValue: '', trim: true,
               description: 'Pytest markers, e.g. "smoke" or "critical and not slow"')
        booleanParam(name: 'CLEAN_WORKSPACE', defaultValue: true,
                     description: 'Clean workspace before build')
    }

    environment {
        VENV_DIR    = "venv"
        REPORTS_DIR = "reports"

        // Credential mapping – super clear and easy to extend
        GSA_CREDENTIALS = credentials("${params.ENV.startsWith('npd') ? 'GSA_NPD' :
                                        params.ENV.startsWith('ppd')  ? 'GSA_PPD' :
                                        params.ENV == 'prd' ? 'GSA_PRD' :
                                        'INVALID'}")
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

        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Data Quality Tests') {
            steps {
                withCredentials([file(credentialsId: "${env.GSA_CREDENTIALS}", variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        . ${VENV_DIR}/bin/activate

                        # Create reports dir (in case no tests run)
                        mkdir -p ${REPORTS_DIR}

                        # Build marker argument only if MARKERS is not empty
                        MARKER_ARG=""
                        if [ -n "${MARKERS}" ]; then
                            MARKER_ARG="-m \\"${MARKERS}\\""
                        fi

                        echo "Running tests against environment: ${ENV}"
                        echo "Markers: ${MARKERS}"

                        # Let conftest.py generate the timestamped report automatically
                        eval pytest --env ${ENV} \
                                     -v \
                                     --tb=short \
                                     --junitxml=${REPORTS_DIR}/junit_${ENV}_${BUILD_NUMBER}.xml \
                                     $MARKER_ARG
                    '''
                }
            }
        }

        stage('Publish Reports') {
            steps {
                script {
                    // Archive everything from reports/
                    archiveArtifacts artifacts: 'reports/*.*', fingerprint: true, allowEmptyArchive: false

                    // Find and display the latest HTML report
                    def latestHtml = sh(script: "ls -t reports/report_*.html 2>/dev/null | head -1 || echo ''",
                                        returnStdout: true).trim()
                    if (latestHtml) {
                        echo "HTML Report → ${env.BUILD_URL}artifact/${latestHtml}"
                    }

                    // Beautiful clickable report in Jenkins UI
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'report_*.html',
                        reportName: 'Data Quality HTML Report',
                        reportTitles: 'BigQuery DQ Results'
                    ])
                }

                // Standard Jenkins test results trending
                junit testResults: 'reports/junit_*.xml', allowEmptyResults: true
            }
        }
    }

    post {
        always {
            // Optional: clean venv to keep agents light
            sh 'rm -rf ${VENV_DIR}'
        }
        success {
            echo "All data quality checks PASSED for ${params.ENV}"
        }
        failure {
            echo "Data quality checks FAILED on ${params.ENV} — check the HTML report above!"
        }
        cleanup {
            // Keep reports only via archiveArtifacts – workspace gets cleaned anyway
            cleanWs(cleanWhenNotBuilt: false, deleteDirs: true)
        }
    }
}
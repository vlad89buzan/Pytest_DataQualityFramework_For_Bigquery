pipeline {

    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd5', 'npd4'], description: 'Select environment')
        string(name: 'MARKERS', defaultValue: '', description: 'Run only tests with markers')
    }

    environment {
        VENV = "venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    ${VENV}/bin/pip install --upgrade pip
                    ${VENV}/bin/pip install -r requirements.txt
                    ${VENV}/bin/pip install pyyaml pytest pytest-html google-cloud-bigquery google-auth
                '''
            }
        }

        stage('Determine Credentials') {
            steps {
                script {
                    if (params.ENV == "npd5") {
                        env.GCP_CREDS = "npd5"   // <-- change to your actual Jenkins credentialsId
                    } else if (params.ENV == "npd4") {
                        env.GCP_CREDS = "npd4"   // <-- change to your actual Jenkins credentialsId
                    } else {
                        error "Unknown environment: ${params.ENV}"
                    }
                    echo "Using GCP credentials: ${env.GCP_CREDS}"
                }
            }
        }

        stage('Run Pytest') {
            steps {
                withCredentials([file(credentialsId: "${GCP_CREDS}", variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                        mkdir -p reports

                        MARKER_OPTION=""
                        if [ ! -z "${MARKERS}" ]; then
                            MARKER_OPTION="-m '${MARKERS}'"
                        fi

                        ${VENV}/bin/pytest \
                            --env ${ENV} \
                            $MARKER_OPTION \
                            --html=reports/report.html \
                            --self-contained-html \
                            --junitxml=reports/results.xml
                    """
                }
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**/*.html', allowEmptyArchive: true
                junit 'reports/results.xml'
            }
        }
    }

    post {
        always {
            echo "Pipeline finished."
        }
    }
}

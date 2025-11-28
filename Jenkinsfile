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

        stage('Prepare Python Environment') {
            steps {
                sh '''
                    echo "Creating virtual environment..."
                    python3 -m venv ${VENV}

                    echo "Upgrading pip inside venv..."
                    ${VENV}/bin/pip install --upgrade pip

                    echo "Installing dependencies inside venv..."
                    ${VENV}/bin/pip install -r requirements.txt
                    ${VENV}/bin/pip install pyyaml pytest pytest-html

                    echo "Python version inside venv:"
                    ${VENV}/bin/python --version
                    ${VENV}/bin/pip --version
                '''
            }
        }

        stage('Read Environment Config') {
            steps {
                sh '''
                    echo "Reading ENV config for ${ENV}"
                    ${VENV}/bin/python ci/read_env_config.py ${ENV}
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                sh """
                    echo "Running tests..."

                    mkdir -p reports

                    MARKER_OPTION=""
                    if [ ! -z "${MARKERS}" ]; then
                        MARKER_OPTION="-m ${MARKERS}"
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

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

                    echo "Activating venv..."
                    . ${VENV}/bin/activate

                    echo "Installing dependencies..."
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pyyaml pytest pytest-html

                    echo "Python inside venv:"
                    ${VENV}/bin/python --version
                '''
            }
        }

        stage('Read Environment Config') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    ${VENV}/bin/python ci/read_env_config.py ${ENV}
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                sh """
                    . ${VENV}/bin/activate

                    mkdir -p reports

                    ${VENV}/bin/pytest \\
                        --env ${ENV} \\
                        ${MARKERS ? "-m ${MARKERS}" : ""} \\
                        --html=reports/report.html \\
                        --self-contained-html \\
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

pipeline {

    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd', 'ws5', 'prod'], description: 'Select environment to run tests')
        string(name: 'MARKERS', defaultValue: '', description: 'Run only tests with these pytest markers')
    }

    stages {

        stage('Install Python') {
            steps {
                sh '''
                    echo "Installing Python 3 and pip..."

                    if ! command -v python3 >/dev/null 2>&1; then
                        sudo apt-get update
                        sudo apt-get install -y python3 python3-pip python3-venv
                    else
                        echo "Python3 already installed"
                    fi

                    python3 --version
                    pip3 --version
                '''
            }
        }

        stage('Install Python Dependencies') {
            steps {
                sh '''
                    pip3 install --upgrade pip
                    pip3 install -r requirements.txt
                    pip3 install pyyaml
                '''
            }
        }

        stage('Read Environment Config') {
            steps {
                sh '''
                    python3 ci/read_env_config.py ${ENV}
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                sh """
                    echo "Running pytest on environment: ${ENV}"

                    pytest \\
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
            echo "Pipeline completed."
        }
    }
}

pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1','npd2','npd3','npd4','npd5','ppd','ppd1','prd'], description: 'Environment to test')
        string(name: 'MARKS', defaultValue: '', description: 'Optional pytest markers, e.g., "smoke or regression"')
    }

    environment {
        PYTHONPATH = "${WORKSPACE}/venv/bin"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python Env') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                withCredentials([
                    file(credentialsId: 'GSA_NPD', variable: 'GSA_NPD'),
                    file(credentialsId: 'GSA_PPD', variable: 'GSA_PPD'),
                    file(credentialsId: 'GSA_PRD', variable: 'GSA_PRD')
                ]) {
                    script {
                        def pytestCmd = ". venv/bin/activate && mkdir -p reports && pytest --env ${params.ENV}"
                        if (params.MARKS?.trim()) {
                            pytestCmd += " -m \"${params.MARKS}\""
                        }
                        pytestCmd += " || true"
                        sh pytestCmd
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive HTML reports
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
        }
    }
}

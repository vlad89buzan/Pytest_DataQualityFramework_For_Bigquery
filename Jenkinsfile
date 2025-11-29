pipeline {
    agent any

    // Optional parameters for environment and pytest marks
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
                // Inject Jenkins Secret Files
                withCredentials([
                    file(credentialsId: 'GSA_NPD', variable: 'GSA_NPD'),
                    file(credentialsId: 'GSA_PPD', variable: 'GSA_PPD'),
                    file(credentialsId: 'GSA_PRD', variable: 'GSA_PRD')
                ]) {
                    script {
                        // Build pytest command dynamically
                        def pytestCmd = ". venv/bin/activate && mkdir -p reports && pytest --env ${params.ENV}"
                        if (params.MARKS?.trim()) {
                            pytestCmd += " -m \"${params.MARKS}\""
                        }
                        pytestCmd += " || true"  // continue even if tests fail
                        sh pytestCmd
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
        }
        // Optionally mark build unstable if pytest failed
        script {
            script {
                def reportFiles = findFiles(glob: 'reports/*.html')
                if (reportFiles.length > 0) {
                    echo "Reports generated: ${reportFiles.collect { it.name }}"
                }
            }
        }
    }
}

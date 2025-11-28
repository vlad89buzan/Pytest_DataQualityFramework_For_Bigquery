pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['npd1', 'npd2','npd3','npd4','npd5','ppd','ppd1','prd'], description: 'Select environment')
        string(name: 'MARK', defaultValue: '', description: 'Pytest marker expression (e.g. smoke or smoke and regression)')
    }

    environment {
        VENV = "${WORKSPACE}/venv"
        GOOGLE_APPLICATION_CREDENTIALS = "${WORKSPACE}/gcp_key.json"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/vlad89buzan/Pytest_DataQualityFramework_For_Bigquery.git'
            }
        }

        stage('Read Environment Config') {
            steps {
                script {
                    // Install Python dependencies for parsing YAML
                    sh 'python -m pip install --upgrade pip pyyaml'

                    // Read YAML and export variables
                    envConfig = sh(
                        script: """python - <<'EOF'
import yaml, os, json
with open('env_config.yaml') as f:
    cfg = yaml.safe_load(f)
env = os.environ['ENV']
config = cfg.get(env, {})
print(json.dumps(config))
EOF
                        """, returnStdout: true
                    ).trim()

                    configMap = readJSON text: envConfig

                    // Set Jenkins env variables dynamically
                    env.GCP_CRED_ID = configMap.gcp_cred
                    env.BQ_PROJECT = configMap.bq_project
                    env.BQ_DATASET = configMap.dataset
                }
            }
        }

        stage('Setup GCP Credentials') {
            steps {
                withCredentials([file(credentialsId: "${GCP_CRED_ID}", variable: 'GCP_KEY')]) {
                    sh 'cp $GCP_KEY $GOOGLE_APPLICATION_CREDENTIALS'
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh """
                python -m venv $VENV
                $VENV/bin/pip install --upgrade pip
                $VENV/bin/pip install -r requirements.txt
                $VENV/bin/pip install pytest-html pytest-xdist pyyaml
                """
            }
        }

        stage('Run Pytest') {
            steps {
                script {
                    def markerOption = params.MARK ? "-m '${params.MARK}'" : ""
                    sh """
                    mkdir -p reports
                    $VENV/bin/pytest tests/ \
                        --env ${ENV} \
                        ${markerOption} \
                        --junitxml=reports/results.xml \
                        --html=reports/report.html \
                        --self-contained-html \
                        -n auto
                    """
                }
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            junit 'reports/results.xml'
            cleanWs()
        }
        failure {
            echo 'Some tests failed! Check HTML report for details.'
        }
    }
}

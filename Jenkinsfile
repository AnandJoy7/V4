pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
        GITHUB_CREDENTIALS    = credentials('github-credentials')
        AWS_DEFAULT_REGION    = 'us-east-1'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install Terraform and Python dependencies
                sh '''
                sudo apt-get update -y
                sudo apt-get install -y python3-pip terraform
                pip3 install boto3
                '''
            }
        }

        stage('Checkout Code') {
            steps {
                script {
                    dir('terraform') {
                        git(
                            url: 'https://github.com/AnandJoy7/terra_pipeline_final.git',
                            branch: 'main',
                            credentialsId: 'github-credentials'
                        )
                    }
                }
            }
        }

        stage('Run Terraform Script') {
            steps {
                dir('terraform') {
                    sh 'python3 terra_auto.py > terraform_output.log 2>&1'
                }
            }
        }
    }

    post {
        always {
            dir('terraform') {
                archiveArtifacts artifacts: 'terraform_output.log', allowEmptyArchive: true
            }
        }
        success {
            echo 'Terraform automation completed successfully.'
        }
        failure {
            echo 'Terraform automation failed. Check the logs for details.'
            dir('terraform') {
                archiveArtifacts artifacts: 'terraform_output.log'
            }
        }
    }
}

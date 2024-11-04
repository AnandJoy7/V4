pipeline {
    agent any
 
    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws_credentials')
        AWS_SECRET_ACCESS_KEY = credentials('aws_credentials')
        GITHUB_PAT            = credentials('github-pat')
        AWS_DEFAULT_REGION    = 'us-east-1'
        PATH = "$PATH:/usr/local/bin:/usr/bin"
    }
 
    stages {
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace...'
                deleteDir()
            }
        }
 
        stage('Setup Python Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip boto3
                '''
            }
        }
 
        stage('Setup Git LFS') {
            steps {
                echo 'Setting up Git LFS...'
                sh '''
                    # Initialize Git LFS
                    /usr/bin/git-lfs install --skip-repo
                   
                    # Verify Git LFS installation
                    /usr/bin/git-lfs version
                '''
            }
        }
 
        stage('Checkout Code') {
            steps {
                dir('terraform') {
                    echo 'Checking out code from GitHub...'
                    git(
                        url: 'https://github.com/AnandJoy7/terra_auto_testing.git',
                        branch: 'main',
                        credentialsId: 'github_credentials'
                    )
                }
            }
        }
 
        stage('Run Terraform Script') {
            steps {
                dir('terraform') {
                    script {
                        echo 'Running Terraform script...'
                        def result = sh(script: '''
                        . ../venv/bin/activate
                        python3 terra_auto8.py > terraform_output.log 2>&1
                        deactivate
                        ''', returnStatus: true)
                        if (result != 0) {
                            error "Terraform script failed. Check terraform_output.log for details."
                        } else {
                            echo "Terraform script ran successfully."
                        }
                    }
                }
            }
        }
 
        stage('Setup Git LFS Tracking') {
            steps {
                dir('terraform') {
                    script {
                        echo 'Setting up Git LFS tracking...'
                        sh '''
                            # Setup Git LFS tracking patterns
                            /usr/bin/git-lfs track "**/.terraform/providers/**/terraform-provider-*"
                            /usr/bin/git-lfs track "*.zip"
                            /usr/bin/git-lfs track "*.tar.gz"
                            /usr/bin/git-lfs track "*.iso"
                           
                            # Create minimal .gitignore
                            echo "# Terraform ignore patterns" > .gitignore
                            echo "crash.log" >> .gitignore
                            echo "crash.*.log" >> .gitignore
                            echo "override.tf" >> .gitignore
                            echo "override.tf.json" >> .gitignore
                            echo "*_override.tf" >> .gitignore
                            echo "*_override.tf.json" >> .gitignore
                            echo "terraform.rc" >> .gitignore
                            echo ".gitattributes" >> .gitignore
                            echo ".gitignore" >> .gitignore
 
                                                       
                            # Add and commit .gitattributes and .gitignore
                            git add .
                            git commit -m "Setup Git LFS tracking and gitignore" || echo "No changes to commit"
                        '''
                    }
                }
            }
        }
 
        stage('Initialize Terraform and Track Providers') {
            steps {
                dir('terraform') {
                    script {
                        echo 'Initializing Terraform and tracking providers...'
                        sh '''
                            # Initialize Terraform
                            terraform init -input=false
                           
                            # Add all files including .terraform directory
                            git add .
                           
                            # Show what's being tracked by Git LFS
                            echo "Files tracked by Git LFS:"
                            /usr/bin/git-lfs ls-files
                           
                            # Show status
                            git status
                           
                            # Commit all changes
                            git commit -m "Add Terraform files and providers" || echo "No changes to commit"
                        '''
                    }
                }
            }
        }
 
        stage('Push to Repository') {
            steps {
                dir('terraform') {
                    script {
                        echo 'Pushing to repository...'
                        sh '''
                            # Configure Git
                            git config user.name "AnandJoy7"
                            git config user.email "k.anad548@gmail.com"
                           
                            # Setup new remote
                            git remote remove origin || true
                            git remote add origin https://${GITHUB_PAT}@github.com/AnandJoy7/V4.git
                           
                            # Show what will be pushed
                            echo "Files to be pushed:"
                            git status
                           
                            # Push LFS objects first
                            echo "Pushing LFS objects..."
                            GIT_TRACE=1 /usr/bin/git-lfs push --all origin main
                           
                            # Push everything to main
                            echo "Pushing to main branch..."
                            GIT_TRACE=1 git push -u origin main --force
                           
                            # Verify push
                            echo "Verifying remote contents..."
                            git ls-remote --heads origin main
                        '''
                    }
                }
            }
        }
    }
 
    post {
        always {
            echo 'Archiving Terraform output log...'
            dir('terraform') {
                archiveArtifacts artifacts: 'terraform_output.log', allowEmptyArchive: true
            }
        }
        success {
            echo 'Pipeline completed successfully and changes pushed to new repository with Git LFS support.'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}

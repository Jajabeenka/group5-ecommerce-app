pipeline {
    agent any

    environment {
        REGISTRY        = 'jessimey'
        APP_NAME        = 'group5-ecommerce-app'
        IMAGE           = "jessimey/group5-ecommerce-app"
        TAG             = "${env.GIT_COMMIT.take(7)}"
        
        // Target EC2 Details
        TARGET_EC2_IP   = '18.233.137.78'          // Target EC2 IP address
        TARGET_EC2_USER = 'ubuntu'            // SSH username (e.g., ubuntu / ec2-user)
        CONTAINER_PORT  = '5000'                // Internal Flask port
        HOST_PORT       = '80'                // Host port mapped on target EC2
        
        // Jenkins Credentials IDs
        DOCKER_HUB_CREDS = 'docker-hub-credentials'
        SSH_KEY_CREDS    = 'webserver-ecommerce-ssh'
    }

    stages {
        stage('Build & Unit Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt pytest
                    pytest
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest ."
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh "docker push ${IMAGE}:${TAG}"
                    sh "docker push ${IMAGE}:latest"
                }
            }
        }

        stage('Deploy to EC2 Host') {
            steps {
                sshagent([SSH_KEY_CREDS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${TARGET_EC2_USER}@${TARGET_EC2_IP} '
                            docker pull ${IMAGE}:${TAG}
                            docker stop ${APP_NAME} || true
                            docker rm ${APP_NAME} || true
                            docker run -d --name ${APP_NAME} --restart always -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE}:${TAG}
                            docker image prune -f
                        '
                    """
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh "curl --fail http://${TARGET_EC2_IP}:${HOST_PORT}/health || exit 1"
            }
        }
    }

    post {
        always {
            sh "docker rmi ${IMAGE}:${TAG} ${IMAGE}:latest || true"
        }
    }
}

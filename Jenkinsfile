pipeline {
    agent any

    environment {
        REGISTRY         = 'jessimey'
        APP_NAME         = 'group5-ecommerce-app'
        IMAGE            = 'jessimey/group5-ecommerce-app'
        TAG              = "${env.GIT_COMMIT.take(7)}"
        
        // Target EC2 Details
        TARGET_EC2_IP    = '18.233.137.78'
        TARGET_EC2_USER  = 'ubuntu'
        CONTAINER_PORT   = '5000'
        HOST_PORT        = '5001'
        
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
                    pytest || [ $? -eq 5 ]
                '''
            }
        }

        stage('Docker Build') {
            steps {
                 sh "DOCKER_BUILDKIT=0 docker build --no-cache -t ${IMAGE}:${TAG} -t ${IMAGE}:latest ."
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
                sshagent(["${SSH_KEY_CREDS}"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${TARGET_EC2_USER}@${TARGET_EC2_IP} "
                            docker pull ${IMAGE}:${TAG}
                            docker rm -f ${APP_NAME} 2>/dev/null || true
                            docker run -d --name ${APP_NAME} --restart always -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE}:${TAG}
                            docker image prune -f
                        "
                    """
                }
            }
        }

        // FIX 3: Smoke test runs over SSH on target host with retry loop + auto docker log output
        stage('Smoke Test') {
            steps {
                sshagent(["${SSH_KEY_CREDS}"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${TARGET_EC2_USER}@${TARGET_EC2_IP} "
                            for i in {1..10}; do
                                if curl -s --fail http://localhost:${HOST_PORT}/ > /dev/null; then
                                    echo 'Smoke Test Passed successfully on EC2!'
                                    exit 0
                                fi
                                echo 'App not ready yet, retrying in 3 seconds...'
                                sleep 3
                            done
                            echo 'Smoke test failed after 10 attempts. Container Logs:'
                            docker logs ${APP_NAME}
                            exit 1
                        "
                    """
                }
            }
        }
    }

    post {
        always {
            sh "docker rmi ${IMAGE}:${TAG} ${IMAGE}:latest || true"
        }
    }
}

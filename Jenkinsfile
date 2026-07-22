pipeline {

    agent any

    environment {
        AZ_ACCOUNT = 'group5storage2026'
        AZ_SHARE   = 'webcontent'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy to ACI (file share)') {
            steps {

                withCredentials([
                    string(credentialsId: 'group5-storage-key', variable: 'AZ_KEY')
                ]) {

                    sh '''
                    az storage file upload-batch \
                        --account-name "$AZ_ACCOUNT" \
                        --account-key "$AZ_KEY" \
                        --destination "$AZ_SHARE" \
                        --source "./templates" \
                        --pattern "*.html" \
                        --no-progress
                    '''

                }

            }
        }

    }

}

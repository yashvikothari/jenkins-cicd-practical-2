pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'RUN_ROLLBACK_DEMO',
            defaultValue: false,
            description: 'Deploy a deliberately broken image after the healthy release, then roll back.'
        )
    }

    environment {
        APP_NAME = 'jenkins-cicd-demo'
        SERVICE_NAME = 'jenkins-cicd-demo'
        DOCKERHUB_REPO = 'yashvikothari/jenkins-cicd-demo'
        IMAGE_TAG = "${BUILD_NUMBER}"
        REPLICAS = '3'
        PUBLISHED_PORT = '8090'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m compileall -q src
                    echo "Build validation passed."
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    APP_VERSION="build-${BUILD_NUMBER}" \
                    python3 -m unittest discover -s tests -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      --build-arg APP_VERSION="build-${BUILD_NUMBER}" \
                      -t "$DOCKERHUB_REPO:$IMAGE_TAG" \
                      -t "$DOCKERHUB_REPO:latest" .
                '''

                script {
                    if (params.RUN_ROLLBACK_DEMO) {
                        sh '''
                            docker build \
                              -f Dockerfile.bad \
                              --build-arg APP_VERSION="broken-${BUILD_NUMBER}" \
                              -t "$DOCKERHUB_REPO:${IMAGE_TAG}-bad" .
                        '''
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker push "$DOCKERHUB_REPO:$IMAGE_TAG"
                        docker push "$DOCKERHUB_REPO:latest"
                    '''

                    script {
                        if (params.RUN_ROLLBACK_DEMO) {
                            sh '''
                                set +x
                                docker push "$DOCKERHUB_REPO:${IMAGE_TAG}-bad"
                            '''
                        }
                    }

                    sh '''
                        set +x
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy / Rolling Update') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -e

                        SWARM_STATE="$(docker info --format '{{.Swarm.LocalNodeState}}')"
                        if [ "$SWARM_STATE" != "active" ]; then
                          echo "Docker Swarm is not active. Run: docker swarm init"
                          exit 1
                        fi

                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin

                        if docker service inspect "$SERVICE_NAME" >/dev/null 2>&1; then
                          echo "Rolling update to $DOCKERHUB_REPO:$IMAGE_TAG"
                          docker service update \
                            --image "$DOCKERHUB_REPO:$IMAGE_TAG" \
                            --with-registry-auth \
                            --update-parallelism 1 \
                            --update-delay 8s \
                            --update-monitor 12s \
                            --update-failure-action pause \
                            --rollback-parallelism 1 \
                            --rollback-delay 4s \
                            --detach=true \
                            "$SERVICE_NAME"
                        else
                          echo "Creating first 3-replica deployment."
                          docker service create \
                            --name "$SERVICE_NAME" \
                            --replicas "$REPLICAS" \
                            --publish "published=${PUBLISHED_PORT},target=8080" \
                            --with-registry-auth \
                            --update-parallelism 1 \
                            --update-delay 8s \
                            --update-monitor 12s \
                            --update-failure-action pause \
                            --rollback-parallelism 1 \
                            --rollback-delay 4s \
                            "$DOCKERHUB_REPO:$IMAGE_TAG"
                        fi

                        docker logout
                        bash ./scripts/wait-for-service.sh "$SERVICE_NAME" 180 "$REPLICAS"
                        docker service ps "$SERVICE_NAME" --no-trunc
                    '''
                }
            }
        }

        stage('Verify New Version') {
            steps {
                sh '''
                    bash ./scripts/verify-app.sh "http://127.0.0.1:${PUBLISHED_PORT}/health" 90
                    docker service inspect "$SERVICE_NAME" \
                      --format 'Current image: {{.Spec.TaskTemplate.ContainerSpec.Image}}'
                    docker service ls --filter "name=$SERVICE_NAME"
                '''
            }
        }

        stage('Controlled Deployment Issue') {
            when {
                expression { return params.RUN_ROLLBACK_DEMO }
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set -e
                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin

                        docker service update \
                          --image "$DOCKERHUB_REPO:${IMAGE_TAG}-bad" \
                          --with-registry-auth \
                          --update-parallelism 1 \
                          --update-delay 5s \
                          --update-monitor 10s \
                          --update-max-failure-ratio 0 \
                          --update-failure-action pause \
                          --detach=true \
                          "$SERVICE_NAME"

                        docker logout

                        bash ./scripts/wait-for-paused-update.sh "$SERVICE_NAME" 60

                        echo "CONTROLLED FAILURE CAPTURED"
                        docker service inspect "$SERVICE_NAME" \
                          --format 'Update state: {{.UpdateStatus.State}} | {{.UpdateStatus.Message}}'
                        docker service ps "$SERVICE_NAME" --no-trunc || true
                    '''
                }
            }
        }

        stage('Rollback') {
            when {
                expression { return params.RUN_ROLLBACK_DEMO }
            }
            steps {
                sh '''
                    echo "Rolling back to previous working service configuration..."
                    docker service update --rollback --detach=true "$SERVICE_NAME"

                    bash ./scripts/wait-for-service.sh "$SERVICE_NAME" 180 "$REPLICAS"
                    ./scripts/verify-app.sh "http://127.0.0.1:${PUBLISHED_PORT}/health" 90

                    echo "ROLLBACK SUCCESSFUL"
                    docker service inspect "$SERVICE_NAME" \
                      --format 'Recovered image: {{.Spec.TaskTemplate.ContainerSpec.Image}}'
                    docker service ls --filter "name=$SERVICE_NAME"
                    docker service ps "$SERVICE_NAME" --no-trunc
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the failed stage and service state.'
            sh 'docker service ps "$SERVICE_NAME" --no-trunc || true'
        }
    }
}

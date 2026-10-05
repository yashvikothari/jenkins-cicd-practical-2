# Jenkins Rolling Deployment and Rollback Lab

Flow:

**GitHub → Jenkins → Build → Test → Docker → Deploy → Verify → Rollback**

This project extends the previous Jenkins/Docker practical. It uses Docker Swarm for a true rolling deployment while keeping the setup simple enough for a local Jenkins lab.

## One-time setup

Required on the Jenkins machine:

- Jenkins
- Git
- Python 3
- Docker Engine / Docker CLI
- curl
- Jenkins Pipeline, Git, and Credentials Binding plugins

Initialize Swarm once:

```bash
docker swarm init
docker node ls
```

A single-node swarm is enough for this practical.

## Jenkins Docker Hub credential

Create:

**Manage Jenkins → Credentials → System → Global credentials → Add Credentials**

Use:

- Kind: Username with password
- Username: Docker Hub username
- Password: Docker Hub access token
- ID: `dockerhub-credentials`

Replace in `Jenkinsfile`:

```groovy
DOCKERHUB_REPO = 'YOUR_DOCKERHUB_USERNAME/jenkins-cicd-demo'
```

## Connect GitHub

Create a Jenkins **Pipeline** job:

- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: your GitHub repository
- Branch: `*/main`
- Script Path: `Jenkinsfile`

If Jenkins is internet-reachable, optionally configure:

```text
https://YOUR_JENKINS_HOST/github-webhook/
```

## Normal deployment run

Run with:

```text
RUN_ROLLBACK_DEMO = false
```

The pipeline builds and tests the app, creates/pushes the Docker image, then creates or rolling-updates a 3-replica Docker Swarm service.

Open the deployed application:

```text
http://YOUR_JENKINS_HOST:8090/
```

The app visibly shows the Jenkins build version.

## Rollback demonstration

Run **Build with Parameters**:

```text
RUN_ROLLBACK_DEMO = true
```

After the healthy deployment, Jenkins pushes and deploys a deliberately broken image. Swarm updates only one replica at a time and pauses when that task fails. Jenkins then runs:

```bash
docker service update --rollback jenkins-cicd-demo
```

and verifies the restored healthy version.

## Useful evidence commands

```bash
docker service ls
docker service ps jenkins-cicd-demo
docker service inspect jenkins-cicd-demo --pretty
curl http://127.0.0.1:8090/health
```

## Cleanup

```bash
docker service rm jenkins-cicd-demo
docker swarm leave --force
```

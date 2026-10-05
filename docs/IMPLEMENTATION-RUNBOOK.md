# Complete Deployment Flow

## GitHub → Jenkins

Application code, tests, Dockerfiles, scripts, and the Jenkinsfile are committed to GitHub. Jenkins uses **Pipeline script from SCM** to retrieve the repository.

## Build

Jenkins validates Python source code:

```bash
python3 -m compileall -q src
```

## Test

Jenkins runs four automated unit tests:

```bash
python3 -m unittest discover -s tests -v
```

## Docker

The pipeline builds:

```text
username/jenkins-cicd-demo:<build-number>
username/jenkins-cicd-demo:latest
```

The build number is embedded into `APP_VERSION`, making the deployed version visible in the browser.

## Deploy / Rolling Update

Docker Swarm runs 3 replicas. Updates use:

```text
--update-parallelism 1
```

so only one replica is replaced at a time. Existing healthy replicas remain available during the rollout.

## Verify

Jenkins calls:

```text
http://127.0.0.1:8090/health
```

and prints the running service image and replica state.

## Controlled Deployment Issue

With `RUN_ROLLBACK_DEMO=true`, Jenkins builds a second image from `Dockerfile.bad`. Its container intentionally exits.

Jenkins attempts to deploy it with:

```text
--update-parallelism 1
--update-max-failure-ratio 0
--update-failure-action pause
```

The first failed task causes the rolling update to pause, preserving the remaining healthy replicas.

## Rollback

Jenkins runs:

```bash
docker service update --rollback jenkins-cicd-demo
```

Swarm restores the immediately previous working service configuration. Jenkins waits for all 3 replicas and verifies `/health` again.

## Screenshot order

1. **CI/CD Pipeline Screenshot** — Jenkins stage view with all stages.
2. **Deployment Screenshot** — `docker service ps jenkins-cicd-demo` showing 3 running replicas.
3. **Docker Image Screenshot** — Docker Hub tags showing `latest`, build number, and optional `<build>-bad`.
4. **Successful Application Screenshot** — browser at `http://YOUR_HOST:8090/`.
5. **Rollback Screenshot** — Jenkins/console showing `ROLLBACK SUCCESSFUL`, recovered image, and 3/3 replicas.
6. **Pipeline Architecture Diagram** — open `docs/pipeline-architecture.html` and capture it.

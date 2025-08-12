# Better — DevOps Assessment Demo

This repo is designed to exactly match the Better assessment request: a small Flask app with a real CI/CD pipeline using GitHub Actions, Docker, and an example deploy to a server or Kubernetes.

## Quick start (local)

1. Create and activate a python venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open http://localhost:5000 and click the Get Status button.

Build locally with Docker
```bash
docker build -t better-demo:local .
docker run -p 5000:5000 better-demo:local
```

## Deploy path A — GitHub Actions → Docker Hub → Remote server
1. Create a Docker Hub repo named better-demo or use YOUR_DOCKERHUB_USERNAME/better-demo.
2. Add the following GitHub secrets to your repo:
   - DOCKERHUB_USERNAME — your Docker Hub username
   - DOCKERHUB_TOKEN — Docker Hub access token (or password)
   - DEPLOY_USER — username on remote server (e.g., ubuntu)
   - DEPLOY_SERVER — server IP or hostname
   - SSH_PRIVATE_KEY — private key with access to remote server
   - SSH_KNOWN_HOSTS — (optional) known hosts entry to avoid prompts
   - DATADOG_API_KEY — (optional) Datadog API key
3. Ensure deploy/remote-deploy.sh is present on the remote server and executable (or change the Actions step to run the docker commands directly over SSH).
4. Push to main branch. The Actions workflow will build, push, then SSH to the server and run the deploy script.

## Deploy path B — Kubernetes
To deploy to a Kubernetes cluster (e.g., Minikube, DigitalOcean Kubernetes, or EKS):
1. Push image to Docker Hub (Actions already does this) OR docker push YOUR_DOCKERHUB_USERNAME/better-demo:latest.
2. Update k8s/deployment.yaml image field to YOUR_DOCKERHUB_USERNAME/better-demo:latest.
3. Apply manifests:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
If using Minikube, expose service via minikube service better-demo-service.

## Monitoring
This repo includes a minimal Datadog event POST example. To actually see events in Datadog set DATADOG_API_KEY in GitHub secrets (or as an env on your server) and ensure outbound requests to the Datadog API are allowed.

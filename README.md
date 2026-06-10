# Student CRUD REST API

A Flask REST API for managing student records, with support for local development, Docker, bare metal, Kubernetes, Helm, and GitOps deployments via ArgoCD. Secrets are managed via HashiCorp Vault and External Secrets Operator.

## Features

- CRUD operations for students
- Versioned API under `/api/v1`
- Healthcheck endpoint
- Database migrations with Flask-Migrate
- PostgreSQL via Docker Compose or Kubernetes
- Unit tests with pytest
- Dockerfile and Docker Compose support
- Helm chart for Kubernetes deployment (local and remote)
- Secret management via HashiCorp Vault + ESO
- GitOps deployments via ArgoCD
- CI/CD pipeline via GitHub Actions with self-hosted runner

## Tech Stack

- Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate
- PostgreSQL / SQLite
- Docker, Docker Compose
- Kubernetes, Helm
- HashiCorp Vault, External Secrets Operator
- ArgoCD, GitHub Actions

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/healthcheck` | Healthcheck |
| POST | `/api/v1/students` | Create a student |
| GET | `/api/v1/students` | Get all students |
| GET | `/api/v1/students/<id>` | Get a student by ID |
| PUT | `/api/v1/students/<id>` | Update a student |
| DELETE | `/api/v1/students/<id>` | Delete a student |

## Project Structure

```txt
student-crud-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   │   └── student.py
│   ├── routes/
│   │   └── student_routes.py
│   └── utils/
│       └── logger.py
├── migrations/
│   └── versions/
│       └── c1945a5d6d80_initial_migration.py
├── Kubernetes/
│   ├── application/
│   │   └── application.yml
│   ├── database/
│   │   └── database.yml
│   ├── external-secrets/
│   │   ├── secret-store.yml
│   │   └── external-secret.yml
│   ├── namespace/
│   │   └── namespace.yml
│   ├── argocd/
│   │   ├── values.yaml          # nodeSelector for dependent_services node
│   │   ├── application.yaml     # ArgoCD Application manifest
│   │   └── repository-secret.yaml
│   └── helm/
│       └── student-api/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│               ├── namespace.yaml
│               ├── configmap.yaml
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── secret-store.yaml
│               └── external-secret.yaml
├── docs/                        # Helm chart repository (served via GitHub Pages)
│   ├── index.yaml
│   └── student-api-0.1.0.tgz
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── tests/
├── Dockerfile
├── Makefile
├── docker-compose.yaml
├── entrypoint.sh
├── requirements.txt
└── run.py
```

---

# Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/JayanthNaiduKundrapu/student-crud-api.git
cd student-crud-api
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
make install
```

### 4. Configure local environment

```bash
cp .env.example .env
# edit .env:
# DATABASE_URL=sqlite:///students.db
# DEBUG=True
```

### 5. Run migrations and start

```bash
export FLASK_APP=run.py
make init-db
make migrate
make upgrade
make run
```

Open at `http://127.0.0.1:5000`.

### Makefile commands

| Command | Description |
|---|---|
| `make run` | Run Flask locally |
| `make test` | Run unit tests |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |

---

# Docker Setup

### Run with Docker Compose (recommended)

Starts Flask + PostgreSQL together:

```bash
docker compose up --build
```

API available at `http://127.0.0.1:5000`.

### Run with Dockerfile only

Only use this if PostgreSQL is already running and reachable:

```bash
docker run --rm -p 5000:5000 \
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/students_db \
  student-api:v1.0.0
```

### Testing

```bash
make test
```

---

# Bare Metal Deployment

Run `vagrant up` — it automatically provisions the full stack.

```txt
Client / Postman
      ↓
localhost:8080
      ↓
NGINX
   ↙      ↘
API 1    API 2
    \    /
   PostgreSQL
```

Test at `http://localhost:8080/healthcheck`.

> **Debug tip:** verify container connectivity using Python:
> ```python
> import socket
> socket.gethostbyname("db")
> ```

---

# Kubernetes Deployment (Raw Manifests)

## Cluster Setup

```bash
# start a 4-node cluster
minikube start --nodes 4 --driver=docker
kubectl get nodes

# label worker nodes
kubectl label node minikube-m02 type=application
kubectl label node minikube-m03 type=database
kubectl label node minikube-m04 type=dependent_services

# verify
kubectl get nodes --show-labels
```

## Prerequisites — Install Vault and ESO

### Install Vault (dev mode)

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

helm install vault hashicorp/vault \
  -n vault \
  --create-namespace \
  --set "server.dev.enabled=true"

kubectl get pods -n vault
# vault-0 should be Running
```

### Write secrets into Vault

```bash
# exec into the vault pod
kubectl exec -it vault-0 -n vault -- sh

# VAULT_ADDR and VAULT_TOKEN are already set in dev mode
vault kv put secret/student-api POSTGRES_PASSWORD=postgres
vault kv get secret/student-api
exit
```

> **Note:** Vault dev mode does not persist secrets across pod restarts. Re-run `vault kv put` after every restart.

### Install ESO

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace \
  --wait

kubectl get pods -n external-secrets
```

## Deploy with Raw Manifests

```bash
cd Kubernetes

kubectl apply -f namespace/namespace.yml

# create vault-token secret (always manual — never commit this)
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

kubectl apply -f external-secrets/secret-store.yml
kubectl apply -f external-secrets/external-secret.yml
kubectl apply -f database/database.yml
kubectl apply -f application/application.yml
```

### Verify

```bash
kubectl get pods -n student-api
kubectl get secretstore -n student-api       # should be: Valid
kubectl get externalsecret -n student-api    # should be: SecretSynced
kubectl get secrets -n student-api
```

### Access the API

```bash
kubectl port-forward svc/student-api-service 8080:80 -n student-api
# test at http://localhost:8080/healthcheck
```

### Debug

```bash
kubectl describe pod <pod-name> -n student-api
kubectl exec -it <pod-name> -n student-api -- sh
env | grep POSTGRES
```

---

# Kubernetes Deployment (Helm)

Helm packages all K8s resources into a single chart. One command replaces all the `kubectl apply` steps.

## Helm Chart Structure

```txt
helm/student-api/
├── Chart.yaml        # chart metadata
├── values.yaml       # all configurable values
└── templates/        # templated K8s manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── deployment.yaml  # includes init container for migrations
    ├── service.yaml
    ├── secret-store.yaml
    └── external-secret.yaml
```

## Option A — Install from Local Chart

### Prerequisites

```bash
# 1. install vault
helm install vault hashicorp/vault \
  -n vault --create-namespace \
  --set "server.dev.enabled=true"

# 2. write secret into vault
kubectl exec -it vault-0 -n vault -- sh
vault kv put secret/student-api POSTGRES_PASSWORD=postgres
exit

# 3. install ESO
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace --wait
```

### Install

```bash
cd Kubernetes

# dry run first
helm lint helm/student-api
helm template student-api helm/student-api

# install
helm install student-api helm/student-api
```

## Option B — Install from Remote Chart Repository

The chart is published at:
```
https://jayanthnaidukundrapu.github.io/student-crud-api/
```

```bash
helm repo add student-api https://jayanthnaidukundrapu.github.io/student-crud-api/
helm repo update
helm search repo student-api
helm install student-api student-api/student-api
```

## After Install (both options)

```bash
# create vault-token secret (always manual — never commit this)
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

# force ESO to sync immediately
kubectl annotate externalsecret student-api-secret \
  force-sync=$(date +%s) \
  --overwrite -n student-api
```

### Verify

```bash
kubectl get pods -n student-api -w
kubectl get secretstore -n student-api       # should be: Valid
kubectl get externalsecret -n student-api    # should be: SecretSynced
kubectl get secrets -n student-api
```

### Access the API

```bash
kubectl port-forward svc/student-api-service 8080:80 -n student-api
# test at http://localhost:8080/healthcheck
```

### Upgrade after changes

```bash
# NOTE: when ArgoCD is running, never run helm upgrade manually
# push to git and let ArgoCD handle it

# only use this when ArgoCD is NOT installed
helm upgrade student-api helm/student-api
```

### Uninstall

```bash
helm uninstall student-api
```

## Publishing a New Chart Version

```bash
# 1. bump version in Chart.yaml
# 2. package
helm package Kubernetes/helm/student-api

# 3. move to docs/
mv student-api-0.2.0.tgz docs/

# 4. regenerate index
helm repo index docs/ --url https://jayanthnaidukundrapu.github.io/student-crud-api/

# 5. push
git add docs/
git commit -m "helm chart release 0.2.0"
git push origin master
```

---

# GitOps Deployment (ArgoCD)

ArgoCD watches the git repository and automatically syncs the cluster whenever `values.yaml` or helm templates change. No manual `helm upgrade` needed after initial setup.

## How it works

```txt
Code merged to master
        │
        ▼
GitHub Actions CI/CD pipeline
  ├── lint and test (on PR only)
  └── on merge:
      ├── build Docker image (tag: sha-<git-sha>)
      ├── push to Docker Hub
      └── update Kubernetes/helm/student-api/values.yaml
              │
              ▼
        ArgoCD detects values.yaml changed
              │
              ▼
        helm upgrade runs automatically
              │
              ▼
        new pods roll out with new image
```

## ArgoCD Setup

ArgoCD runs in the `argocd` namespace on the `dependent_services` node (`minikube-m04`).

### Install ArgoCD via Helm

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

kubectl create namespace argocd

helm install argocd argo/argo-cd \
  -n argocd \
  -f Kubernetes/argocd/values.yaml
```

`Kubernetes/argocd/values.yaml` pins all ArgoCD components to `minikube-m04`:

```yaml
global:
  nodeSelector:
    type: dependent_services
```

Verify all pods are on `minikube-m04`:

```bash
kubectl get pods -n argocd -o wide
# NODE column should show minikube-m04 for all pods
```

### Access ArgoCD UI

```bash
# port-forward in a separate terminal
kubectl port-forward svc/argocd-server 8090:443 -n argocd

# get admin password
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```

Open `https://localhost:8090` — username: `admin`, password from above.

### Apply ArgoCD manifests (declarative)

All ArgoCD resources are committed to git and applied declaratively:

```bash
kubectl apply -f Kubernetes/argocd/repository-secret.yaml
kubectl apply -f Kubernetes/argocd/application.yaml
```

`repository-secret.yaml` — gives ArgoCD access to the GitHub repo.

`application.yaml` — tells ArgoCD what to deploy:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: student-api
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/JayanthNaiduKundrapu/student-crud-api
    targetRevision: master
    path: Kubernetes/helm/student-api
  destination:
    server: https://kubernetes.default.svc
    namespace: student-api
  syncPolicy:
    automated:
      prune: true       # removes resources deleted from git
      selfHeal: true    # reverts manual kubectl changes
    syncOptions:
      - CreateNamespace=true
```

Verify ArgoCD picked it up:

```bash
kubectl get application -n argocd
# SYNC STATUS should be: Synced
# HEALTH STATUS should be: Healthy
```

### After ArgoCD is running

Still manual (always):

```bash
# vault secret (re-run after every vault pod restart)
kubectl exec -it vault-0 -n vault -- sh
vault kv put secret/student-api POSTGRES_PASSWORD=postgres
exit

# vault-token
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

# force ESO sync
kubectl annotate externalsecret student-api-secret \
  force-sync=$(date +%s) \
  --overwrite -n student-api
```

---

# CI/CD Pipeline (GitHub Actions)

## Flow

```txt
PR opened         →  lint-and-test only
PR merged to master →  lint-and-test → build-push-deploy
                                              │
                                              ├── docker build + push (sha tag)
                                              ├── update values.yaml image tag
                                              └── git commit + push
                                                        │
                                                        ▼
                                                  ArgoCD auto-deploys
```

## Pipeline setup

The pipeline runs on a self-hosted runner (your Mac). Set it up at:
```
GitHub repo → Settings → Actions → Runners → New self-hosted runner
```

### Required GitHub secrets and variables

| Name | Type | Value |
|---|---|---|
| `DOCKER_USERNAME` | Secret | Docker Hub username |
| `DOCKER_PASSWORD` | Secret | Docker Hub password |
| `GH_PAT` | Secret | GitHub Personal Access Token (repo scope) |
| `DOCKER_IMAGE_NAME` | Variable | `student-api` |
| `DATABASE_URL` | Variable | postgres URL for tests |

### Create GH_PAT

GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → `repo` scope.

Add as repo secret named `GH_PAT`.

## Workflow file `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - app/**
      - tests/**
      - migrations/**
      - '*.py'
      - 'Makefile'
      - 'entrypoint.sh'
      - 'requirements.txt'
      - 'Dockerfile'

  push:
    branches:
      - master
    paths:
      - app/**
      - migrations/**
      - '*.py'
      - 'Makefile'
      - 'entrypoint.sh'
      - 'requirements.txt'
      - 'Dockerfile'

jobs:
  lint-and-test:
    runs-on: self-hosted
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      - run: make lint
      - run: make docker-compose-up
      - name: Run tests
        env:
          DATABASE_URL: ${{ vars.DATABASE_URL }}
        run: make test

  build-push-deploy:
    runs-on: self-hosted
    if: |
      github.event_name == 'push' &&
      github.ref == 'refs/heads/master' &&
      github.actor != 'github-actions' &&
      !startsWith(github.event.head_commit.message, 'ci:')
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GH_PAT }}

      - name: Build and push
        run: |
          TAG=sha-$(git rev-parse --short HEAD)
          echo "TAG=$TAG" >> $GITHUB_ENV
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker build -t ${{ secrets.DOCKER_USERNAME }}/${{ vars.DOCKER_IMAGE_NAME }}:$TAG .
          docker push ${{ secrets.DOCKER_USERNAME }}/${{ vars.DOCKER_IMAGE_NAME }}:$TAG

      - name: Update values.yaml and push
        run: |
          sed -i '' '/^app:/,/^db:/ s/^\([[:space:]]*\)tag:.*/\1tag: "'"$TAG"'"/' Kubernetes/helm/student-api/values.yaml
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git add Kubernetes/helm/student-api/values.yaml
          git commit -m "ci: update image tag to $TAG"
          git push origin master
```

## Important notes

`github.actor != 'github-actions'` — prevents infinite loop when the bot commits `values.yaml` back to git.

`!startsWith(github.event.head_commit.message, 'ci:')` — extra safety net, skips pipeline for bot commits.

`sed -i ''` — macOS BSD sed syntax. On Linux use `sed -i` without the empty string.

Image tag uses git SHA (`sha-abc1234`) not a fixed tag — ArgoCD detects the change in `values.yaml` and redeploys.

---

# Secret Management — How It Works

Secrets are never hardcoded in any YAML file or committed to git.

```txt
HashiCorp Vault
  secret/student-api
    POSTGRES_PASSWORD = "..."
            │
            │  ESO pulls on refreshInterval
            ▼
     SecretStore          ← how ESO connects to Vault
            │
     ExternalSecret       ← what to pull and where to put it
            │
            │  ESO auto-creates
            ▼
     K8s Secret (student-api-secret)
            │
            ▼
     Postgres Pod + Flask Pod
```

### What is manual vs automated

| Step | How |
|---|---|
| Install Vault, ESO, ArgoCD | `helm install` (one time) |
| Write secret into Vault | Manual — `vault kv put` inside vault pod |
| Create `vault-token` K8s secret | Manual — `kubectl create secret` |
| SecretStore, ExternalSecret | Helm via ArgoCD (automated) |
| K8s Secret creation | ESO (automated) |
| Secret rotation | ESO re-syncs on `refreshInterval` |
| New image deployment | ArgoCD (automated after CI push) |

> **Production note:** replace static token auth with Kubernetes auth so no token needs to be stored anywhere.

---

# Troubleshooting

## Pods

| Symptom | What to check |
|---|---|
| `CreateContainerConfigError` | Secret missing — `kubectl get secrets -n student-api` |
| `CrashLoopBackOff` | Check logs — `kubectl logs <pod> -n student-api` |
| `Init:0/1` stuck | Init container waiting — `kubectl logs <pod> -n student-api -c migrate-db` |
| `students` table does not exist | Migrations not in image — check `ls migrations/versions/` |
| Pod on wrong node | Check nodeSelector in values.yaml and node labels |

## ESO / Vault

| Symptom | What to check |
|---|---|
| SecretStore `InvalidProvider` | Vault URL wrong — `kubectl get svc -n vault` |
| SecretStore `vault-token not found` | Create vault-token — `kubectl create secret generic vault-token ...` |
| ExternalSecret `SecretSyncedError` | Vault path missing — exec into vault pod and run `vault kv get secret/student-api` |
| ExternalSecret not re-syncing | Force sync — `kubectl annotate externalsecret student-api-secret force-sync=$(date +%s) --overwrite -n student-api` |
| `no matches for kind SecretStore` | ESO not installed or wrong API version — check `helm list -n external-secrets` |
| ESO v2.5+ `unknown field auth.token` | Use `tokenSecretRef` not `token` |
| ESO `apiVersion: v1beta1` error | Use `apiVersion: external-secrets.io/v1` for ESO v2.5+ |

## Helm

| Symptom | What to check |
|---|---|
| `helm install` 404 error | index.yaml has wrong URL — regenerate with correct GitHub Pages URL |
| `cannot reuse a name` | Already installed — `helm uninstall student-api` first |
| `CRD already exists` error | Leftover from previous install — `kubectl delete crd <name>` |
| YAML parse error line 20 | nodeSelector template syntax — use `{{- toYaml .Values.x.nodeSelector \| nindent 8 }}` |
| `conflict with argocd-controller` | Don't run `helm upgrade` manually when ArgoCD is installed — push to git instead |

## ArgoCD

| Symptom | What to check |
|---|---|
| App `OutOfSync` | ArgoCD detected drift — click Sync in UI or wait for auto-sync |
| App `Degraded` | Pods unhealthy — `kubectl get pods -n student-api` |
| ArgoCD not picking up changes | Check poll interval — default 3 mins, or push a webhook |
| Bot commits triggering pipeline loop | Check `github.actor` condition and commit message filter in workflow |
| `git push` rejected after bot commit | `git pull origin master --no-rebase` then push |

## CI/CD

| Symptom | What to check |
|---|---|
| Pipeline not triggering | Changed file not in `paths` filter |
| `sed` error on Mac | Use `sed -i ''` not `sed -i` |
| Pipeline loops infinitely | Bot actor name mismatch — check `git log --format="%an"` |
| `git push` rejected in pipeline | Remote has new commits — add `git pull` before push in workflow |


# Observability

```txt
1. Prometheus    ← scrapes metrics, stores them
2. Grafana       ← UI to visualize metrics
3. Node Exporter ← hardware metrics from nodes
4. Kube State Metrics ← K8s object metrics
5. Loki          ← log storage
6. Promtail      ← log collector
7. Postgres Exporter  ← DB metrics
8. Blackbox Exporter  ← endpoint uptime

```

## Prometheus

Prometheus
  │
  ├── scrapes → your Flask app (/metrics)
  ├── scrapes → postgres exporter (/metrics)
  ├── scrapes → node exporter (/metrics)
  └── scrapes → blackbox exporter (/metrics)

Stores all numbers with timestamps.
You query later: "what was CPU at 3pm?"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# see all configurable values
helm show values prometheus-community/prometheus | less






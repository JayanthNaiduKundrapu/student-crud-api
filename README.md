# Student CRUD REST API

A Flask REST API for managing student records, with support for local development, Docker, bare metal, Kubernetes, and Helm deployments. Secrets are managed via HashiCorp Vault and External Secrets Operator.

## Features

- CRUD operations for students
- Versioned API under `/api/v1`
- Healthcheck endpoint
- Database migrations with Flask-Migrate
- PostgreSQL via Docker Compose or Kubernetes
- Unit tests with pytest
- Dockerfile and Docker Compose support
- Helm chart for Kubernetes deployment
- Secret management via HashiCorp Vault + ESO

## Tech Stack

- Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate
- PostgreSQL / SQLite
- Docker, Docker Compose
- Kubernetes, Helm
- HashiCorp Vault, External Secrets Operator

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

# inside the pod — these env vars are already set in dev mode, do echo else configure
# VAULT_ADDR='http://127.0.0.1:8200'
# VAULT_TOKEN='root'

# write your secret
vault kv put secret/student-api POSTGRES_PASSWORD=postgres

# verify
vault kv get secret/student-api

# exit the pod
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
kubectl apply -f namespace/namespace.yml

# create vault-token secret (always manual)
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
# describe a pod
kubectl describe pod <pod-name> -n student-api

# exec into a pod
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
    ├── deployment.yaml
    ├── service.yaml
    ├── secret-store.yaml
    └── external-secret.yaml
```

## Prerequisites

Same as raw manifests — Vault and ESO must be running first:

```bash
# 1. install vault (if not already)
helm install vault hashicorp/vault \
  -n vault --create-namespace \
  --set "server.dev.enabled=true"

# 2. write secret into vault
kubectl exec -it vault-0 -n vault -- sh
# inside the pod run:
# export VAULT_ADDR='http://127.0.0.1:8200'
# export VAULT_TOKEN='root'
vault kv put secret/student-api POSTGRES_PASSWORD=postgres
# exit

# 3. install ESO (if not already)
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace --wait
```

## Deploy with Helm

```bash
cd Kubernetes

# dry run — verify templates without deploying
helm lint helm/student-api
helm template student-api helm/student-api

# install
helm install student-api helm/student-api

# create vault-token secret (always manual)
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

# force ESO to sync immediately (default refresh is 1m)
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
# after editing values.yaml or templates
helm upgrade student-api helm/student-api
```

### Uninstall

```bash
helm uninstall student-api
```

## Customising Values

All configurable values are in `helm/student-api/values.yaml`:

```yaml
app:
  image:
    tag: "v1.1.0"       # change image version
  replicas: 2           # scale the API

db:
  database: students_db

externalSecret:
  refreshInterval: "1m" # how often ESO re-syncs from Vault
```

---

# Secret Management — How It Works

Secrets are never hardcoded in any YAML file or committed to git. They live in Vault and are synced into the cluster automatically by ESO.

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
| Install Vault, ESO | `helm install` (one time) |
| Write secret into Vault | Manual — `vault kv put` |
| Create `vault-token` K8s secret | Manual — `kubectl create secret` |
| SecretStore, ExternalSecret | Helm (automated) |
| K8s Secret creation | ESO (automated) |
| Secret rotation | ESO re-syncs on `refreshInterval` |

> **Production note:** replace static token auth with Kubernetes auth so no token needs to be stored anywhere. See ESO docs for setup.

## Troubleshooting

| Symptom | What to check |
|---|---|
| SecretStore `InvalidProvider` | Vault URL wrong — `kubectl get svc -n vault` |
| ExternalSecret `SecretSyncedError` | Vault path missing — `vault kv get secret/student-api` |
| ExternalSecret not re-syncing | Force sync — `kubectl annotate externalsecret student-api-secret force-sync=$(date +%s) --overwrite -n student-api` |
| Pod `CrashLoopBackOff` | Secret not mounted — `kubectl describe pod <name> -n student-api` |
| `no matches for kind SecretStore` | ESO not installed — `kubectl get pods -n external-secrets` |
| `students` table does not exist | Postgres not ready when migrations ran — check pod logs |

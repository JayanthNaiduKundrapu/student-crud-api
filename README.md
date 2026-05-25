# Student CRUD REST API

A simple Flask service for creating, reading, updating, and deleting student records.

This repository supports local development, Docker deployment, database migrations, and unit tests.

## Features

- CRUD operations for students
- Versioned API under `/api/v1`
- Healthcheck endpoint
- Database migrations with Flask-Migrate
- Local SQLite support and PostgreSQL via Docker Compose
- Unit tests with pytest
- Dockerfile and Docker Compose support

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- PostgreSQL / SQLite
- Pytest
- Docker

## Local setup

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

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///students.db
DEBUG=True
```

### 5. Apply database migrations

```bash
export FLASK_APP=run.py
make init-db
make migrate
make upgrade
```

### 6. Run the app locally

```bash
make run
```

Open the app at `http://127.0.0.1:5000`.

## Docker setup

### Build the image

```bash
make docker-build
```

### Recommended: run with Docker Compose

This starts the Flask app and a PostgreSQL database together.

```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:5000`.

### Dockerfile-only run

If you need to run only the Flask container, make sure PostgreSQL is reachable from the container and that `DATABASE_URL` is set appropriately.

```bash
docker run --rm -p 5000:5000 \
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/students_db \
  student-api:v1.0.0
```

> Note: `docker run` alone does not start the PostgreSQL service. Use Docker Compose for a complete setup.

## Testing

```bash
make test
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/students` | Create a new student |
| GET | `/api/v1/students` | Get all students |
| GET | `/api/v1/students/<id>` | Get a student by ID |
| PUT | `/api/v1/students/<id>` | Update a student |
| DELETE | `/api/v1/students/<id>` | Delete a student |
| GET | `/healthcheck` | Healthcheck endpoint |

## Example request

Create a new student:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/students \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","age":20}'
```

## Makefile commands

| Command | Description |
|---|---|
| `make run` | Run Flask API locally |
| `make test` | Run unit tests |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |

## Project structure

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
├── postman/
│   └── Student CRUD API.postman_collection.json
├── tests/
│   ├── conftest.py
│   └── test_students.py
├── Dockerfile
├── Makefile
├── docker-compose.yaml
├── entrypoint.sh
├── requirements.txt
├── run.py
├── README.md
└── .env.example
```

## Notes

- Use `docker compose up --build` for the full PostgreSQL + Flask environment.
- Use SQLite locally for quick development with `DATABASE_URL=sqlite:///students.db`.
- Run `flask db upgrade` whenever the model schema changes.
- `docker run` is only appropriate when a PostgreSQL service is already available.
- While running the `Github CI workflow`, make sure to setup the necessary environment and secret variables to ensure stages are successful.

---

# Baremetal Deployment

- Run `Vagrant up` command, it will automatically start the application with the architecture described below
- Test it via Postman at `http://localhost:8080/healthcheck`

```txt
Client/Postman
      ↓
localhost:8080
      ↓
NGINX
   ↙      ↘
API 1    API 2
    \    /
   PostgreSQL
```

> **Debug tip:** to verify if one container can reach another, use `ping` or a Python shell:
> ```python
> import socket
> socket.gethostbyname("db")
> ```

---

# Kubernetes Deployment

## Cluster setup

Set up a local Kubernetes cluster using minikube and kubectl.

Create a 4-node cluster (1 control plane + 3 workers) using Docker as the driver:

```bash
minikube start --nodes 4 --driver=docker
kubectl get nodes
```

Inspect nodes to understand their configuration:

```bash
kubectl describe node <node-name>
```

Label the 3 worker nodes for workload scheduling:

```bash
kubectl label node minikube-m02 type=application
kubectl label node minikube-m03 type=database
kubectl label node minikube-m04 type=dependent_services
```

Verify labels:

```bash
kubectl get nodes --show-labels
```

## Folder structure

```txt
Kubernetes/
├── application/
│   └── application.yml
├── database/
│   └── database.yml
├── external-secrets/
│   └── secret-store.yml
│   └── external-secret.yml
├── namespace/
│   └── namespace.yml
```

## Deploy workloads

```bash
# 1. Create namespace
kubectl apply -f namespace/namespace.yml

# 2. Deploy database
kubectl apply -f database/database.yml

# 3. Deploy application
kubectl apply -f application/application.yml
```

### Verify database workload

```bash
kubectl get deployments -n student-api
kubectl get svc -n student-api
kubectl get cm -n student-api
kubectl get secrets -n student-api

# check which node the pod got scheduled on
kubectl get pods -n student-api -o wide

# describe a pod for details
kubectl describe <pod-name> -n student-api
```

### Debug inside a pod

```bash
kubectl exec -it <pod-name> -n student-api -- bash
env | grep POSTGRES
```

## Access the API locally

Since minikube uses Docker as a driver, the cluster is inside a Docker container and is not directly reachable from your laptop. Use port-forward:

```bash
kubectl port-forward svc/student-api-service 8080:80 -n student-api
```

Then hit the API via Postman or curl at `http://localhost:8080`.

---

# Secret Management with HashiCorp Vault and External Secrets Operator

Secrets (like `POSTGRES_PASSWORD`) are not hardcoded in any YAML file. They are stored in HashiCorp Vault and synced into the cluster automatically by the External Secrets Operator (ESO).

## How it works

```txt
HashiCorp Vault
  secret/student-api
    POSTGRES_PASSWORD = "..."
            │
            │  ESO pulls every 1m
            ▼
     SecretStore          ← how ESO connects to Vault
            │
     ExternalSecret       ← what ESO pulls from Vault
            │
            │  ESO auto-creates
            ▼
     K8s Secret (student-api-secret)
            │
            ▼
     Postgres Pod + Flask Pod
```

## Prerequisites

- Vault running in dev mode inside the cluster
- ESO v2.5.0 installed via Helm

## Step 1 — Install ESO

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace \
  --wait
```

Verify:

```bash
kubectl get pods -n external-secrets
# expect 3 pods: external-secrets, webhook, cert-controller

kubectl get crd | grep external-secrets
# expect: secretstores, externalsecrets, clustersecretstores
```

## Step 2 — Write secrets into Vault

```bash
# port-forward vault (leave running in a separate terminal)
kubectl port-forward svc/vault 8200:8200 -n vault

# in another terminal
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# write your secret
vault kv put secret/student-api POSTGRES_PASSWORD=yourpassword

# verify
vault kv get secret/student-api
```

## Step 3 — Create a K8s Secret holding the Vault token

ESO needs a Vault token to authenticate. Store it as a K8s Secret in the same namespace as your app:

```bash
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api
```

> In production, use Kubernetes auth instead of a static token. See the ESO docs for details.

## Step 4 — Apply the SecretStore

The SecretStore tells ESO how to connect to Vault.

```bash
kubectl apply -f external-secrets/secret-store.yml

# status should be: Valid
kubectl get secretstore vault-secret-store -n student-api
```

## Step 5 — Apply the ExternalSecret

The ExternalSecret tells ESO what to pull from Vault and what K8s Secret to create.

```bash
kubectl apply -f external-secrets/external-secret.yml

# status should be: SecretSynced
kubectl get externalsecret student-api-secret -n student-api

# verify the K8s secret was created
kubectl get secret student-api-secret -n student-api

# decode and confirm the value or exec into pod and try to print variable
kubectl get secret student-api-secret -n student-api \
  -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d
```

## Step 6 — Verify end to end

```bash
# all pods running?
kubectl get pods -n student-api

# healthcheck
kubectl port-forward svc/student-api-service 8080:80 -n student-api
curl http://localhost:8080/healthcheck
# expect: healthy
```

## Troubleshooting

| Symptom | Check |
|---|---|
| SecretStore status `InvalidProvider` | Vault URL is wrong — run `kubectl get svc -n vault` and verify |
| ExternalSecret status `SecretSyncedError` | Token is wrong or Vault path doesn't exist — run `vault kv get secret/student-api` |
| Pod `CrashLoopBackOff` | Secret not mounted — run `kubectl describe pod <name> -n student-api` |
| `no matches for kind SecretStore` | ESO not installed — run `kubectl get pods -n external-secrets` |
# Student CRUD REST API

A Flask REST API for managing student records, with support for local development, Docker, bare metal, Kubernetes, Helm, GitOps deployments via ArgoCD, and full observability via Prometheus, Loki, and Grafana.

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
- Observability via Prometheus, Grafana, Loki, Promtail

## Tech Stack

- Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate
- PostgreSQL / SQLite
- Docker, Docker Compose
- Kubernetes, Helm
- HashiCorp Vault, External Secrets Operator
- ArgoCD, GitHub Actions
- Prometheus, Grafana, Loki, Promtail

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
│   │   ├── values.yaml
│   │   ├── application.yaml
│   │   └── repository-secret.yaml
│   ├── helm/
│   │   └── student-api/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   │           ├── namespace.yaml
│   │           ├── configmap.yaml
│   │           ├── deployment.yaml
│   │           ├── service.yaml
│   │           ├── secret-store.yaml
│   │           └── external-secret.yaml
│   └── observability/
│       ├── prometheus-values.yaml
│       ├── grafana-values.yaml
│       ├── loki-values.yaml
│       ├── promtail-values.yaml
│       ├── postgres-exporter-values.yaml
│       ├── kube-state-metrics-values.yaml
│       └── blackbox-values.yaml
├── docs/
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

```bash
docker compose up --build
```

API available at `http://127.0.0.1:5000`.

### Run with Dockerfile only

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

---

# Kubernetes Deployment (Raw Manifests)

## Cluster Setup

```bash
minikube start --nodes 4 --driver=docker
kubectl get nodes

kubectl label node minikube-m02 type=application
kubectl label node minikube-m03 type=database
kubectl label node minikube-m04 type=dependent_services

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
```

### Write secrets into Vault

```bash
kubectl exec -it vault-0 -n vault -- sh
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
```

## Deploy

```bash
cd Kubernetes

kubectl apply -f namespace/namespace.yml

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
```

---

# Kubernetes Deployment (Helm)

## Option A — Local Chart

```bash
cd Kubernetes

helm lint helm/student-api
helm template student-api helm/student-api
helm install student-api helm/student-api
```

## Option B — Remote Chart Repository

```
https://jayanthnaidukundrapu.github.io/student-crud-api/
```

```bash
helm repo add student-api https://jayanthnaidukundrapu.github.io/student-crud-api/
helm repo update
helm install student-api student-api/student-api
```

## After Install

```bash
kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

kubectl annotate externalsecret student-api-secret \
  force-sync=$(date +%s) \
  --overwrite -n student-api
```

## Publishing a New Chart Version

```bash
# 1. bump version in Chart.yaml
helm package Kubernetes/helm/student-api
mv student-api-0.2.0.tgz docs/
helm repo index docs/ --url https://jayanthnaidukundrapu.github.io/student-crud-api/
git add docs/
git commit -m "helm chart release 0.2.0"
git push origin master
```

---

# GitOps Deployment (ArgoCD)

ArgoCD watches the git repo and automatically syncs the cluster when anything changes.

## How it works

```txt
Code merged to master
        │
        ▼
GitHub Actions builds image (sha-<git-sha>)
updates Kubernetes/helm/student-api/values.yaml
        │
        ▼
ArgoCD detects values.yaml changed
        │
        ▼
helm upgrade runs automatically
new pods roll out
```

## Install ArgoCD

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

kubectl create namespace argocd

helm install argocd argo/argo-cd \
  -n argocd \
  -f Kubernetes/argocd/values.yaml
```

`Kubernetes/argocd/values.yaml` pins all components to `minikube-m04`:

```yaml
global:
  nodeSelector:
    type: dependent_services
```

### Access ArgoCD UI

```bash
kubectl port-forward svc/argocd-server 8090:443 -n argocd

kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath='{.data.password}' | base64 -d
```

Open `https://localhost:8090` — username: `admin`.

### Apply declarative manifests

```bash
kubectl apply -f Kubernetes/argocd/repository-secret.yaml
kubectl apply -f Kubernetes/argocd/application.yaml
```

```bash
kubectl get application -n argocd
# SYNC STATUS: Synced
# HEALTH STATUS: Healthy
```

### Still manual after ArgoCD

```bash
# after every vault pod restart
kubectl exec -it vault-0 -n vault -- sh
vault kv put secret/student-api POSTGRES_PASSWORD=postgres
exit

kubectl create secret generic vault-token \
  --from-literal=VAULT_TOKEN=root \
  -n student-api

kubectl annotate externalsecret student-api-secret \
  force-sync=$(date +%s) \
  --overwrite -n student-api
```

---

# CI/CD Pipeline (GitHub Actions)

## Flow

```txt
PR opened         →  lint-and-test only
PR merged         →  build image → push → update values.yaml → ArgoCD deploys
```

## Required secrets and variables

| Name | Type | Value |
|---|---|---|
| `DOCKER_USERNAME` | Secret | Docker Hub username |
| `DOCKER_PASSWORD` | Secret | Docker Hub password |
| `GH_PAT` | Secret | GitHub PAT with repo scope |
| `DOCKER_IMAGE_NAME` | Variable | `student-api` |
| `DATABASE_URL` | Variable | postgres URL for tests |

## Key notes

`github.actor != 'github-actions'` — prevents pipeline loop when bot commits `values.yaml`.

`!startsWith(github.event.head_commit.message, 'ci:')` — extra safety net for bot commits.

`sed -i ''` — macOS BSD sed syntax. Linux uses `sed -i` without the empty string.

Image tag uses git SHA so ArgoCD always detects a real change.

---

# Observability Stack

All observability components run in the `observability` namespace on `minikube-m04` (dependent_services node), except node-exporter and Promtail which run on all nodes as DaemonSets.

## Architecture

```txt
Metrics flow:

Node Exporter ─────────────┐
Postgres Exporter ─────────┤
kube-state-metrics ────────┤──▶ Prometheus ──▶ Grafana
Blackbox Exporter ─────────┘

Logs flow:

Application Pods ──▶ Promtail ──▶ Loki ──▶ Grafana
```

## What each component does

| Component | Purpose |
|---|---|
| Prometheus | Scrapes and stores metrics from all targets every 15s |
| Grafana | UI — visualizes metrics and logs in dashboards |
| Loki | Stores and indexes application logs |
| Promtail | DaemonSet — collects logs from pods and ships to Loki |
| Node Exporter | DaemonSet — exposes CPU, memory, disk, network metrics per node |
| kube-state-metrics | Exposes K8s object metrics (pod status, deployments, replicas) |
| Postgres Exporter | Connects to postgres DB and exposes DB metrics to Prometheus |
| Blackbox Exporter | Probes HTTP endpoints and reports uptime and latency |

## Setup

### Add Helm repos

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl create namespace observability
```

### Install Prometheus

```bash
helm install prometheus prometheus-community/prometheus \
  -n observability \
  -f Kubernetes/observability/prometheus-values.yaml
```

Access:
```bash
kubectl port-forward svc/prometheus-server -n observability 9090:80
# open http://localhost:9090
# Status → Targets to see what's being scraped
```

### Install Grafana

```bash
helm install grafana grafana/grafana \
  -n observability \
  -f Kubernetes/observability/grafana-values.yaml
```

Access:
```bash
kubectl port-forward svc/grafana -n observability 3000:80
# open http://localhost:3000
# username: admin

kubectl get secret grafana \
  -n observability \
  -o jsonpath="{.data.admin-password}" | base64 -d
```

Grafana is pre-configured with Prometheus as a data source. Verify at Connections → Data Sources → Test.

### Install Loki

```bash
helm install loki grafana/loki \
  -n observability \
  -f Kubernetes/observability/loki-values.yaml
```

### Install Promtail

Promtail runs as a DaemonSet on all nodes. It is configured to collect logs only from the `student-api` namespace to reduce noise.

```bash
helm install promtail grafana/promtail \
  -n observability \
  -f Kubernetes/observability/promtail-values.yaml
```

Verify logs in Grafana → Explore → select Loki data source → run:
```
{namespace="student-api"}
```

### Install Postgres Exporter

Postgres does not expose Prometheus metrics natively. The exporter connects to the DB and exposes metrics on `:9187/metrics`.

```bash
helm install postgres-exporter \
  prometheus-community/prometheus-postgres-exporter \
  -n observability \
  -f Kubernetes/observability/postgres-exporter-values.yaml
```

Verify in Prometheus:
```
pg_up
```
Expected result: `1`

### Install kube-state-metrics

```bash
helm install kube-state-metrics \
  prometheus-community/kube-state-metrics \
  -n observability \
  -f Kubernetes/observability/kube-state-metrics-values.yaml
```

Verify in Prometheus:
```
kube_pod_info
```

### Install Blackbox Exporter

Probes the following endpoints every 15 seconds:
- Student API `/healthcheck`
- Vault
- ArgoCD

```bash
helm install blackbox-exporter \
  prometheus-community/prometheus-blackbox-exporter \
  -n observability \
  -f Kubernetes/observability/blackbox-values.yaml
```

Then upgrade Prometheus to add the blackbox scrape config:

```bash
helm upgrade prometheus prometheus-community/prometheus \
  -n observability \
  -f Kubernetes/observability/prometheus-values.yaml
```

Verify in Prometheus:
```
probe_success
probe_http_status_code
probe_duration_seconds
```

### Add Loki as Grafana data source

After Loki is running, add it in Grafana → Connections → Data Sources → Add:
- Type: Loki
- URL: `http://loki.observability.svc.cluster.local:3100`

## Useful Prometheus queries

| Query | What it shows |
|---|---|
| `pg_up` | Postgres is reachable (1=up, 0=down) |
| `kube_pod_info` | Info about all pods in the cluster |
| `probe_success` | Endpoint up/down (1=up, 0=down) |
| `probe_http_status_code` | HTTP status code for each probed endpoint |
| `probe_duration_seconds` | Response latency for each endpoint |
| `node_cpu_seconds_total` | CPU usage per node |
| `node_memory_MemAvailable_bytes` | Available memory per node |

## Notes

Promtail runs as a DaemonSet — no nodeSelector, runs on all nodes intentionally so it can collect logs from every node's `/var/log/pods/`.

Node Exporter also runs as a DaemonSet on all nodes — no nodeSelector — so you get hardware metrics from every node, not just m04.

ArgoCD uses a self-signed TLS certificate — Blackbox Exporter will report TLS verification failures for the ArgoCD HTTPS endpoint. This is expected behaviour, not a bug.

---

# Secret Management — How It Works

```txt
HashiCorp Vault
  secret/student-api
    POSTGRES_PASSWORD = "..."
            │
            │  ESO pulls on refreshInterval
            ▼
     SecretStore → ExternalSecret → K8s Secret → Pods
```

| Step | How |
|---|---|
| Install Vault, ESO, ArgoCD | `helm install` (one time) |
| Write secret into Vault | Manual — `vault kv put` inside vault pod |
| Create `vault-token` K8s secret | Manual — `kubectl create secret` |
| SecretStore, ExternalSecret | Helm via ArgoCD (automated) |
| K8s Secret creation | ESO (automated) |
| New image deployment | ArgoCD (automated after CI push) |

---

# Troubleshooting

## Pods

| Symptom | What to check |
|---|---|
| `CreateContainerConfigError` | Secret missing — `kubectl get secrets -n student-api` |
| `CrashLoopBackOff` | `kubectl logs <pod> -n student-api` |
| `Init:0/1` stuck | `kubectl logs <pod> -n student-api -c migrate-db` |
| `students` table does not exist | `ls migrations/versions/` — migration file missing from image |
| Pod on wrong node | Check nodeSelector in values.yaml and node labels |

## ESO / Vault

| Symptom | What to check |
|---|---|
| SecretStore `InvalidProvider` | Vault URL wrong — `kubectl get svc -n vault` |
| SecretStore `vault-token not found` | `kubectl create secret generic vault-token ...` |
| ExternalSecret `SecretSyncedError` | Vault path missing — exec into vault pod and run `vault kv get secret/student-api` |
| ExternalSecret not re-syncing | `kubectl annotate externalsecret student-api-secret force-sync=$(date +%s) --overwrite -n student-api` |
| ESO v2.5+ `unknown field auth.token` | Use `tokenSecretRef` not `token` |
| ESO `apiVersion: v1beta1` error | Use `apiVersion: external-secrets.io/v1` |

## Helm

| Symptom | What to check |
|---|---|
| `helm install` 404 error | index.yaml wrong URL — regenerate with correct GitHub Pages URL |
| `cannot reuse a name` | `helm uninstall student-api` first |
| `CRD already exists` | `kubectl delete crd <name>` |
| YAML parse error nodeSelector | Use `{{- toYaml .Values.x.nodeSelector \| nindent 8 }}` |
| `conflict with argocd-controller` | Never run `helm upgrade` manually when ArgoCD is installed |

## ArgoCD

| Symptom | What to check |
|---|---|
| App `OutOfSync` | Wait for auto-sync or click Sync in UI |
| App `Degraded` | `kubectl get pods -n student-api` |
| Bot commits triggering pipeline loop | Check `github.actor` and commit message filter |
| `git push` rejected after bot commit | `git pull origin master --no-rebase` then push |

## CI/CD

| Symptom | What to check |
|---|---|
| Pipeline not triggering | File not in `paths` filter |
| `sed` error on Mac | Use `sed -i ''` not `sed -i` |
| Pipeline loops | Bot actor name mismatch — check `git log --format="%an"` |

## Observability

| Symptom | What to check |
|---|---|
| Prometheus target down | Check service annotations `prometheus.io/scrape: "true"` |
| `pg_up` returns 0 | Postgres exporter can't reach DB — check host/port in values |
| No logs in Grafana | Check Promtail pods running — `kubectl get pods -n observability` |
| Loki data source error | Verify URL `http://loki.observability.svc.cluster.local:3100` |
| Blackbox TLS error for ArgoCD | Expected — ArgoCD uses self-signed cert |
| probe_success = 0 | Endpoint unreachable — check service name and namespace in blackbox config |
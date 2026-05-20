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
make docker install
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
- While running the `Github CI workflow`, make sure to setup the neccessary environment, secret variables to ensure stages are successful

# Baremetal Deployment

- Run `Vagrant up` command, it will automatically start the application with the architecture described below


- Test it via postman at http://localhost:8080/healthcheck
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
- (debug) to internally verify if one conatiner is able to reach db or other ; use ping / python shell -> import sockets -> sockets.gethostbyname("db")

# K8 Deployment 

- Setup local k8 cluster by installing `minikube` and `kubectl`
- Create a local minikube cluster with 3 worker nodes and one master control plane, using docker as a driver
```bash
minikube start --nodes 4 --driver=docker
kubectl get nodes
```
- Inspect the nodes for validating and understanding node configs : 
```bash
kubectl describe node < node-name >
```
- Assign labels to all the 3 worker nodes in teh cluster :
```bash
kubectl label node minikube-m02 type=application
kubectl label node minikube-m03 type=database
kubectl label node minikube-m04 type=dependent_services
```
- Verify the labels :
```bash
kubectl get nodes --show-labels
```

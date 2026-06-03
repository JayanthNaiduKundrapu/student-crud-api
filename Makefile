run:
	python3 run.py

test:
	pytest

init-db:
	flask db init

migrate:
	flask db migrate -m "migration"

upgrade:
	flask db upgrade

install:
	pip install -r requirements.txt

docker-build:
	docker build -t student-api:v1.0.0 .

docker-network:
	docker network create student-network

docker-connect-db:
	docker network connect student-network postgres-db

docker-run-db:
	docker run \
	--name postgres-db \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_DB=students_db \
	-p 5432:5432 \
	postgres:latest

docker-run-api:
	docker run \
	--name student-api \
	-p 5000:5000 \
	-e DATABASE_URL=postgresql://postgres:postgres@postgres-db:5432/students_db \
	student-api:v1.0.0

docker-stop-api:
	docker stop student-api

docker-stop-db:
	docker stop postgres-db

docker-compose-up:
	docker-compose up --build -d

docker-compose-logs:
	docker-compose logs

docker-compose-down:
	docker-compose down -v

lint:
	flake8 app tests


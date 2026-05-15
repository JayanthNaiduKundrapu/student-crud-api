run:
	python3 run.py

test:
	pytest

migrate:
	flask db migrate -m "migration"

upgrade:
	flask db upgrade

install:
	pip install -r requirements.txt

docker-build:
	docker build -t student-api:v1.0.0 .

docker-run:
	docker run \
	-d \
	-p 5000:5000 \
	-e DATABASE_URL=sqlite:///students.db \
	student-api:v1.0.0
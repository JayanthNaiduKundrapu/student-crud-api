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
#!/bin/sh

echo "Waiting for postgres..."
while ! python3 -c "import socket; s=socket.create_connection(('postgres-service', 5432), timeout=1)" 2>/dev/null; do
  sleep 1
done
echo "Postgres is ready!"

if [ ! -d migrations ]; then
  flask db init # initialize the migration environment
fi

flask db migrate -m "auto migration" # generate a new migration script based on the changes detected in the models
flask db upgrade # apply the migration to the database (create tables, alter tables, etc.)

python3 run.py # start the Flask application
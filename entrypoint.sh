#!/bin/sh

if [ ! -d migrations ]; then
  flask db init # initialize the migration environment
fi

flask db migrate -m "auto migration" # generate a new migration script based on the changes detected in the models
flask db upgrade # apply the migration to the database (create tables, alter tables, etc.)

python3 run.py # start the Flask application
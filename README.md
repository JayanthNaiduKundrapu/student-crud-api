# Student CRUD REST API

A REST API built using Flask and SQLAlchemy
to manage student records.

The project supports CRUD operations,
database migrations, API versioning,
logging, healthcheck endpoint,
environment-based configuration,
and unit tests.


## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Migrate
- SQLite
- Pytest
- Postman


## Setup Instructions

### Clone Repo
```txt
`git clone https://github.com/JayanthNaiduKundrapu/student-crud-api.git`
`cd student-crud-api`
```
### Create Virtual Environment

`python3 -m venv venv`

### Activate Virtual Env

`source venv/bin/activate`

### Install Dependencies

`pip install -r requirements.txt`

## Environment Variables

Create a `.env` file in the project root:

```txt
DATABASE_URL=sqlite:///students.db 
DEBUG=True```

### Database Migrations

```txt
export FLASK_APP=run.py
flask db upgrade```

### Run Application 

`make run`

### Run Tests

`make test`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/students` | Create a new student |
| GET | `/api/v1/students` | Get all students |
| GET | `/api/v1/students/<id>` | Get a student by ID |
| PUT | `/api/v1/students/<id>` | Update student information |
| DELETE | `/api/v1/students/<id>` | Delete a student |
| GET | `/healthcheck` | Healthcheck endpoint |


## Postman Collection

The exported Postman collection is available inside:

`postman/student-api.postman_collection.json`


## Application Structure

Creating the folder structure as below :

```txt
student-crud-api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   └── student.py
│   │
│   ├── routes/
│   │   └── student_routes.py
│   │
│   └── utils/
│       └── logger.py
│
├── migrations/
├── postman/
├── tests/
│   ├── conftest.py
│   └── test_students.py
│
├── .env.example
├── .gitignore
├── Makefile
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py 
```

## Misc 

route -> service -> DB


## typical post route :

HTTP Request
→ Flask Route
→ JSON Parsing
→ ORM Object
→ DB Session
→ Commit
→ Response Serialization

```txt
student-crud-api/
│
├── app/
│   ├── __init__.py     creates flask app, connects everything, initializes db,      register routes
│   ├── config.py       configs
│   ├── extensions.py   Stores reusable Flask tools/extensions across app
│   ├── models/         definition of database tables
│   │   └── student.py  student schema
│   ├── routes/         api endpoints handler
│   │   └── student_routes.py  recieve and return requests
│   └── services/    actual business logic 
│       └── student_service.py  create,validate,fetch,delete work logic
│
├── tests/   automated tests 
├── migrations/   tracks structure/schema changes in db (like git vcs for db)
│
├── .env    stores secret, env vars
├── .env.example   just a temnplate 
├── run.py      entry point of app, this file starts server
├── requirements.txt   dependencies
├── README.md     about
└── Makefile      command shortcut system    
```

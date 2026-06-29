# AI Agent

## Overview

The AI Agent is a separate FastAPI service that uses Google's Gemini LLM to understand natural language requests and execute tools against the Student CRUD API.

Current architecture:

```
User
   │
   ▼
FastAPI Agent
   │
   ▼
Gemini LLM
   │
   ▼
Tool Registry
   │
   ▼
Student API
   │
   ▼
PostgreSQL
```

---

# Project Structure

```
agent/
├── main.py
├── llm.py
├── otel.py
├── requirements.txt
├── test.py
└── tools
    ├── registry.py
    └── student_api.py
```

---

# Features

- Natural language interface
- Gemini powered reasoning
- Tool based architecture
- Student CRUD operations
- Easily extensible

Supported tools:

- get_students
- get_student
- create_student
- update_student
- delete_student

---

# Setup

## 1. Activate virtual environment

```bash
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Gemini API Key

```bash
export GEMINI_API_KEY=<YOUR_API_KEY>
```

## 4. Start Student API

Ensure the Student API is already running.

Example:

```
http://127.0.0.1:8080
```

## 5. Start Agent

```bash
cd agent

uvicorn main:app --reload --port 8001
```

---

# Testing

Healthcheck

```bash
curl http://127.0.0.1:8001/healthcheck
```

List Students

```bash
curl -X POST http://127.0.0.1:8001/chat \
-H "Content-Type: application/json" \
-d '{"message":"Show all students"}'
```

Create Student

```bash
curl -X POST http://127.0.0.1:8001/chat \
-H "Content-Type: application/json" \
-d '{"message":"Create a student named Bob with email bob@test.com and age 28"}'
```

Get Student

```bash
curl -X POST http://127.0.0.1:8001/chat \
-H "Content-Type: application/json" \
-d '{"message":"Get student 1"}'
```

Update Student

```bash
curl -X POST http://127.0.0.1:8001/chat \
-H "Content-Type: application/json" \
-d '{"message":"Update student 1 to name Alice, email alice@test.com and age 30"}'
```

Delete Student

```bash
curl -X POST http://127.0.0.1:8001/chat \
-H "Content-Type: application/json" \
-d '{"message":"Delete student 1"}'
```

---

# How it works

1. User sends a natural language request to `/chat`.
2. The request is sent to Gemini.
3. Gemini determines which tool should be executed.
4. Gemini returns structured JSON containing:
   - tool name
   - arguments
5. The Tool Registry maps the tool name to the corresponding Python function.
6. The Python function invokes the Student CRUD API.
7. The Student API performs the database operation.
8. The result is returned back to the user.

---


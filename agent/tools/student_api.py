import requests

BASE_URL = "http://127.0.0.1:8080"


def get_students():
    response = requests.get(f"{BASE_URL}/api/v1/students")
    response.raise_for_status()
    return response.json()


def get_student(student_id):
    response = requests.get(f"{BASE_URL}/api/v1/students/{student_id}")
    response.raise_for_status()
    return response.json()


def create_student(name, email, age):
    response = requests.post(
        f"{BASE_URL}/api/v1/students",
        json={
            "name": name,
            "email": email,
            "age": age,
        },
    )
    response.raise_for_status()
    return response.json()


def update_student(student_id, name, email, age):
    response = requests.put(
        f"{BASE_URL}/api/v1/students/{student_id}",
        json={
            "name": name,
            "email": email,
            "age": age,
        },
    )
    response.raise_for_status()
    return response.json()


def delete_student(student_id):
    response = requests.delete(
        f"{BASE_URL}/api/v1/students/{student_id}"
    )
    response.raise_for_status()
    return response.json()
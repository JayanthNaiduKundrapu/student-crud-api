def test_healthcheck(client):

    response = client.get("/healthcheck")
    assert response.status_code == 200

def test_create_student(client):

    response = client.post(
        "/api/v1/students",
        json={
            "name": "lewis hamilton",
            "email": "lh@test.com",
            "age": 45
        }
    )

    assert response.status_code == 201

def test_get_students(client):

    response = client.get("/api/v1/students")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert "email" in data[0]
    assert "age" in data[0]
    
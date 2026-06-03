def test_healthcheck(client):

    response = client.get("/healthcheck")
    assert response.status_code == 200


def test_create_student(client):

    response = client.post(
        "/api/v1/students",
        json={
            "name": "lewiis hamilton",
            "email": "hammertime44@test.com",
            "age": 45
        }
    )

    assert response.status_code == 201


def test_get_students(client):

    response = client.get("/api/v1/students")
    response = client.delete("/api/v1/students/1")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1
    assert "name" in response.json[0]
    assert "email" in response.json[0]
    assert "age" in response.json[0]

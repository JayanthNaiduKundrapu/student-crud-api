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

from fastapi import status
from fastapi.testclient import TestClient
from ..main import app
from ..routers import routes


client = TestClient(app)


def test_register_missing_data():
    response = client.post(routes.API_USER_REGISTER, json={})

    expected_errors = [
        {"type": "missing", "loc": ["body", "full_name"], "msg": "Field required", "input": {}},
        {"type": "missing", "loc": ["body", "email"], "msg": "Field required", "input": {}},
        {"type": "missing", "loc": ["body", "password"], "msg": "Field required", "input": {}},
        {"type": "missing", "loc": ["body", "confirm_password"], "msg": "Field required", "input": {}},
        {"type": "missing", "loc": ["body", "agreement"], "msg": "Field required", "input": {}},
    ]

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for expected_error in expected_errors:
        assert expected_error in response.json()["detail"]


def test_register_invalid_full_name():
    input_value = "a"
    response = client.post(routes.API_USER_REGISTER, json={"full_name": input_value})

    expected_error = {
        "type": "string_too_short",
        "loc": ["body", "full_name"],
        "msg": "String should have at least 5 characters",
        "input": input_value,
        "ctx": {"min_length": 5},
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]


def test_register_invalid_password_length():
    input_value = "a"
    response = client.post(routes.API_USER_REGISTER, json={"password": input_value})

    expected_error = {
        "type": "string_too_short",
        "loc": ["body", "password"],
        "msg": "String should have at least 5 characters",
        "input": input_value,
        "ctx": {"min_length": 5},
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]

    input_value = "this password is too long - it should be shorter"
    response = client.post(routes.API_USER_REGISTER, json={"password": input_value})

    expected_error = {
        "type": "string_too_long",
        "loc": ["body", "password"],
        "msg": "String should have at most 20 characters",
        "ctx": {"max_length": 20},
        "input": input_value,
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]


def test_register_passwords_does_not_match():
    input_json = {
        "full_name": "John Doe",
        "email": "example@test321.com",
        "password": "String1",
        "confirm_password": "Other_pass1",
        "agreement": True,
    }
    response = client.post(routes.API_USER_REGISTER, json=input_json)

    expected_error = {
        "type": "value_error",
        "loc": ["body"],
        "msg": "Value error, Passwords do not match",
        "input": input_json,
        "ctx": {"error": {}},
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]

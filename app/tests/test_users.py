from fastapi import status
from fastapi.testclient import TestClient
from ..main import app
from ..routers import routes
from ..schemas import user_schema


client = TestClient(app)


register_valid_input_json = {
    "full_name": "John Doe",
    "email": "example@test321.com",
    "password": "String1",
    "confirm_password": "String1",
    "agreement": True,
}


def test_register_missing_data():
    response = client.post(routes.API_USERS_REGISTER, json={})

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
    response = client.post(routes.API_USERS_REGISTER, json={"full_name": input_value})

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
    response = client.post(routes.API_USERS_REGISTER, json={"password": input_value})

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
    response = client.post(routes.API_USERS_REGISTER, json={"password": input_value})

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
    input_json = register_valid_input_json.copy()
    input_json["confirm_password"] = "Other_pass1"

    response = client.post(routes.API_USERS_REGISTER, json=input_json)

    expected_error = {
        "type": "value_error",
        "loc": ["body"],
        "msg": "Passwords do not match",
        "input": input_json,
        "ctx": {"error": {}},
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]


def test_password_strength():
    expected_error = {
        "type": "value_error",
        "loc": ["body", "password"],
        "msg": "Password must contain at least one uppercase letter",
        "input": "no_uppercase_letter1",
        "ctx": {"error": {}},
    }

    test_cases = [
        {"input": "no_uppercase_letter1", "error": "Password must contain at least one uppercase letter"},
        {"input": "NO_LOWERCASE_LETTER1", "error": "Password must contain at least one lowercase letter"},
        {"input": "No_digit", "error": "Password must contain at least one digit"},
    ]

    for test_case in test_cases:
        input_json = register_valid_input_json.copy()
        input_json["password"] = test_case["input"]
        input_json["confirm_password"] = test_case["input"]

        response = client.post(routes.API_USERS_REGISTER, json=input_json)

        expected_error["input"] = test_case["input"]
        expected_error["msg"] = test_case["error"]

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert expected_error in response.json()["detail"]


def test_agreement_required():
    input_json = register_valid_input_json.copy()
    input_json["agreement"] = False

    response = client.post(routes.API_USERS_REGISTER, json=input_json)

    expected_error = {
        "type": "value_error",
        "loc": ["body", "agreement"],
        "msg": "You must accept terms",
        "input": False,
        "ctx": {"error": {}},
    }
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.json()["detail"]


def test_registration_successful():
    response = client.post(routes.API_USERS_REGISTER, json=register_valid_input_json)

    expected_response = register_valid_input_json.copy()
    del expected_response["password"]
    del expected_response["confirm_password"]
    del expected_response["agreement"]
    expected_response["id"] = expected_response.get("email")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


def test_login_wrong_data():
    form_data = {
        "username": "invalid_email@email.com",
        "password": "invalid_password",
    }
    response = client.post(routes.API_TOKEN, data=form_data)
    expected_response = {
        "detail": "Incorrect username or password"
    }

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_response


def test_users_me_unauthorized():
    response = client.get(routes.API_USERS_ME)
    expected_response = {
      "detail": "Could not validate credentials"
    }

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_response


def test_login_successful():
    form_data = {
        "username": register_valid_input_json["email"],
        "password": register_valid_input_json["password"],
    }
    response = client.post(routes.API_TOKEN, data=form_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_users_me_successful():
    response = client.get(routes.API_USERS_ME)
    expected_response = register_valid_input_json.copy()
    expected_response["id"] = expected_response["email"]

    user_out = user_schema.UserOut(**expected_response)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_out.model_dump()

from uuid import UUID, uuid4

import pytest

from config.endpoints import AUTH_GUEST_SESSION


def unique_device_id(suffix="device"):
    return f"qa-automation-{suffix}-{uuid4()}"


def assert_validation_error(response):
    assert response.status_code == 400, (
        "POTENTIAL VALIDATION BUG: invalid guest deviceId must return HTTP 400, "
        f"but the API returned HTTP {response.status_code}."
    )
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["statusCode"] == 400
    assert response_data["error"] == "Bad Request"
    assert response_data["path"] == AUTH_GUEST_SESSION
    assert response_data["message"], "Validation error message must not be empty"


@pytest.mark.api
@pytest.mark.smoke
def test_create_guest_session(api_client):
    device_id = unique_device_id()

    response = api_client.post(
        AUTH_GUEST_SESSION,
        data={"deviceId": device_id},
    )

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["timestamp"]

    session = response_data["data"]
    UUID(session["id"])
    assert session["deviceId"] == device_id
    assert session["language"] is None
    assert session["browsedProgramId"] is None


@pytest.mark.api
def test_create_guest_session_is_idempotent(api_client):
    device_id = unique_device_id("idempotency")

    first_response = api_client.post(
        AUTH_GUEST_SESSION,
        data={"deviceId": device_id},
    )
    second_response = api_client.post(
        AUTH_GUEST_SESSION,
        data={"deviceId": device_id},
    )

    assert first_response.status_code == 200, first_response.text
    assert second_response.status_code == 200, second_response.text

    first_session = first_response.json()["data"]
    second_session = second_response.json()["data"]
    assert second_session["id"] == first_session["id"], (
        "DATA BUG: repeated guest-session request created a duplicate session "
        "for the same deviceId."
    )
    assert second_session["deviceId"] == device_id


@pytest.mark.api
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"deviceId": None},
        {"deviceId": ""},
        {"deviceId": "   "},
        {"deviceId": 123},
        {"deviceId": True},
        {"deviceId": []},
        {"deviceId": {}},
        {"deviceId": "x" * 256},
    ],
    ids=[
        "missing",
        "null",
        "empty",
        "whitespace",
        "integer",
        "boolean",
        "list",
        "object",
        "too-long",
    ],
)
def test_create_guest_session_rejects_invalid_device_id(api_client, payload):
    response = api_client.post(AUTH_GUEST_SESSION, data=payload)

    assert_validation_error(response)

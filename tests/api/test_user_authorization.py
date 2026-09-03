import pytest

from config.endpoints import (
    USER_ME,
    USER_ME_ACCOUNT,
    USER_ME_DEVICES,
    USER_ME_PREFERENCES,
)

PROTECTED_USER_ENDPOINTS = (
    USER_ME,
    USER_ME_ACCOUNT,
    USER_ME_DEVICES,
)


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Bearer ",
        "Bearer malformed-token",
        "Bearer abc.def.xyz",
    ],
    ids=["missing", "empty-bearer", "malformed", "malformed-jwt"],
)
def test_preferences_reject_invalid_authorization(api_client, authorization):
    api_client.access_token = None
    headers = {"Authorization": authorization} if authorization is not None else None

    response = api_client.get(USER_ME_PREFERENCES, headers=headers)

    assert response.status_code == 401, (
        "SECURITY BUG: /user/me/preferences must reject missing or invalid "
        f"authorization, but returned HTTP {response.status_code}."
    )
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["statusCode"] == 401
    assert response_data["error"] == "Unauthorized"
    assert response_data["path"] == USER_ME_PREFERENCES


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize("endpoint", PROTECTED_USER_ENDPOINTS)
@pytest.mark.parametrize(
    "authorization",
    [None, "Bearer malformed-token"],
    ids=["missing", "malformed"],
)
def test_user_endpoints_reject_unauthorized_requests(
    api_client,
    endpoint,
    authorization,
):
    api_client.access_token = None
    headers = {"Authorization": authorization} if authorization else None

    response = api_client.get(endpoint, headers=headers)

    assert response.status_code == 401, (
        f"SECURITY BUG: {endpoint} must reject unauthorized requests, "
        f"but returned HTTP {response.status_code}."
    )
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["statusCode"] == 401
    assert response_data["error"] == "Unauthorized"
    assert response_data["path"] == endpoint

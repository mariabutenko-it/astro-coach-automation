import os
from datetime import date

import pytest

from config.endpoints import (
    KARMA_COINS_TRANSACTIONS,
    KARMA_COINS_WALLET,
    KC_STORE_PURCHASES,
    PAYMENT_SUBSCRIPTIONS,
    PAYMENTS,
    USER_ME,
    USER_ME_ACCOUNT,
    USER_ME_DEVICES,
    USER_ME_PREFERENCES,
)
from config.endpoints import AUTH_LOGOUT, AUTH_VERIFY_OTP, HOME
from utils.api_client import APIClient


def require_qa_credentials():
    email = os.getenv("TEST_EMAIL")
    otp = os.getenv("TEST_OTP")
    if not email or not otp:
        pytest.skip("TEST_EMAIL and a current TEST_OTP are required for authorized read-only tests")
    return email, otp


@pytest.fixture(scope="module")
def authenticated_client(base_url):
    email, otp = require_qa_credentials()
    client = APIClient(base_url=base_url, timeout=60)
    response = client.post(
        AUTH_VERIFY_OTP,
        data={
            "email": email,
            "code": otp,
            "platform": "ANDROID",
            "appVersion": "1.0.0",
            "osVersion": "17",
            "deviceId": "qa-automation-readonly",
        },
    )

    assert response.status_code == 200, "QA login failed; request a fresh OTP and rerun"
    body = response.json()
    assert body["success"] is True
    tokens = body["data"]["tokens"]
    assert tokens["accessToken"]
    client.access_token = tokens["accessToken"]
    return client


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint",
    [
        USER_ME,
        USER_ME_ACCOUNT,
        USER_ME_PREFERENCES,
        USER_ME_DEVICES,
        KARMA_COINS_WALLET,
        f"{KARMA_COINS_TRANSACTIONS}?offset=0&limit=20",
        f"{PAYMENTS}?page=1&limit=20",
        PAYMENT_SUBSCRIPTIONS,
        KC_STORE_PURCHASES,
    ],
    ids=[
        "user-profile",
        "account-summary",
        "preferences",
        "devices",
        "karma-wallet",
        "karma-transactions",
        "payments",
        "subscriptions",
        "store-purchases",
    ],
)
def test_authorized_read_endpoints_return_success(authenticated_client, endpoint):
    response = authenticated_client.get(endpoint)

    assert response.status_code == 200, f"Authorized GET failed for {endpoint}: HTTP {response.status_code}"
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is True
    assert body.get("data") is not None


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint",
    [
        f"{KARMA_COINS_TRANSACTIONS}?offset=-1&limit=20",
        f"{KARMA_COINS_TRANSACTIONS}?offset=0&limit=0",
        f"{PAYMENTS}?page=0&limit=20",
        f"{PAYMENTS}?page=1&limit=0",
    ],
    ids=["transactions-negative-offset", "transactions-zero-limit", "payments-zero-page", "payments-zero-limit"],
)
def test_invalid_authorized_pagination_does_not_cause_server_error(authenticated_client, endpoint):
    response = authenticated_client.get(endpoint)

    assert response.status_code in (200, 400), (
        f"Invalid pagination must be handled or explicitly rejected, not cause HTTP {response.status_code}: {endpoint}"
    )


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    ("endpoint", "expected_type"),
    [
        (USER_ME, dict),
        (USER_ME_PREFERENCES, dict),
        (USER_ME_DEVICES, list),
        (KARMA_COINS_WALLET, dict),
    ],
    ids=["profile", "preferences", "devices", "karma-wallet"],
)
def test_authorized_personal_data_has_expected_shape(authenticated_client, endpoint, expected_type):
    response = authenticated_client.get(endpoint)

    assert response.status_code == 200, f"Authorized GET failed for {endpoint}: HTTP {response.status_code}"
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], expected_type)


@pytest.mark.api
@pytest.mark.authorized
def test_authorized_home_has_daily_energy_contract(authenticated_client):
    response = authenticated_client.get(HOME)

    assert response.status_code == 200
    data = response.json()["data"]
    assert {"userTier", "kcBalance", "dailyEnergy", "dailyFreeAudio"} <= data.keys()
    assert isinstance(data["userTier"], str) and data["userTier"].strip()
    assert isinstance(data["kcBalance"], dict)
    assert isinstance(data["dailyEnergy"], dict)
    date.fromisoformat(data["dailyEnergy"]["date"])


@pytest.mark.api
@pytest.mark.authorized
def test_preferences_accept_current_values_without_changing_them(authenticated_client):
    original_response = authenticated_client.get(USER_ME_PREFERENCES)
    assert original_response.status_code == 200
    original = original_response.json()["data"]

    editable_fields = ("theme", "language", "notificationSettings", "reminderTimes")
    payload = {field: original[field] for field in editable_fields if field in original}
    assert payload, "Preferences response did not contain editable preference fields"

    update_response = authenticated_client.patch(USER_ME_PREFERENCES, data=payload)
    assert update_response.status_code == 200, update_response.status_code
    assert update_response.json()["success"] is True

    current_response = authenticated_client.get(USER_ME_PREFERENCES)
    assert current_response.status_code == 200
    current = current_response.json()["data"]
    for field, expected_value in payload.items():
        assert current[field] == expected_value


@pytest.mark.api
@pytest.mark.authorized
def test_logout_revokes_only_the_current_qa_test_session(authenticated_client):
    response = authenticated_client.post(AUTH_LOGOUT)

    assert response.status_code == 200, response.status_code
    assert response.json()["message"] == "Operation completed successfully."

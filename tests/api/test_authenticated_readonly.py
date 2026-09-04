import os

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
from config.endpoints import AUTH_VERIFY_OTP
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

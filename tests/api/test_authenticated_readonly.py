import os
from datetime import date

import pytest

from config.endpoints import (
    KARMA_COINS_TRANSACTIONS,
    KARMA_COINS_WALLET,
    KC_STORE_PURCHASES,
    PAYMENT_SUBSCRIPTIONS,
    PAYMENTS,
    PREDICTIONS_HOROSCOPE,
    COMPATIBILITY_HISTORY,
    COMPATIBILITY_PROFILES,
    ASTRO_PROFILES,
    ASTRO_PROGRAMS_ENROLLED,
    astro_program_daily_tasks,
    astro_program_progress,
    astro_profile_chart,
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
    "query",
    ["page=-1&limit=20", "page=1&limit=-1", "page=not-a-number&limit=20"],
    ids=["negative-page", "negative-limit", "non-numeric-page"],
)
def test_payments_malformed_pagination_does_not_cause_server_error(authenticated_client, query):
    endpoint = f"{PAYMENTS}?{query}"
    response = authenticated_client.get(endpoint)

    assert response.status_code in (200, 400), response.text


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "query",
    ["offset=0&limit=-1", "offset=not-a-number&limit=20", "offset=0&limit=not-a-number"],
    ids=["negative-limit", "non-numeric-offset", "non-numeric-limit"],
)
def test_karma_transactions_malformed_pagination_does_not_cause_server_error(
    authenticated_client,
    query,
):
    endpoint = f"{KARMA_COINS_TRANSACTIONS}?{query}"
    response = authenticated_client.get(endpoint)

    assert response.status_code in (200, 400), response.text


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


@pytest.mark.api
@pytest.mark.authorized
def test_daily_horoscope_has_documented_content_contract(authenticated_client):
    response = authenticated_client.get(f"{PREDICTIONS_HOROSCOPE}?period=daily")

    assert response.status_code == 200, response.text
    body = response.json()
    assert {"period", "data"} <= body.keys(), (
        "POTENTIAL CONTRACT BUG: Postman documents top-level period and data, "
        f"but the API returned: {body}"
    )
    assert body["period"] == "daily"
    data = body["data"]
    assert {"energyTitle", "energyLevel", "energyProfile", "isPremium", "isLocked"} <= data.keys()
    assert data["energyLevel"] in {"LOW", "NORMAL", "HIGH"}
    assert isinstance(data["energyProfile"], dict)


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "query",
    [
        "period=unknown",
        "period=daily&date=not-a-date",
        "period=daily&date=2026-13-40",
    ],
    ids=["unknown-period", "non-iso-date", "impossible-date"],
)
def test_horoscope_invalid_query_does_not_cause_server_error(authenticated_client, query):
    response = authenticated_client.get(f"{PREDICTIONS_HOROSCOPE}?{query}")

    assert response.status_code in (200, 400, 404), response.text


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint",
    [
        COMPATIBILITY_PROFILES,
        f"{COMPATIBILITY_HISTORY}?category=FAMILY",
    ],
    ids=["saved-profiles", "history"],
)
def test_compatibility_lists_match_documented_array_contract(authenticated_client, endpoint):
    response = authenticated_client.get(endpoint)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list), (
        "POTENTIAL CONTRACT BUG: Postman documents a JSON array for this compatibility "
        f"list endpoint, but the API returned: {body}"
    )


@pytest.mark.api
@pytest.mark.authorized
def test_astro_profile_list_has_enveloped_array_contract(authenticated_client):
    response = authenticated_client.get(ASTRO_PROFILES)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.api
@pytest.mark.authorized
def test_unknown_astro_profile_chart_is_not_exposed(authenticated_client):
    endpoint = astro_profile_chart("00000000-0000-0000-0000-000000000001")
    response = authenticated_client.get(endpoint)

    assert response.status_code in (403, 404), response.text


@pytest.fixture
def enrolled_programs(authenticated_client):
    response = authenticated_client.get(ASTRO_PROGRAMS_ENROLLED)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    return body["data"]


@pytest.mark.api
@pytest.mark.authorized
def test_enrolled_programs_have_unique_ids(enrolled_programs):
    program_ids = [program["programId"] for program in enrolled_programs]
    assert len(program_ids) == len(set(program_ids)), "Enrolled program IDs must be unique"


@pytest.mark.api
@pytest.mark.authorized
def test_enrolled_programs_have_non_empty_titles(enrolled_programs):
    for program in enrolled_programs:
        assert isinstance(program["title"], str) and program["title"].strip()


@pytest.fixture
def enrolled_program_id(enrolled_programs):
    if not enrolled_programs:
        pytest.skip("The QA account has no enrolled programs to inspect")
    return enrolled_programs[0]["programId"]


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint_factory",
    [astro_program_daily_tasks, astro_program_progress],
    ids=["daily-tasks", "progress"],
)
def test_enrolled_program_details_return_data(
    authenticated_client,
    enrolled_program_id,
    endpoint_factory,
):
    response = authenticated_client.get(endpoint_factory(enrolled_program_id))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"] is not None

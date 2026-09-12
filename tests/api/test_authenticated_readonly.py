import os
from datetime import date

import pytest
import requests

from config.endpoints import (
    KARMA_COINS_TRANSACTIONS,
    KARMA_COINS_WALLET,
    KC_STORE_PURCHASES,
    PAYMENT_SUBSCRIPTIONS,
    PAYMENTS,
    payment,
    PREDICTIONS_HOROSCOPE,
    COMPATIBILITY_HISTORY,
    COMPATIBILITY_PROFILES,
    COSMIC_CALENDAR,
    compatibility_history_entry,
    ASTRO_PROFILES,
    ASTRO_PROGRAMS_ENROLLED,
    astro_program_daily_tasks,
    astro_program_enrollment,
    astro_program_progress,
    astro_program_task_player,
    astro_profile_chart,
    astro_profile_karmic_combinations,
    astro_profile_personality,
    astro_profile_signs,
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
def test_cosmic_calendar_snapshot_matches_documented_contract(authenticated_client):
    previous_timeout = authenticated_client.timeout
    authenticated_client.timeout = 15
    try:
        try:
            response = authenticated_client.get(COSMIC_CALENDAR)
        except requests.ConnectionError as error:
            pytest.fail(
                "POTENTIAL PERFORMANCE BUG: authorized cosmic calendar snapshot "
                "did not return a response within 15 seconds. "
                f"Request error: {error}"
            )
    finally:
        authenticated_client.timeout = previous_timeout

    assert response.status_code == 200, response.text
    body = response.json()
    required_fields = {
        "today",
        "activeTransits",
        "upcomingTransits",
        "week",
        "currentMoonPhase",
        "currentMoonDay",
    }
    assert required_fields <= body.keys(), (
        "POTENTIAL CONTRACT BUG: Postman documents a flat cosmic calendar "
        f"snapshot, but the API returned: {body}"
    )
    assert isinstance(body["week"], list) and len(body["week"]) == 7


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


@pytest.mark.api
@pytest.mark.authorized
def test_enrolled_program_task_player_matches_documented_contract(
    authenticated_client,
    enrolled_program_id,
):
    tasks_response = authenticated_client.get(astro_program_daily_tasks(enrolled_program_id))
    assert tasks_response.status_code == 200, tasks_response.text
    tasks_body = tasks_response.json()
    tasks = tasks_body["data"]["items"]
    if not tasks:
        pytest.skip("The enrolled program has no daily tasks to inspect")

    endpoint = astro_program_task_player(enrolled_program_id, tasks[0]["id"])
    response = authenticated_client.get(endpoint)
    assert response.status_code == 200, response.text
    body = response.json()
    required_fields = {
        "itemId",
        "title",
        "language",
        "gender",
        "audioUrl",
        "captionUrl",
        "coverAttachmentId",
    }
    assert required_fields <= body.keys(), (
        "POTENTIAL CONTRACT BUG: Postman documents a flat task-player object, "
        f"but the API returned: {body}"
    )


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


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    ("endpoint_factory", "required_fields"),
    [
        (
            astro_program_enrollment,
            {"programId", "enrollmentId", "title", "currentDay", "todayTasks"},
        ),
        (
            astro_program_progress,
            {"enrollmentId", "status", "currentDay", "totalDays", "progressPercent"},
        ),
        (
            astro_program_daily_tasks,
            {"programId", "programTitle", "dayNumber", "items"},
        ),
    ],
    ids=["enrollment", "progress", "daily-tasks"],
)
def test_enrolled_program_responses_match_documented_flat_contract(
    authenticated_client,
    enrolled_program_id,
    endpoint_factory,
    required_fields,
):
    response = authenticated_client.get(endpoint_factory(enrolled_program_id))

    assert response.status_code == 200, response.text
    body = response.json()
    assert required_fields <= body.keys(), (
        "POTENTIAL CONTRACT BUG: Postman documents a flat response for this "
        "enrolled-program endpoint, but the API returned an envelope or an "
        "incomplete top-level object."
    )


@pytest.fixture
def astro_profile_id(authenticated_client):
    response = authenticated_client.get(ASTRO_PROFILES)
    assert response.status_code == 200, response.text
    profiles = response.json()["data"]
    if not profiles:
        pytest.skip("The QA account has no astro profiles to inspect")
    return profiles[0]["id"]


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint_factory",
    [
        astro_profile_chart,
        astro_profile_signs,
        lambda profile_id: f"{astro_profile_personality(profile_id)}?category=STRENGTH",
        lambda profile_id: f"{astro_profile_karmic_combinations(profile_id)}?polarity=negative",
    ],
    ids=["chart", "signs", "personality", "karmic-combinations"],
)
def test_astro_profile_details_return_data(
    authenticated_client,
    astro_profile_id,
    endpoint_factory,
):
    response = authenticated_client.get(endpoint_factory(astro_profile_id))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"] is not None


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    ("endpoint_factory", "required_fields"),
    [
        (astro_profile_signs, {"sun", "moon", "ascendant"}),
        (lambda profile_id: f"{astro_profile_personality(profile_id)}?category=STRENGTH", {"traits", "archetype"}),
        (lambda profile_id: f"{astro_profile_karmic_combinations(profile_id)}?polarity=negative", {"combinations"}),
    ],
    ids=["signs", "personality", "karmic-combinations"],
)
def test_astro_profile_details_match_documented_flat_contract(
    authenticated_client,
    astro_profile_id,
    endpoint_factory,
    required_fields,
):
    response = authenticated_client.get(endpoint_factory(astro_profile_id))

    assert response.status_code == 200, response.text
    body = response.json()
    assert required_fields <= body.keys(), (
        "POTENTIAL CONTRACT BUG: Postman documents a flat astro-profile detail "
        "response, but the API returned an envelope or an incomplete top-level object."
    )


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint_factory",
    [
        lambda profile_id: f"{astro_profile_personality(profile_id)}?category=NOT_A_CATEGORY",
        lambda profile_id: f"{astro_profile_karmic_combinations(profile_id)}?polarity=invalid",
    ],
    ids=["invalid-personality-category", "invalid-karmic-polarity"],
)
def test_astro_profile_invalid_filters_return_validation_error(
    authenticated_client,
    astro_profile_id,
    endpoint_factory,
):
    response = authenticated_client.get(endpoint_factory(astro_profile_id))
    assert response.status_code == 400, response.text


@pytest.mark.api
@pytest.mark.authorized
def test_compatibility_history_rejects_unknown_category(authenticated_client):
    endpoint = f"{COMPATIBILITY_HISTORY}?category=NOT_A_COMPATIBILITY_CATEGORY"
    response = authenticated_client.get(endpoint)

    assert response.status_code == 400, response.text


@pytest.mark.api
@pytest.mark.authorized
def test_unknown_compatibility_history_entry_returns_not_found(authenticated_client):
    endpoint = compatibility_history_entry("00000000-0000-0000-0000-000000000001")
    response = authenticated_client.get(endpoint)

    assert response.status_code == 404, response.text


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint_factory",
    [astro_program_enrollment, astro_program_progress, astro_program_daily_tasks],
    ids=["enrollment", "progress", "daily-tasks"],
)
def test_unknown_program_detail_is_not_exposed(authenticated_client, endpoint_factory):
    response = authenticated_client.get(
        endpoint_factory("00000000-0000-0000-0000-000000000001")
    )

    assert response.status_code in (403, 404), response.text


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize(
    "endpoint_factory",
    [astro_program_enrollment, astro_program_progress, astro_program_daily_tasks],
    ids=["enrollment", "progress", "daily-tasks"],
)
def test_malformed_program_detail_id_returns_validation_error(
    authenticated_client,
    endpoint_factory,
):
    response = authenticated_client.get(endpoint_factory("not-a-uuid"))
    assert response.status_code == 400, response.text


@pytest.mark.api
@pytest.mark.authorized
def test_subscription_list_matches_documented_array_contract(authenticated_client):
    response = authenticated_client.get(PAYMENT_SUBSCRIPTIONS)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list), (
        "POTENTIAL CONTRACT BUG: Postman documents a JSON array for subscriptions, "
        f"but the API returned: {body}"
    )


@pytest.mark.api
@pytest.mark.authorized
def test_kc_store_purchase_list_matches_documented_array_contract(authenticated_client):
    response = authenticated_client.get(KC_STORE_PURCHASES)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list), (
        "POTENTIAL CONTRACT BUG: Postman documents a JSON array for KC Store purchases, "
        f"but the API returned: {body}"
    )


@pytest.mark.api
@pytest.mark.authorized
@pytest.mark.parametrize("payment_id", ["00000000-0000-0000-0000-000000000001", "not-a-uuid"])
def test_unknown_payment_detail_returns_not_found(authenticated_client, payment_id):
    response = authenticated_client.get(payment(payment_id))
    assert response.status_code == 404, response.text

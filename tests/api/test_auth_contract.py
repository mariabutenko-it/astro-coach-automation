import os

import allure
import pytest

from config.endpoints import AUTH_REFRESH, AUTH_SEND_OTP, AUTH_VERIFY_OTP

INVALID_OTP_EMAIL = "qa-contract-check@example.invalid"


def attach_contract_result(response):
    """Attach contract metadata without leaking tokens or personal data."""
    allure.attach(
        f"status={response.status_code}\n"
        f"content-type={response.headers.get('Content-Type', '')}",
        name="Contract response metadata",
        attachment_type=allure.attachment_type.TEXT,
    )


def verification_payload(platform):
    return {
        "email": INVALID_OTP_EMAIL,
        "code": "0000",
        "platform": platform,
        "appVersion": "1.0.0",
        "osVersion": "17",
        "deviceId": "qa-contract-android",
    }


@pytest.mark.api
@pytest.mark.contract
def test_invalid_otp_matches_documented_status(api_client):
    """Postman documents invalid/expired OTP as HTTP 400."""
    response = api_client.post(
        AUTH_VERIFY_OTP,
        data=verification_payload("ANDROID"),
    )
    attach_contract_result(response)

    assert response.status_code == 400, (
        "POTENTIAL CONTRACT BUG: Postman documents HTTP 400 for an invalid "
        f"or expired OTP, but the API returned HTTP {response.status_code}."
    )


@pytest.mark.api
@pytest.mark.contract
def test_documented_lowercase_platform_is_accepted(api_client):
    """The documented lowercase 'ios' value must pass platform validation."""
    response = api_client.post(
        AUTH_VERIFY_OTP,
        data=verification_payload("ios"),
    )
    attach_contract_result(response)

    response_data = response.json()
    message = response_data.get("message", "")
    if isinstance(message, list):
        message = " ".join(message)

    assert "platform" not in message.lower(), (
        "POTENTIAL CONTRACT BUG: Postman uses platform='ios', but the API "
        f"rejected that documented value: {message}"
    )


@pytest.mark.api
@pytest.mark.contract
def test_send_otp_rate_limit_matches_documented_status(api_client):
    """Opt-in because this test sends email and consumes the resend quota."""
    test_email = os.getenv("RATE_LIMIT_TEST_EMAIL")
    if not test_email:
        pytest.skip(
            "RATE_LIMIT_TEST_EMAIL is not set. Use a dedicated QA mailbox "
            "to run the OTP rate-limit contract test."
        )

    attempts = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "3"))
    attempts = max(1, min(attempts, 5))
    response = None

    for _ in range(attempts):
        response = api_client.post(AUTH_SEND_OTP, data={"email": test_email})
        if response.status_code not in (200, 201):
            break

    assert response is not None
    attach_contract_result(response)

    if response.status_code in (200, 201):
        pytest.skip(
            "The controlled request limit was not reached; no rate-limit "
            "contract assertion was made."
        )

    assert response.status_code == 429, (
        "POTENTIAL CONTRACT BUG: Postman documents HTTP 429 for too many "
        f"OTP requests, but the API returned HTTP {response.status_code}."
    )


@pytest.mark.api
@pytest.mark.contract
def test_refresh_success_matches_documented_schema(api_client):
    """Opt-in because a valid refresh token is required and may be rotated."""
    refresh_token = os.getenv("CONTRACT_REFRESH_TOKEN")
    if not refresh_token:
        pytest.skip(
            "CONTRACT_REFRESH_TOKEN is not set. A dedicated QA refresh token "
            "is required for the success-schema contract test."
        )

    response = api_client.post(
        AUTH_REFRESH,
        data={"refreshToken": refresh_token},
    )
    attach_contract_result(response)

    assert response.status_code == 200, response.status_code
    response_data = response.json()
    assert "tokens" in response_data.get("data", {}), (
        "POTENTIAL CONTRACT BUG: Postman documents tokens under data.tokens, "
        "but the API returned a different refresh response structure."
    )

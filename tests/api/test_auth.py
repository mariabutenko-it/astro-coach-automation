import os

import allure
import pytest

from config.endpoints import (
    AUTH_REFRESH,
    AUTH_SEND_OTP,
    AUTH_VERIFY_OTP,
)

TEST_EMAIL = os.getenv(
    "TEST_EMAIL",
    "",
)


def require_test_email():
    if not TEST_EMAIL:
        pytest.skip(
            "TEST_EMAIL is not set. A dedicated QA email is required "
            "for tests that send or verify OTP."
        )

    return TEST_EMAIL


@pytest.mark.api
def test_send_otp(api_client):

    test_email = require_test_email()

    response = api_client.post(
        AUTH_SEND_OTP,
        data={
            "email": test_email,
        },
    )

    allure.attach(
        response.text,
        name="Send OTP response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["success"] is True
    assert "data" in response_data
    assert response_data["data"]["message"] == ("Verification code sent to your email")


@pytest.mark.api
def test_send_otp_invalid_email(api_client):

    response = api_client.post(
        AUTH_SEND_OTP,
        data={
            "email": "wrong-email",
        },
    )

    allure.attach(
        response.text,
        name="Invalid email response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 400

    response_data = response.json()

    assert response_data["statusCode"] == 400
    assert "email must be an email" in response_data["message"]


@pytest.mark.api
def test_verify_otp_invalid_code(api_client):

    test_email = require_test_email()

    response = api_client.post(
        AUTH_VERIFY_OTP,
        data={
            "email": test_email,
            "code": "0000",
            "platform": "ANDROID",
            "appVersion": "1.0.0",
            "osVersion": "17",
            "deviceId": "qa-automation-android",
        },
    )

    allure.attach(
        response.text,
        name="Invalid OTP response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 401

    response_data = response.json()

    assert response_data["statusCode"] == 401
    assert response_data["message"] == ("Invalid or expired verification code")


@pytest.mark.api
def test_authentication_flow(api_client):

    test_email = require_test_email()

    # 1. Send OTP
    send_response = api_client.post(
        AUTH_SEND_OTP,
        data={
            "email": test_email,
        },
    )

    allure.attach(
        send_response.text,
        name="Send OTP response",
        attachment_type=allure.attachment_type.TEXT,
    )

    if send_response.status_code == 403:
        response_data = send_response.json()

        assert response_data["statusCode"] == 403

        pytest.skip(
            "OTP resend is temporarily blocked. Wait for the current OTP to expire."
        )

    assert send_response.status_code == 200, send_response.text

    # 2. Get OTP from environment
    otp_code = os.getenv("TEST_OTP")

    if not otp_code:
        pytest.skip(
            "TEST_OTP is not set. "
            "Request OTP and set TEST_OTP before running "
            "test_authentication_flow."
        )

    assert otp_code.isdigit(), "OTP must contain only digits"
    assert len(otp_code) == 4, "OTP must contain exactly 4 digits"

    # 3. Verify OTP
    response = api_client.post(
        AUTH_VERIFY_OTP,
        data={
            "email": test_email,
            "code": otp_code,
            "platform": "ANDROID",
            "appVersion": "1.0.0",
            "osVersion": "17",
            "deviceId": "qa-automation-android",
        },
    )

    allure.attach(
        response.text,
        name="OTP verification response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 200, response.text

    response_data = response.json()

    assert response_data["success"] is True
    assert "data" in response_data

    data = response_data["data"]

    assert data["userId"]
    assert "tokens" in data

    tokens = data["tokens"]

    assert tokens["accessToken"]
    assert tokens["refreshToken"]
    assert tokens["expiresIn"] > 0

    # Save refresh token for the refresh test
    refresh_token = tokens["refreshToken"]

    os.environ["TEST_REFRESH_TOKEN"] = refresh_token


@pytest.mark.api
def test_refresh_success(api_client):

    refresh_token = os.getenv("TEST_REFRESH_TOKEN")

    if not refresh_token:
        pytest.skip(
            "TEST_REFRESH_TOKEN is not set. "
            "Run test_authentication_flow successfully first."
        )

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": refresh_token,
        },
    )

    allure.attach(
        response.text,
        name="Refresh token response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 200, response.text

    response_data = response.json()

    assert response_data["success"] is True
    assert "data" in response_data

    data = response_data["data"]

    assert data["accessToken"]
    assert data["refreshToken"]
    assert data["expiresIn"] > 0


@pytest.mark.api
def test_refresh_invalid_token(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": "invalid-refresh-token",
        },
    )

    allure.attach(
        response.text,
        name="Invalid refresh token response",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert response.status_code == 401

    response_data = response.json()

    assert response_data["statusCode"] == 401
    assert response_data["message"] == "Unauthorized"

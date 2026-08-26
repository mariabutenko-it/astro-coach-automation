import pytest
import allure

from config.endpoints import AUTH_REFRESH


@pytest.mark.api
def test_refresh_empty_token(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": ""
        }
    )

    allure.attach(
        response.text,
        name="Empty refresh token response",
        attachment_type=allure.attachment_type.TEXT
    )

    assert response.status_code in [400, 401]


@pytest.mark.api
def test_refresh_missing_token(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={}
    )

    allure.attach(
        response.text,
        name="Missing refresh token response",
        attachment_type=allure.attachment_type.TEXT
    )

    assert response.status_code in [400, 401]


@pytest.mark.api
def test_refresh_null_token(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": None
        }
    )

    allure.attach(
        response.text,
        name="Null refresh token response",
        attachment_type=allure.attachment_type.TEXT
    )

    assert response.status_code in [400, 401]


@pytest.mark.api
def test_refresh_invalid_jwt(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": "abc.def.xyz"
        }
    )

    allure.attach(
        response.text,
        name="Invalid JWT refresh token response",
        attachment_type=allure.attachment_type.TEXT
    )

    assert response.status_code == 401

    response_data = response.json()

    assert response_data["statusCode"] == 401


@pytest.mark.api
def test_refresh_random_token(api_client):

    response = api_client.post(
        AUTH_REFRESH,
        data={
            "refreshToken": "random-token-123456"
        }
    )

    allure.attach(
        response.text,
        name="Random token response",
        attachment_type=allure.attachment_type.TEXT
    )

    assert response.status_code == 401

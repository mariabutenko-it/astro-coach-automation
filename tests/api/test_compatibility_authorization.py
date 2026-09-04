import pytest

from config.endpoints import (
    COMPATIBILITY_CHECK,
    COMPATIBILITY_PROFILES,
    compatibility_history_entry,
)

RESOURCE_ID = "00000000-0000-0000-0000-000000000001"


def assert_unauthorized(response, endpoint):
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.security
def test_saving_compatibility_profile_requires_authorization(api_client):
    assert_unauthorized(api_client.post(COMPATIBILITY_PROFILES, data={}), COMPATIBILITY_PROFILES)


@pytest.mark.api
@pytest.mark.security
def test_compatibility_check_requires_authorization(api_client):
    assert_unauthorized(api_client.post(COMPATIBILITY_CHECK, data={}), COMPATIBILITY_CHECK)


@pytest.mark.api
@pytest.mark.security
def test_compatibility_history_entry_requires_authorization(api_client):
    endpoint = compatibility_history_entry(RESOURCE_ID)
    assert_unauthorized(api_client.get(endpoint), endpoint)

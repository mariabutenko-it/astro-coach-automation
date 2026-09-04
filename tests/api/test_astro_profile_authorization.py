import pytest

from config.endpoints import (
    astro_profile_chart,
    astro_profile_chart_export,
    astro_profile_karmic_combinations,
    astro_profile_personality,
    astro_profile_primary,
    astro_profile_signs,
)

PROFILE_ID = "00000000-0000-0000-0000-000000000001"


def assert_unauthorized(response, endpoint):
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        astro_profile_chart(PROFILE_ID),
        astro_profile_signs(PROFILE_ID),
        f"{astro_profile_personality(PROFILE_ID)}?category=STRENGTH",
        f"{astro_profile_karmic_combinations(PROFILE_ID)}?polarity=negative",
    ],
    ids=["chart", "signs", "personality", "karmic-combinations"],
)
def test_astro_profile_read_endpoints_require_authorization(api_client, endpoint):
    assert_unauthorized(api_client.get(endpoint), endpoint)


@pytest.mark.api
@pytest.mark.security
def test_astro_profile_primary_requires_authorization(api_client):
    endpoint = astro_profile_primary(PROFILE_ID)
    assert_unauthorized(api_client.put(endpoint), endpoint)


@pytest.mark.api
@pytest.mark.security
def test_astro_profile_chart_export_requires_authorization(api_client):
    endpoint = astro_profile_chart_export(PROFILE_ID)
    assert_unauthorized(api_client.post(endpoint), endpoint)

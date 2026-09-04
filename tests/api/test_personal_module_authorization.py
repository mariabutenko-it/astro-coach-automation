import pytest

from config.endpoints import (
    ASTRO_PROFILES,
    COMPATIBILITY_PROFILES,
    PREDICTIONS_HOROSCOPE,
)


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        f"{PREDICTIONS_HOROSCOPE}?period=monthly&date=2026-05-01",
        COMPATIBILITY_PROFILES,
        ASTRO_PROFILES,
    ],
    ids=["horoscope", "compatibility-profiles", "astro-profiles"],
)
def test_personal_modules_require_authorization(api_client, endpoint):
    response = api_client.get(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

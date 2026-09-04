import pytest

from config.endpoints import (
    ASTRO_PROGRAMS_ENROLLED,
    COMPATIBILITY_HISTORY,
    PAYMENT_SUBSCRIPTIONS,
)


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        ASTRO_PROGRAMS_ENROLLED,
        f"{COMPATIBILITY_HISTORY}?category=FAMILY",
        PAYMENT_SUBSCRIPTIONS,
    ],
    ids=["enrolled-programs", "compatibility-history", "subscriptions"],
)
def test_user_data_endpoints_require_authorization(api_client, endpoint):
    response = api_client.get(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

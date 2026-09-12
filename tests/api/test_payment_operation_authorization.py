import pytest

from config.endpoints import compatibility_profile, payment, payment_refund, subscription_cancel


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        payment_refund("00000000-0000-0000-0000-000000000001"),
        subscription_cancel("00000000-0000-0000-0000-000000000001"),
    ],
    ids=["refund-payment", "cancel-subscription"],
)
def test_payment_operations_require_authorization(api_client, endpoint):
    response = api_client.post(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.security
def test_private_payment_detail_requires_authorization(api_client):
    endpoint = payment("00000000-0000-0000-0000-000000000001")

    response = api_client.get(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.security
def test_deleting_compatibility_profile_requires_authorization(api_client):
    endpoint = compatibility_profile("00000000-0000-0000-0000-000000000001")
    response = api_client.delete(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

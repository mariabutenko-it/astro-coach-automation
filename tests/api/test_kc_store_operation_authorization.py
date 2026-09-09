import pytest

from config.endpoints import kc_store_purchase_use


@pytest.mark.api
@pytest.mark.security
def test_using_store_purchase_requires_authorization(api_client):
    endpoint = kc_store_purchase_use("00000000-0000-0000-0000-000000000001")
    response = api_client.post(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

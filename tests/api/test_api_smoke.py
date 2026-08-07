import pytest

from config.endpoints import HEALTH


@pytest.mark.api
def test_get_request(api_client):

    response = api_client.get(HEALTH)

    assert response.status_code == 200

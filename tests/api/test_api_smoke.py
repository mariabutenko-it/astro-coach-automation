import pytest

from utils.api_client import APIClient


@pytest.mark.api
def test_get_request():

    client = APIClient(
        base_url="https://example.com"
    )

    response = client.get("/")

    assert response.status_code == 200


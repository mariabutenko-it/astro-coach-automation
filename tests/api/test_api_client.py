from utils.api_client import APIClient


def test_api_client_creation():
    client = APIClient()

    assert client.base_url is not None
    assert client.timeout == 15


def test_api_client_merges_custom_headers():
    client = APIClient()

    headers = client._headers({"Accept-Language": "en"})

    assert headers["Accept"] == "application/json"
    assert headers["Accept-Language"] == "en"

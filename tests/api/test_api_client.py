from utils.api_client import APIClient


def test_api_client_creation():
    client = APIClient()

    assert client.base_url is not None

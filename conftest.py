import pytest

from utils.api_client import APIClient


@pytest.fixture(scope="session")
def base_url():
    return "https://example.com"


@pytest.fixture
def api_client(base_url):

    return APIClient(
        base_url=base_url
    )

import pytest

from utils.api_client import APIClient
from config.settings import API_URL


@pytest.fixture(scope="session")
def base_url():
    return API_URL


@pytest.fixture
def api_client(base_url):
    return APIClient(
        base_url=base_url
    )

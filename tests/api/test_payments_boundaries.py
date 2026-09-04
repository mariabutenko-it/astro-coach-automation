from decimal import Decimal

import pytest

from config.endpoints import (
    KARMA_COINS_PRICING,
    KARMA_COINS_TRANSACTIONS,
    KARMA_COINS_WALLET,
    PAYMENTS,
)
from utils.api_client import APIClient

PRICING_FIELDS = {"actionType", "kcPrice", "priceMinor", "currency"}


@pytest.fixture(scope="module")
def payments_client(base_url):
    return APIClient(base_url=base_url, timeout=60)


@pytest.fixture(scope="module")
def karma_pricing(payments_client):
    response = payments_client.get(KARMA_COINS_PRICING)

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list) and body["data"]
    return body["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_karma_coin_pricing_contract(karma_pricing):
    for price in karma_pricing:
        assert PRICING_FIELDS <= price.keys()
        assert isinstance(price["actionType"], str) and price["actionType"].strip()
        assert isinstance(price["kcPrice"], int) and price["kcPrice"] > 0

        if price["priceMinor"] is None:
            assert price["currency"] is None
        else:
            assert Decimal(price["priceMinor"]) > 0
            assert isinstance(price["currency"], str) and price["currency"].strip()


@pytest.mark.api
def test_karma_coin_pricing_has_unique_action_types(karma_pricing):
    action_types = [price["actionType"] for price in karma_pricing]
    assert len(action_types) == len(set(action_types)), "Duplicate Karma Coin actionType found"


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        KARMA_COINS_WALLET,
        f"{KARMA_COINS_TRANSACTIONS}?offset=0&limit=20",
        f"{PAYMENTS}?page=1&limit=20",
    ],
    ids=["wallet", "transactions", "payments"],
)
def test_payment_data_requires_authorization(payments_client, endpoint):
    response = payments_client.get(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

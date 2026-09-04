from uuid import UUID

import pytest

from config.endpoints import KC_STORE, KC_STORE_ITEMS, KC_STORE_PURCHASES

REQUIRED_ITEM_FIELDS = {
    "id",
    "itemType",
    "name",
    "imageUrl",
    "kcPrice",
    "originalKcPrice",
    "discountPercentage",
    "isOffer",
    "quantity",
}


@pytest.fixture
def store_items(api_client):
    response = api_client.get(KC_STORE_ITEMS)

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list) and body["data"]
    return body["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_kc_store_catalogue_contract(store_items):
    for item in store_items:
        assert REQUIRED_ITEM_FIELDS <= item.keys()
        UUID(item["id"])
        assert isinstance(item["itemType"], str) and item["itemType"].strip()
        assert isinstance(item["name"], str) and item["name"].strip()
        assert isinstance(item["imageUrl"], str) and item["imageUrl"].startswith("https://")
        assert isinstance(item["kcPrice"], int) and item["kcPrice"] > 0
        assert isinstance(item["quantity"], int) and item["quantity"] > 0
        assert isinstance(item["isOffer"], bool)


@pytest.mark.api
def test_kc_store_catalogue_has_unique_ids_and_names(store_items):
    item_ids = [item["id"] for item in store_items]
    item_names = [item["name"] for item in store_items]

    assert len(item_ids) == len(set(item_ids)), "Duplicate KC Store item IDs found"
    assert len(item_names) == len(set(item_names)), "Duplicate KC Store item names found"


@pytest.mark.api
def test_kc_store_offer_fields_are_consistent(store_items):
    for item in store_items:
        if item["originalKcPrice"] is not None:
            assert isinstance(item["originalKcPrice"], int)
            assert item["originalKcPrice"] > item["kcPrice"]
            assert isinstance(item["discountPercentage"], int)
            assert item["discountPercentage"] > 0
        else:
            assert item["discountPercentage"] is None


@pytest.mark.api
def test_kc_store_has_safe_guest_view(api_client):
    response = api_client.get(KC_STORE)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["balance"] == 0
    assert isinstance(data["items"], list) and data["items"]
    assert data["recentPurchases"] == []


@pytest.mark.api
@pytest.mark.security
def test_kc_store_purchases_require_authorization(api_client):
    response = api_client.get(KC_STORE_PURCHASES)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == KC_STORE_PURCHASES

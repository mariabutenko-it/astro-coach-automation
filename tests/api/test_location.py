import pytest

from config.endpoints import LOCATION_SEARCH, location_details
from utils.api_client import APIClient

SEARCH_ITEM_FIELDS = {"placeId", "mainText", "secondaryText", "description"}
DETAIL_FIELDS = {"placeId", "name", "description", "latitude", "longitude"}


@pytest.fixture(scope="module")
def location_client(base_url):
    return APIClient(base_url=base_url, timeout=60)


@pytest.fixture(scope="module")
def moscow_locations(location_client):
    response = location_client.get(f"{LOCATION_SEARCH}?q=Moscow&lang=en")

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list) and body["data"]
    return body["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_location_search_returns_matching_places(moscow_locations):
    assert all(SEARCH_ITEM_FIELDS <= item.keys() for item in moscow_locations)
    assert all(
        isinstance(item[field], str) and item[field].strip()
        for item in moscow_locations
        for field in SEARCH_ITEM_FIELDS
    )
    assert any("moscow" in item["description"].lower() for item in moscow_locations)


@pytest.mark.api
def test_location_search_has_unique_place_ids(moscow_locations):
    place_ids = [item["placeId"] for item in moscow_locations]
    assert len(place_ids) == len(set(place_ids)), "Location search returned duplicate placeId values"


@pytest.mark.api
@pytest.mark.contract
def test_location_details_match_selected_search_result(location_client, moscow_locations):
    selected = next(item for item in moscow_locations if item["secondaryText"] == "Russia")
    endpoint = f"{location_details(selected['placeId'])}?lang=en"
    response = location_client.get(endpoint)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    location = body["data"]
    assert DETAIL_FIELDS <= location.keys()
    assert location["placeId"] == selected["placeId"]
    assert location["name"] == selected["mainText"]
    assert isinstance(location["latitude"], (int, float)) and -90 <= location["latitude"] <= 90
    assert isinstance(location["longitude"], (int, float)) and -180 <= location["longitude"] <= 180


@pytest.mark.api
@pytest.mark.parametrize(
    "query",
    ["q=&lang=en", "q=Moscow&lang=xx-INVALID"],
    ids=["empty-query", "invalid-language"],
)
def test_location_search_rejects_invalid_parameters(location_client, query):
    endpoint = f"{LOCATION_SEARCH}?{query}"
    response = location_client.get(endpoint)

    assert response.status_code == 400, response.text
    body = response.json()
    assert body["statusCode"] == 400
    assert body["error"] == "Bad Request"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.contract
def test_unknown_place_id_returns_documented_validation_error(location_client):
    endpoint = f"{location_details('not-a-real-place')}?lang=en"
    response = location_client.get(endpoint)

    assert response.status_code == 400, (
        "POTENTIAL CONTRACT BUG: Postman documents HTTP 400 for an invalid placeId, "
        f"but the API returned HTTP {response.status_code}: {response.text}"
    )

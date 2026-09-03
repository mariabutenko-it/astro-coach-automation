from uuid import UUID

import pytest

from config.endpoints import ZODIAC_SIGNS, zodiac_sign
from utils.api_client import APIClient

EXPECTED_SLUGS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]
REQUIRED_FIELDS = {
    "id",
    "slug",
    "order",
    "name",
    "description",
    "keywords",
    "iconUrl",
    "coverUrl",
}
ALLOWED_ELEMENTS = {"FIRE", "EARTH", "AIR", "WATER"}


@pytest.fixture(scope="module")
def zodiac_signs_response(base_url):
    client = APIClient(base_url=base_url, timeout=60)
    return client.get(ZODIAC_SIGNS, headers={"Accept-Language": "en"})


@pytest.fixture(scope="module")
def zodiac_signs(zodiac_signs_response):
    assert zodiac_signs_response.status_code == 200, zodiac_signs_response.text
    assert zodiac_signs_response.headers["Content-Type"].startswith(
        "application/json"
    )

    response_data = zodiac_signs_response.json()
    assert response_data["success"] is True
    assert isinstance(response_data["data"], list)
    return response_data["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_zodiac_signs_returns_all_twelve_signs(zodiac_signs):
    assert len(zodiac_signs) == 12


@pytest.mark.api
@pytest.mark.contract
def test_zodiac_signs_have_expected_order_and_slugs(zodiac_signs):
    assert [sign["order"] for sign in zodiac_signs] == list(range(1, 13))
    assert [sign["slug"] for sign in zodiac_signs] == EXPECTED_SLUGS


@pytest.mark.api
def test_zodiac_signs_have_unique_ids_slugs_and_orders(zodiac_signs):
    for field in ("id", "slug", "order"):
        values = [sign[field] for sign in zodiac_signs]
        assert len(values) == len(set(values)), f"Duplicate zodiac {field} found"


@pytest.mark.api
@pytest.mark.contract
def test_zodiac_signs_match_documented_item_contract(zodiac_signs):
    for sign in zodiac_signs:
        assert REQUIRED_FIELDS <= sign.keys()
        UUID(sign["id"])
        assert isinstance(sign["name"], str) and sign["name"].strip()
        assert isinstance(sign["description"], str) and sign["description"].strip()
        assert isinstance(sign["keywords"], list) and sign["keywords"]
        assert all(
            isinstance(keyword, str) and keyword.strip()
            for keyword in sign["keywords"]
        )
        assert sign["iconUrl"] is None or isinstance(sign["iconUrl"], str)
        assert sign["coverUrl"] is None or isinstance(sign["coverUrl"], str)


@pytest.mark.api
def test_zodiac_signs_use_valid_elements(zodiac_signs):
    assert all(sign.get("element") in ALLOWED_ELEMENTS for sign in zodiac_signs)
    assert {sign["element"] for sign in zodiac_signs} == ALLOWED_ELEMENTS


@pytest.mark.api
@pytest.mark.contract
def test_zodiac_signs_support_english_localization(zodiac_signs):
    assert [sign["name"] for sign in zodiac_signs] == [
        slug.capitalize() for slug in EXPECTED_SLUGS
    ]


@pytest.mark.api
@pytest.mark.contract
def test_unknown_zodiac_slug_returns_404(api_client):
    endpoint = zodiac_sign("not-a-real-zodiac-sign")
    response = api_client.get(endpoint)

    assert response.status_code == 404, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["statusCode"] == 404
    assert response_data["path"] == endpoint

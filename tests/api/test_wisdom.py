import pytest

from config.endpoints import (
    WISDOM_GLOSSARY,
    WISDOM_WORD_OF_THE_DAY,
    WISDOM_XP,
    wisdom_glossary_term,
)
from utils.api_client import APIClient

GLOSSARY_TERM_FIELDS = {"slug", "term", "definition", "category"}


@pytest.fixture(scope="module")
def wisdom_client(base_url):
    return APIClient(base_url=base_url, timeout=60)


def get_wisdom_data(client, endpoint, language="en"):
    response = client.get(endpoint, headers={"Accept-Language": language})

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    body = response.json()
    assert body["success"] is True
    return body["data"]


@pytest.fixture(scope="module")
def glossary_page(wisdom_client):
    return get_wisdom_data(wisdom_client, f"{WISDOM_GLOSSARY}?offset=0&limit=5")


@pytest.mark.api
@pytest.mark.smoke
def test_glossary_returns_paginated_terms(glossary_page):
    assert set(glossary_page) >= {"items", "total", "offset", "limit"}
    assert isinstance(glossary_page["items"], list) and glossary_page["items"]
    assert glossary_page["offset"] == 0
    assert glossary_page["limit"] == 5
    assert glossary_page["total"] >= len(glossary_page["items"])


@pytest.mark.api
@pytest.mark.contract
def test_glossary_terms_have_required_content(glossary_page):
    for item in glossary_page["items"]:
        assert GLOSSARY_TERM_FIELDS <= item.keys()
        assert all(isinstance(item[field], str) and item[field].strip() for field in GLOSSARY_TERM_FIELDS)
        assert item.get("imageUrl") is None or isinstance(item["imageUrl"], str)
        assert item.get("imageDarkUrl") is None or isinstance(item["imageDarkUrl"], str)


@pytest.mark.api
def test_glossary_category_filter_returns_only_requested_category(wisdom_client):
    data = get_wisdom_data(
        wisdom_client,
        f"{WISDOM_GLOSSARY}?category=practices&offset=0&limit=20",
    )

    assert data["items"], "Known glossary category practices returned no items"
    assert all(item["category"] == "practices" for item in data["items"])


@pytest.mark.api
def test_glossary_supports_english_localization(wisdom_client):
    russian = get_wisdom_data(wisdom_client, f"{WISDOM_GLOSSARY}?offset=0&limit=1", language="ru")
    english = get_wisdom_data(wisdom_client, f"{WISDOM_GLOSSARY}?offset=0&limit=1", language="en")

    assert russian["items"][0]["slug"] == english["items"][0]["slug"]
    assert russian["items"][0]["term"] != english["items"][0]["term"]


@pytest.mark.api
@pytest.mark.contract
def test_unknown_glossary_slug_returns_documented_404(wisdom_client):
    endpoint = wisdom_glossary_term("not-a-real-glossary-term")
    response = wisdom_client.get(endpoint)

    assert response.status_code == 404, (
        "POTENTIAL CONTRACT BUG: Postman documents HTTP 404 for an unknown "
        f"glossary slug, but the API returned HTTP {response.status_code}: {response.text}"
    )


@pytest.mark.api
@pytest.mark.parametrize(
    "query",
    ["offset=-1&limit=20", "offset=0&limit=0"],
    ids=["negative-offset", "zero-limit"],
)
def test_glossary_rejects_invalid_pagination(wisdom_client, query):
    endpoint = f"{WISDOM_GLOSSARY}?{query}"
    response = wisdom_client.get(endpoint)

    assert response.status_code == 400, (
        "POTENTIAL VALIDATION BUG: invalid glossary pagination must return HTTP 400, "
        f"but {endpoint} returned HTTP {response.status_code}: {response.text}"
    )


@pytest.mark.api
def test_word_of_the_day_has_valid_scheduled_term_when_present(wisdom_client):
    data = get_wisdom_data(wisdom_client, WISDOM_WORD_OF_THE_DAY)

    if data is None:
        pytest.skip("No Word of the Day is scheduled for the current date")

    assert set(data) >= {"date", "term"}
    assert GLOSSARY_TERM_FIELDS <= data["term"].keys()


@pytest.mark.api
@pytest.mark.security
def test_xp_requires_authorization(wisdom_client):
    response = wisdom_client.get(WISDOM_XP)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"

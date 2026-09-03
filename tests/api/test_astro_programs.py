from uuid import UUID

import pytest

from config.endpoints import (
    ASTRO_PROGRAM_THEMES,
    ASTRO_PROGRAMS,
    ASTRO_PROGRAMS_FEATURED,
    astro_program,
)
from utils.api_client import APIClient

THEME_REQUIRED_FIELDS = {"id", "slug", "name"}
PROGRAM_REQUIRED_FIELDS = {
    "id",
    "slug",
    "title",
    "tagline",
    "type",
    "accessType",
    "isPersonalized",
    "isFeatured",
    "themeIds",
}


@pytest.fixture(scope="module")
def programs_client(base_url):
    return APIClient(base_url=base_url, timeout=60)


def get_data(client, endpoint):
    response = client.get(endpoint, headers={"Accept-Language": "en"})
    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["success"] is True
    return response_data["data"]


@pytest.fixture(scope="module")
def themes(programs_client):
    data = get_data(programs_client, ASTRO_PROGRAM_THEMES)
    assert isinstance(data, list) and data
    return data


@pytest.fixture(scope="module")
def featured_programs(programs_client):
    data = get_data(programs_client, ASTRO_PROGRAMS_FEATURED)
    assert isinstance(data, list) and data
    return data


@pytest.mark.api
@pytest.mark.contract
def test_program_themes_match_documented_contract(themes):
    for theme in themes:
        assert THEME_REQUIRED_FIELDS <= theme.keys()
        UUID(theme["id"])
        assert isinstance(theme["slug"], str) and theme["slug"].strip()
        assert isinstance(theme["name"], str) and theme["name"].strip()


@pytest.mark.api
def test_program_themes_have_unique_ids_and_slugs(themes):
    for field in ("id", "slug"):
        values = [theme[field] for theme in themes]
        assert len(values) == len(set(values)), f"Duplicate theme {field} found"


@pytest.mark.api
@pytest.mark.contract
def test_featured_programs_match_documented_contract(featured_programs):
    for program in featured_programs:
        assert PROGRAM_REQUIRED_FIELDS <= program.keys()
        UUID(program["id"])
        assert isinstance(program["slug"], str) and program["slug"].strip()
        assert isinstance(program["title"], str) and program["title"].strip()
        assert isinstance(program["themeIds"], list)
        assert all(UUID(theme_id) for theme_id in program["themeIds"])


@pytest.mark.api
@pytest.mark.contract
def test_featured_endpoint_returns_only_featured_programs(featured_programs):
    invalid_programs = [
        program["slug"]
        for program in featured_programs
        if program["isFeatured"] is not True
    ]
    assert not invalid_programs, (
        "POTENTIAL CONTRACT BUG: /astro-programs/featured returned programs "
        f"with isFeatured=false: {invalid_programs}"
    )


@pytest.mark.api
@pytest.mark.contract
def test_program_catalogue_pagination_contract(programs_client):
    data = get_data(programs_client, f"{ASTRO_PROGRAMS}?page=1&limit=5")

    assert set(data) >= {"items", "total"}
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 5
    assert isinstance(data["total"], int) and data["total"] >= len(data["items"])
    assert all(PROGRAM_REQUIRED_FIELDS <= item.keys() for item in data["items"])


@pytest.mark.api
def test_program_catalogue_rejects_page_zero(programs_client):
    endpoint = f"{ASTRO_PROGRAMS}?page=0&limit=20"
    response = programs_client.get(endpoint)

    assert response.status_code == 400, response.text
    response_data = response.json()
    assert response_data["statusCode"] == 400
    assert response_data["error"] == "Bad Request"
    assert response_data["path"] == endpoint


@pytest.mark.api
@pytest.mark.parametrize(
    ("query", "expected_message"),
    [
        ("page=one&limit=20", "page must be an integer number"),
        ("page=1&limit=0", "limit must not be less than 1"),
        (
            "page=1&limit=20&type=NOT_A_PROGRAM_TYPE",
            "type must be one of the following values",
        ),
        (
            "page=1&limit=20&themeId=not-a-uuid",
            "themeId must be a UUID",
        ),
    ],
    ids=["non-integer-page", "zero-limit", "invalid-type", "invalid-theme-id"],
)
def test_program_catalogue_rejects_invalid_query_parameters(
    programs_client,
    query,
    expected_message,
):
    endpoint = f"{ASTRO_PROGRAMS}?{query}"
    response = programs_client.get(endpoint)

    assert response.status_code == 400, response.text
    response_data = response.json()
    message = response_data["message"]
    if isinstance(message, list):
        message = " ".join(message)

    assert response_data["statusCode"] == 400
    assert response_data["error"] == "Bad Request"
    assert expected_message.lower() in message.lower()
    assert response_data["path"] == endpoint


@pytest.mark.api
def test_program_detail_rejects_malformed_id(programs_client):
    endpoint = astro_program("not-a-uuid")
    response = programs_client.get(endpoint)

    assert response.status_code == 400, response.text
    response_data = response.json()
    assert response_data["statusCode"] == 400
    assert response_data["error"] == "Bad Request"
    assert response_data["path"] == endpoint


@pytest.mark.api
def test_unknown_program_id_returns_404(programs_client):
    endpoint = astro_program("00000000-0000-4000-8000-000000000000")
    response = programs_client.get(endpoint)

    assert response.status_code == 404, response.text
    response_data = response.json()
    assert response_data["statusCode"] == 404
    assert response_data["error"] == "Not Found"
    assert response_data["path"] == endpoint

from datetime import date
from uuid import UUID

import pytest
import requests

from config.endpoints import COSMIC_CALENDAR, COSMIC_CALENDAR_TRANSITS
from utils.api_client import APIClient


def get_calendar_data(api_client, endpoint):
    response = api_client.get(endpoint)

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], dict)
    return body["data"]


@pytest.fixture
def transits(api_client):
    return get_calendar_data(api_client, COSMIC_CALENDAR_TRANSITS)


@pytest.mark.api
@pytest.mark.smoke
def test_planet_transits_are_grouped_into_current_and_coming(transits):
    assert {"current", "coming"} <= transits.keys()
    assert isinstance(transits["current"], list)
    assert isinstance(transits["coming"], list)


@pytest.mark.api
def test_planet_transits_have_valid_dates_and_unique_ids(transits):
    all_transits = transits["current"] + transits["coming"]
    assert all_transits, "Cosmic Calendar must provide at least one transit"

    transit_ids = []
    for transit in all_transits:
        assert {"id", "dateFrom", "dateTo", "title", "planetSlug", "zodiacSignSlug"} <= transit.keys()
        UUID(transit["id"])
        assert date.fromisoformat(transit["dateFrom"]) <= date.fromisoformat(transit["dateTo"])
        assert isinstance(transit["title"], str) and transit["title"].strip()
        transit_ids.append(transit["id"])

    assert len(transit_ids) == len(set(transit_ids)), "Duplicate transit IDs found"


@pytest.mark.api
@pytest.mark.security
def test_cosmic_calendar_snapshot_rejects_unauthorized_request_without_timeout(base_url):
    client = APIClient(base_url=base_url, timeout=15)

    try:
        response = client.get(COSMIC_CALENDAR)
    except requests.ConnectionError as error:
        pytest.fail(
            "POTENTIAL PERFORMANCE/SECURITY BUG: cosmic calendar snapshot did not "
            "return an authorization response within 15 seconds. "
            f"Request error: {error}"
        )

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"

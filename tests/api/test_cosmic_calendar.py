from datetime import date
from uuid import UUID

import pytest

from config.endpoints import COSMIC_CALENDAR_TRANSITS


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

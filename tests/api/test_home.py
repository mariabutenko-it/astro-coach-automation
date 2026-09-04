from datetime import date

import pytest

from config.endpoints import HOME


@pytest.fixture
def guest_home(api_client):
    response = api_client.get(HOME)

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], dict)
    return body["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_guest_home_has_required_sections(guest_home):
    assert {
        "userTier",
        "greeting",
        "kcBalance",
        "banner",
        "dailyEnergy",
        "suggestedActivities",
        "lockedFeatures",
        "dailyFreeAudio",
    } <= guest_home.keys()
    assert guest_home["userTier"] == "guest"
    assert isinstance(guest_home["greeting"], str) and guest_home["greeting"].strip()


@pytest.mark.api
def test_guest_home_has_zero_personal_balance(guest_home):
    balance = guest_home["kcBalance"]

    assert {"coins", "freeCredits"} <= balance.keys()
    assert balance["coins"] == 0
    assert balance["freeCredits"] == 0


@pytest.mark.api
def test_guest_home_daily_energy_contract(guest_home):
    daily_energy = guest_home["dailyEnergy"]

    assert {"date", "isPersonalized", "colorsOfDay", "transits"} <= daily_energy.keys()
    date.fromisoformat(daily_energy["date"])
    assert daily_energy["isPersonalized"] is False
    assert isinstance(daily_energy["colorsOfDay"], list) and daily_energy["colorsOfDay"]
    assert isinstance(daily_energy["transits"], list)

    for color in daily_energy["colorsOfDay"]:
        assert {"slug", "name", "role", "action", "description"} <= color.keys()


@pytest.mark.api
def test_guest_home_daily_free_audio_contract(guest_home):
    audio = guest_home["dailyFreeAudio"]

    assert {"planetSlug", "planetName", "variants"} <= audio.keys()
    assert isinstance(audio["planetSlug"], str) and audio["planetSlug"].strip()
    assert isinstance(audio["planetName"], str) and audio["planetName"].strip()
    assert isinstance(audio["variants"], list) and audio["variants"]

    for variant in audio["variants"]:
        assert {"variant", "title", "audioUrl", "durationSeconds"} <= variant.keys()
        assert variant["audioUrl"].startswith("https://")
        assert isinstance(variant["durationSeconds"], int) and variant["durationSeconds"] > 0

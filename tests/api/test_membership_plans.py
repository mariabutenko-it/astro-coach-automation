from decimal import Decimal, InvalidOperation
from uuid import UUID

import pytest

from config.endpoints import MEMBERSHIP_PLANS

ALLOWED_INTERVALS = {"LIFETIME", "MONTHLY", "QUARTERLY", "YEARLY"}
REQUIRED_PLAN_FIELDS = {
    "id",
    "name",
    "planId",
    "interval",
    "amount",
    "amountUsd",
    "currency",
    "kcTopUp",
    "allowances",
    "perks",
}


def get_plans(api_client, language=None):
    headers = {"Accept-Language": language} if language else None
    response = api_client.get(MEMBERSHIP_PLANS, headers=headers)

    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"].startswith("application/json")

    response_data = response.json()
    assert response_data["success"] is True
    assert isinstance(response_data["data"], list)
    assert response_data["data"], "Membership plans must not be empty"

    return response_data["data"]


@pytest.mark.api
@pytest.mark.smoke
def test_membership_plans_contract(api_client):
    plans = get_plans(api_client)

    for plan in plans:
        assert REQUIRED_PLAN_FIELDS <= plan.keys()
        UUID(plan["id"])
        assert isinstance(plan["name"], str) and plan["name"].strip()
        assert isinstance(plan["planId"], str) and plan["planId"].strip()
        assert plan["interval"] in ALLOWED_INTERVALS
        assert plan["currency"] == "RUB"
        assert isinstance(plan["kcTopUp"], int) and plan["kcTopUp"] >= 0
        assert isinstance(plan["allowances"], list)
        assert isinstance(plan["perks"], list)

        try:
            assert Decimal(plan["amount"]) >= 0
            if plan["amountUsd"] is not None:
                assert Decimal(plan["amountUsd"]) >= 0
        except (InvalidOperation, TypeError) as error:
            pytest.fail(f"Invalid price in plan {plan['planId']}: {error}")


@pytest.mark.api
def test_membership_plans_have_no_duplicate_data(api_client):
    plans = get_plans(api_client)

    plan_ids = [plan["planId"] for plan in plans]
    ids = [plan["id"] for plan in plans]
    assert len(plan_ids) == len(set(plan_ids)), "Duplicate planId values found"
    assert len(ids) == len(set(ids)), "Duplicate membership plan IDs found"

    for plan in plans:
        allowance_keys = [item["actionType"] for item in plan["allowances"]]
        perk_keys = [item["perkKey"] for item in plan["perks"]]
        assert len(allowance_keys) == len(set(allowance_keys)), (
            f"Duplicate allowances found in plan {plan['planId']}"
        )
        assert len(perk_keys) == len(set(perk_keys)), (
            f"Duplicate perks found in plan {plan['planId']}"
        )


@pytest.mark.api
def test_membership_plans_support_english_localization(api_client):
    default_plans = get_plans(api_client)
    english_plans = get_plans(api_client, language="en")

    default_by_id = {plan["planId"]: plan for plan in default_plans}
    english_by_id = {plan["planId"]: plan for plan in english_plans}

    assert default_by_id.keys() == english_by_id.keys()
    assert any(
        default_by_id[plan_id]["name"] != english_by_id[plan_id]["name"]
        for plan_id in default_by_id
    ), "Accept-Language=en did not localize any membership plan name"


@pytest.mark.api
def test_membership_plans_fallback_for_unsupported_language(api_client):
    response = api_client.get(
        MEMBERSHIP_PLANS,
        headers={"Accept-Language": "xx-INVALID"},
    )

    assert response.status_code == 200
    assert response.json()["data"], "Fallback response must contain plans"

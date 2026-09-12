import pytest

from config.endpoints import (
    astro_program_affirmation,
    astro_program_enroll,
    astro_program_task_complete,
    astro_program_task_player,
    kc_store_item_purchase,
)

PROGRAM_ID = "00000000-0000-0000-0000-000000000001"
TASK_ID = "00000000-0000-0000-0000-000000000002"


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    "endpoint",
    [
        astro_program_enroll(PROGRAM_ID),
        astro_program_task_complete(PROGRAM_ID, TASK_ID),
    ],
    ids=["enroll-program", "complete-program-task"],
)
def test_program_state_changes_require_authorization(api_client, endpoint):
    response = api_client.post(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint


@pytest.mark.api
@pytest.mark.security
@pytest.mark.parametrize(
    ("method", "endpoint"),
    [
        ("get", astro_program_task_player(PROGRAM_ID, TASK_ID)),
        ("post", kc_store_item_purchase(PROGRAM_ID)),
        ("delete", astro_program_affirmation(PROGRAM_ID, TASK_ID)),
    ],
    ids=["program-task-player", "kc-store-purchase", "delete-affirmation"],
)
def test_private_media_and_personal_actions_require_authorization(
    api_client,
    method,
    endpoint,
):
    response = getattr(api_client, method)(endpoint)

    assert response.status_code == 401, response.text
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "Unauthorized"
    assert body["path"] == endpoint

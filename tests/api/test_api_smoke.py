import pytest
import allure

from config.endpoints import HEALTH


@pytest.mark.api
@allure.feature("API")
@allure.story("Health check")
def test_get_request(api_client):

    with allure.step("Send GET request to health endpoint"):
        response = api_client.get(HEALTH)

    with allure.step("Attach response body"):
        allure.attach(
            response.text,
            name="API response",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Verify response status code is 200"):
        assert response.status_code == 200

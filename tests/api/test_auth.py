import pytest
import allure

from config.endpoints import AUTH_SEND_OTP


@pytest.mark.api
def test_send_otp(api_client):

    with allure.step("Send OTP request"):
        response = api_client.post(
            AUTH_SEND_OTP,
            data={
                "email": "user@example.com"
            }
        )

    print("STATUS:", response.status_code)
    print("URL:", response.url)
    print("BODY:", response.text)

    with allure.step("Attach response body"):
        allure.attach(
            response.text,
            name="API response",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Verify response status code"):
        assert response.status_code == 200

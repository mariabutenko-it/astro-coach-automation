import pytest

from utils.schema_validator import validate_schema


@pytest.mark.api
def test_api_response_schema():

    response_data = {
        "status": "ok"
    }

    validate_schema(
        response_data,
        "schemas/health_schema.json"
    )

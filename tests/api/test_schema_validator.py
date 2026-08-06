from utils.schema_validator import validate_schema


def test_health_schema():

    response = {
        "status": "ok"
    }

    validate_schema(
        response,
        "schemas/health_schema.json"
    )

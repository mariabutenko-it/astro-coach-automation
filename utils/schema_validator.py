import json
from jsonschema import validate


def validate_schema(data, schema_path):

    with open(schema_path, "r") as file:
        schema = json.load(file)

    validate(
        instance=data,
        schema=schema
    )

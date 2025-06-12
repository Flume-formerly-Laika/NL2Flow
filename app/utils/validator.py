import json
from jsonschema import validate

with open("app/schemas/email_flow_schema.json") as f:
    schema = json.load(f)

def validate_flow(flow):
    validate(instance=flow, schema=schema)

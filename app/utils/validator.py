'''
@file validator.py
@brief Validates email flow against JSON schema
@author Huy Le (huyisme-005)
'''

# import json for loading JSON schema
import json

# import jsonschema for validation
from jsonschema import validate

# Load the JSON schema for email flow validation
with open("app/schemas/email_flow_schema.json") as f:
    schema = json.load(f)


def validate_flow(flow):
    """
    @brief Validates the email flow against the JSON schema
    @param flow the email flow to validate
    """
    validate(instance=flow, schema=schema)

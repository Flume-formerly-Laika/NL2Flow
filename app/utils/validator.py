'''
@file validator.py
@brief Validates email flow against JSON schema
@author Huy Le (huyisme-005)
'''

# import json for loading JSON schema
import json

# import jsonschema for validation
from jsonschema import validate

"""
/**
 * @var schema
 * @brief Loaded JSON schema for email flow validation
 * @type dict
 * @details Schema defines the required structure for automation flow JSON
 */
"""
# Load the JSON schema for email flow validation
with open("app/schemas/email_flow_schema.json") as f:
    schema = json.load(f)


def validate_flow(flow):

    """
    /**
     * @brief Validates the email flow against the predefined JSON schema
     * @param flow The email flow dictionary to validate
     * @return None
     * @throws ValidationError if the flow doesn't match the schema
     * @details Uses jsonschema library to ensure flow structure is correct
     */
    """
    
    validate(instance=flow, schema=schema)

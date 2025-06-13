"""
/**
 * @file field_mapper.py
 * @brief Maps field names using a simple dictionary approach
 * @author Huy Le (huyisme-005)
 */
"""

# Simple field mapping dictionary to replace PyKE complexity
FIELD_MAPPINGS = {
    "name": "first_name",
    "email": "user_email", 
    "signup_date": "registration_date"
}

def map_fields(field_dict: dict) -> dict:
    """
    @brief Maps field names using predefined mapping rules
    @param field_dict Dictionary of field names and their source values
    @return dict Dictionary with mapped field names and values
    @throws None (falls back to source value on error)
    """
    result = {}
    for key, value in field_dict.items():
        # Use mapped name if available, otherwise use original key
        mapped_key = FIELD_MAPPINGS.get(key, key)
        result[mapped_key] = value
    return result
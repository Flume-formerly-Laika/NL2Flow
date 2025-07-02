"""
/**
 * @file field_mapper.py
 * @brief Maps field names using a simple dictionary approach
 * @author Huy Le (huyisme-005)
 */
"""

# Enhanced field mapping dictionary to handle more scenarios
FIELD_MAPPINGS = {
    "name": "first_name",
    "email": "user_email", 
    "signup_date": "registration_date",
    "order_id": "order_id",
    "order_date": "order_date",
    "order_total": "order_total",
    "customer_name": "first_name",
    "customer_email": "user_email",
    "user_name": "first_name",
    "username": "first_name",
    "user_id": "user_id",
    "product_name": "product_name",
    "quantity": "quantity",
    "price": "price",
    "total": "order_total",
    "phone": "phone_number",
    "address": "address"
}

def map_fields(field_dict: dict) -> dict:
    """
    @brief Maps field names using predefined mapping rules
    @param field_dict Dictionary of field names and their source values
    @return dict Dictionary with mapped field names and values
    @throws None (falls back to source value on error)
    """
    result = {}
    
    # Ensure we always have basic required fields
    has_name = False
    has_email = False
    
    for key, value in field_dict.items():
        # Use mapped name if available, otherwise use original key
        mapped_key = FIELD_MAPPINGS.get(key, key)
        result[mapped_key] = value
        
        # Track if we have essential fields
        if mapped_key in ["first_name", "name"]:
            has_name = True
        if mapped_key in ["user_email", "email"]:
            has_email = True
    
    # Add default fields if missing
    if not has_name:
        result["first_name"] = "user.name"
    if not has_email:
        result["user_email"] = "user.email"
    
    return result
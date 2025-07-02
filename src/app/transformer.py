"""
@file transformer.py
@brief Transforms GPT intent into structured flow JSON
@author Huy Le (huyisme-005)
"""

from app.rules.field_mapper import map_fields

def build_flow_json(intent: dict) -> dict:
    """
    @brief Builds the flow JSON from extracted intent
    @param intent Dictionary containing trigger and actions from GPT
    @return dict Structured flow JSON
    @raises ValueError if intent structure is invalid
    """
    
    # Validate intent structure
    if not isinstance(intent, dict):
        raise ValueError("Intent must be a dictionary")
    
    # Get trigger with fallback
    trigger_type = intent.get("trigger", "user_signup")
    
    # Get actions with fallback
    actions = intent.get("actions", [])
    if not actions:
        # Create default action if none provided
        actions = [{
            "type": "send_email",
            "template": "notification",
            "fields": {"name": "user.name", "email": "user.email"}
        }]
    
    # Get the first action
    first_action = actions[0]
    if not isinstance(first_action, dict):
        raise ValueError("First action must be a dictionary")
    
    # Extract fields with fallback
    raw_fields = first_action.get("fields", {"name": "user.name", "email": "user.email"})
    
    # Ensure we have at least basic fields
    if "name" not in raw_fields and "email" not in raw_fields:
        raw_fields.update({"name": "user.name", "email": "user.email"})
    
    # Map fields using the field mapper
    mapped_fields = map_fields(raw_fields)
    
    # Get template name with fallback
    template_name = first_action.get("template", "notification")
    
    # Build the params dictionary with proper templating
    params = {}
    for key, val in mapped_fields.items():
        # Clean up the value and ensure proper templating
        clean_val = str(val).strip()
        
        # If the value already contains template syntax, use it as-is
        if "{{" in clean_val and "}}" in clean_val:
            params[key] = clean_val
        else:
            # Remove 'user.' prefix if present and add proper template syntax
            clean_val = clean_val.replace("user.", "")
            # Handle different possible prefixes
            if clean_val.startswith("order."):
                clean_val = clean_val.replace("order.", "order.")
            elif not clean_val.startswith(("user.", "order.", "system.")):
                # Default to user prefix for most fields
                clean_val = f"user.{clean_val}"
            
            params[key] = f"{{{{ {clean_val} }}}}"
    
    return {
        "flow": {
            "trigger": {
                "event": trigger_type
            },
            "actions": [
                {
                    "action_type": "send_email",
                    "template_id": template_name,
                    "params": params
                }
            ]
        }
    }
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
    
    actions = intent.get("actions", [])
    if not actions:
        raise ValueError("Intent must contain at least one action")
    
    if not isinstance(actions[0], dict) or "fields" not in actions[0]:
        raise ValueError("First action must contain 'fields' key")
    
    # Extract and map fields
    raw_fields = actions[0]["fields"]
    mapped_fields = map_fields(raw_fields)
    
    # Get template name, default to 'welcome' if not specified
    template_name = actions[0].get("template", "welcome")
    
    # Get trigger type, default to 'user_signup' if not specified
    trigger_type = intent.get("trigger", "user_signup")
    
    return {
        "flow": {
            "trigger": {
                "event": trigger_type
            },
            "actions": [
                {
                    "action_type": "send_email",
                    "template_id": template_name,
                    "params": {
                        key: f"{{{{ user.{val.replace('user.', '')} }}}}" 
                        for key, val in mapped_fields.items()
                    }
                }
            ]
        }
    }
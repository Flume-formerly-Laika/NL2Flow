from app.rules.field_mapper import map_fields

def build_flow_json(intent):
    raw_fields = intent["actions"][0]["fields"]
    mapped_fields = map_fields(raw_fields)

    return {
        "flow": {
            "trigger": {
                "event": "user_signup"
            },
            "actions": [
                {
                    "action_type": "send_email",
                    "template_id": intent["actions"][0]["template"],
                    "params": {
                        key: f"{{{{ user.{val} }}}}" for key, val in mapped_fields.items()
                    }
                }
            ]
        }
    }

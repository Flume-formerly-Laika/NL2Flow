from app.transformer import build_flow_json

def test_build_flow_json():
    intent = {
        "trigger": "user_signup",
        "actions": [{"type": "send_email", "template": "welcome", "fields": {"name": "user.name", "email": "user.email"}}]
    }
    flow = build_flow_json(intent)
    assert flow["flow"]["trigger"]["event"] == "user_signup"
    assert "send_email" in flow["flow"]["actions"][0]["action_type"]

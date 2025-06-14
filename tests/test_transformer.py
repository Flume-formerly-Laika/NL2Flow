"""
/**
 * @file test_transformer.py
 * @brief Unit tests for the transformer module functionality
 * @author Huy Le (huyisme-005)
 */
"""

from app.transformer import build_flow_json

def test_build_flow_json():

    """
    /**
     * @brief Tests the build_flow_json function with sample intent data
     * @return None
     * @throws AssertionError if the flow transformation fails
     * @details Verifies that intent data is properly transformed into flow JSON structure
     */
    """

    intent = {
        "trigger": "user_signup",
        "actions": [{"type": "send_email", "template": "welcome", "fields": {"name": "user.name", "email": "user.email"}}]
    }
    flow = build_flow_json(intent)
    assert flow["flow"]["trigger"]["event"] == "user_signup"
    assert "send_email" in flow["flow"]["actions"][0]["action_type"]

"""
/**
 * @file gpt_handler.py
 * @brief Handles Gemini API interactions for extracting structured automation flows
 * @author Huy Le (huyisme-005)
 */
"""

import os
import logging
import json
import google.generativeai as genai

SYSTEM_PROMPT = """You are an AI that extracts structured automation flows from user requests.
Return ONLY a valid JSON object with this exact structure:
{
  "trigger": "trigger_event_name",
  "actions": [
    {
      "type": "send_email",
      "template": "template_name",
      "fields": {
        "name": "user.name",
        "email": "user.email"
      }
    }
  ]
}
Important rules:
- Always return valid JSON
- Use common field names like name, email, signup_date, order_id, etc.
- Template should be descriptive (welcome, confirmation, reminder, notification, etc.)
- Trigger should match the event type:
  * user_signup - when users register/sign up
  * order_placed - when customers place orders
  * payment_received - when payments are processed
  * profile_updated - when users update profiles
  * subscription_started - when users subscribe
- Always include at least name and email fields
- For order-related requests, also include order-related fields
"""

def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your-google-api-key-here":
        raise ValueError("Google API key not configured. Please set GOOGLE_API_KEY in your .env file")
    model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def build_prompt(user_input: str) -> str:
    return f"{SYSTEM_PROMPT}\nConvert this request to automation flow: {user_input}"

async def extract_intent(user_input: str) -> dict:
    try:
        model = get_gemini_client()
        prompt = build_prompt(user_input)
        response = model.generate_content(prompt)
        content = response.text.strip()
        try:
            result = json.loads(content)
            logging.info(f"Successfully parsed Gemini response: {result}")
            # (same validation/fallback logic as before)
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            if "trigger" not in result:
                result["trigger"] = "user_signup"
            if "actions" not in result or not result["actions"]:
                result["actions"] = [{
                    "type": "send_email",
                    "template": "notification",
                    "fields": {"name": "user.name", "email": "user.email"}
                }]
            first_action = result["actions"][0]
            if "type" not in first_action:
                first_action["type"] = "send_email"
            if "template" not in first_action:
                first_action["template"] = "notification"
            if "fields" not in first_action:
                first_action["fields"] = {"name": "user.name", "email": "user.email"}
            return result
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Gemini response as JSON: {content}")
            raise ValueError(f"Gemini returned invalid JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Gemini API call failed: {str(e)}")
        # (same fallback as before)
        fallback_trigger = "user_signup"
        fallback_template = "welcome"
        fallback_fields = {"name": "user.name", "email": "user.email"}
        user_lower = user_input.lower()
        if any(word in user_lower for word in ["order", "purchase", "buy", "customer"]):
            fallback_trigger = "order_placed"
            fallback_template = "confirmation"
            fallback_fields = {
                "name": "user.name",
                "email": "user.email",
                "order_id": "order.id"
            }
        elif any(word in user_lower for word in ["remind", "reminder"]):
            fallback_template = "reminder"
        elif any(word in user_lower for word in ["confirm", "confirmation"]):
            fallback_template = "confirmation"
        return {
            "trigger": fallback_trigger,
            "actions": [
                {
                    "type": "send_email",
                    "template": fallback_template,
                    "fields": fallback_fields
                }
            ]
        }
"""
/**
 * @file gpt_handler.py
 * @brief Handles GPT API interactions for extracting structured automation flows
 * @author Huy Le (huyisme-005)
 */
"""

# OpenAI library for interacting with GPT models and making API calls
from openai import OpenAI
import os
import logging

# JSON library for parsing and handling JSON data from GPT responses
import json

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file")
    return OpenAI(api_key=api_key)

"""
/**
 * @var SYSTEM_PROMPT
 * @brief System prompt used to instruct the GPT model
 * @type str
 */
"""
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
- For order-related requests, also include order-related fields"""

def build_prompt(user_input: str) -> list:
    """
    /**
     * @brief Builds the prompt structure for GPT API
     * @param user_input The user's input text to process
     * @return list A list of message dictionaries containing system and user prompts
     * @throws None
     */
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Convert this request to automation flow: {user_input}"}
    ]

async def extract_intent(user_input: str) -> dict:
    """
    /**
     * @brief Extracts structured automation flow from user input using GPT
     * @param user_input The user's input text to process
     * @return dict The structured automation flow extracted from the input
     * @throws Exception If there's an error in API call or response parsing
     */
    """
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=build_prompt(user_input),
            temperature=0.2,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        try:
            result = json.loads(content)
            logging.info(f"Successfully parsed GPT response: {result}")
            
            # Validate the structure and provide defaults if needed
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")
            
            # Ensure we have required fields
            if "trigger" not in result:
                result["trigger"] = "user_signup"
            
            if "actions" not in result or not result["actions"]:
                result["actions"] = [{
                    "type": "send_email",
                    "template": "notification",
                    "fields": {"name": "user.name", "email": "user.email"}
                }]
            
            # Ensure first action has required fields
            first_action = result["actions"][0]
            if "type" not in first_action:
                first_action["type"] = "send_email"
            if "template" not in first_action:
                first_action["template"] = "notification"
            if "fields" not in first_action:
                first_action["fields"] = {"name": "user.name", "email": "user.email"}
            
            return result
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse GPT response as JSON: {content}")
            raise ValueError(f"GPT returned invalid JSON: {str(e)}")
            
    except ValueError:
        # Re-raise ValueError (API key issues, JSON parsing)
        raise
    except Exception as e:
        logging.error(f"GPT API call failed: {str(e)}")
        # Fallback response if API fails
        logging.info("Using fallback response due to API failure")
        
        # Create a context-aware fallback based on user input
        fallback_trigger = "user_signup"
        fallback_template = "welcome"
        fallback_fields = {"name": "user.name", "email": "user.email"}
        
        # Simple keyword detection for better fallbacks
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
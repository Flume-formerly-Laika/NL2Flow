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
  "trigger": "user_signup",
  "actions": [
    {
      "type": "send_email",
      "template": "welcome",
      "fields": {
        "name": "user.name",
        "email": "user.email",
        "signup_date": "user.signup_date"
      }
    }
  ]
}

Important rules:
- Always return valid JSON
- Use common field names like name, email, signup_date
- Template should be descriptive (welcome, confirmation, reminder, etc.)
- Trigger should match the event type (user_signup, order_placed, etc.)"""

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
        return {
            "trigger": "user_signup",
            "actions": [
                {
                    "type": "send_email",
                    "template": "welcome",
                    "fields": {
                        "name": "user.name",
                        "email": "user.email",
                        "signup_date": "user.signup_date"
                    }
                }
            ]
        }
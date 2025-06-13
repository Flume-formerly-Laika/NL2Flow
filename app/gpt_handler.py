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

# JSON library for parsing and handling JSON data from GPT responses
import json

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
/**
 * @var SYSTEM_PROMPT
 * @brief System prompt used to instruct the GPT model
 * @type str
 */
"""
SYSTEM_PROMPT = """You are an AI that extracts structured automation flows from user requests. 
Return a JSON object with this structure:
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
}"""

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
        {"role": "user", "content": user_input}
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
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=build_prompt(user_input),
            temperature=0.2
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        # Fallback response if API fails
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
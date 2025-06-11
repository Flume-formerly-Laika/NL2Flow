import openai
import json

SYSTEM_PROMPT = "You are an AI that extracts structured automation flows from user requests."

def build_prompt(user_input: str):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

async def extract_intent(user_input: str):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=build_prompt(user_input),
        temperature=0.2
    )
    return json.loads(response["choices"][0]["message"]["content"])

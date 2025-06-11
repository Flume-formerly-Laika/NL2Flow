from pydantic import BaseModel

class NLRequest(BaseModel):
    user_input: str

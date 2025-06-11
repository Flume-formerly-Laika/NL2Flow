"""
/**
 * @file models.py
 * @brief Contains Pydantic models for request/response validation
 * @author Huy Le (huyisme-005)
 */

"""
# Imports BaseModel from pydantic for data validation

from pydantic import BaseModel
class NLRequest(BaseModel):
    """
    Pydantic model for natural language request validation.
    
    Attributes:
        user_input (str): The natural language input from the user
    """
    user_input: str

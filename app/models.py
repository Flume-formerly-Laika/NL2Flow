"""
/**
 * @file models.py
 * @brief Contains Pydantic models for request/response validation
 * @author Huy Le (huyisme-005)
 */

"""
# Imports BaseModel from pydantic for data validation

from pydantic import BaseModel

from typing import Any, Dict

class NLRequest(BaseModel):
    """
    Pydantic model for natural language request validation.
    
    Attributes:
        user_input (str): The natural language input from the user
    """
    user_input: str

class FlowResponse(BaseModel):
    """
    /**
     * @class FlowResponse
     * @brief Pydantic model for API response validation
     * @details Ensures responses contain both trace ID and flow structure
     */
    """
    trace_id: str
    """
    /**
     * @var trace_id
     * @brief Unique identifier for request tracking
     * @type str
     */
    """
    
    flow: Dict[str, Any]
    """
    /**
     * @var flow
     * @brief The generated automation flow structure
     * @type Dict[str, Any]
     */
    """

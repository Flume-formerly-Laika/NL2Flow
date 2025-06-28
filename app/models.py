"""
/**
 * @file models.py
 * @brief Contains Pydantic models for request/response validation
 * @author Huy Le (huyisme-005)
 */

"""
# Imports BaseModel from pydantic for data validation

from pydantic import BaseModel, Field

from typing import Any, Dict, List, Optional

class NLRequest(BaseModel):
    """
    Pydantic model for natural language request validation.
    
    Attributes:
        user_input (str): The natural language input from the user
    """
    user_input: str = Field(..., min_length=1, description="The natural language input from the user (cannot be empty)")

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

class DeleteSnapshotRequest(BaseModel):
    """
    Pydantic model for deleting a specific schema snapshot.
    
    Attributes:
        api_name (str): The name of the API
        timestamp (int): The timestamp of the snapshot to delete
        endpoint (Optional[str]): Optional endpoint filter
        method (Optional[str]): Optional HTTP method filter
    """
    api_name: str = Field(..., description="The name of the API")
    timestamp: int = Field(..., description="The timestamp of the snapshot to delete")
    endpoint: Optional[str] = Field(None, description="Optional endpoint filter")
    method: Optional[str] = Field(None, description="Optional HTTP method filter")

class DeleteAPIRequest(BaseModel):
    """
    Pydantic model for deleting all snapshots for an API.
    
    Attributes:
        api_name (str): The name of the API to delete all snapshots for
    """
    api_name: str = Field(..., description="The name of the API to delete all snapshots for")

class ListAPIResponse(BaseModel):
    """
    Pydantic model for listing APIs response.
    
    Attributes:
        api_names (List[str]): List of available API names
        total_count (int): Total number of APIs
    """
    api_names: List[str] = Field(..., description="List of available API names")
    total_count: int = Field(..., description="Total number of APIs")

class APIVersionInfo(BaseModel):
    """
    Pydantic model for API version information.
    
    Attributes:
        timestamp (str): The timestamp of the version
        endpoints_count (int): Number of endpoints in this version
        methods (List[str]): List of HTTP methods used
        source_url (Optional[str]): Source URL of the API documentation
        auth_type (Optional[str]): Authentication type used
    """
    timestamp: str = Field(..., description="The timestamp of the version")
    endpoints_count: int = Field(..., description="Number of endpoints in this version")
    methods: List[str] = Field(..., description="List of HTTP methods used")
    source_url: Optional[str] = Field(None, description="Source URL of the API documentation")
    auth_type: Optional[str] = Field(None, description="Authentication type used")

class ListVersionsResponse(BaseModel):
    """
    Pydantic model for listing API versions response.
    
    Attributes:
        api_name (str): The name of the API
        versions (List[APIVersionInfo]): List of version information
        total_count (int): Total number of versions
    """
    api_name: str = Field(..., description="The name of the API")
    versions: List[APIVersionInfo] = Field(..., description="List of version information")
    total_count: int = Field(..., description="Total number of versions")

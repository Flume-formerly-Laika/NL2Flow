'''
@file logger.py
@brief Logs the request and user input
@author Huy Le (huyisme-005)
'''

#import uuid for trace ID generation
import uuid

#import logging for logging
import logging


def log_request(request, user_input):

    """
    /**
     * @brief Logs the request and user input with a unique trace ID
     * @param request The FastAPI request object containing URL and other metadata
     * @param user_input The user's natural language input string
     * @return str The unique trace ID for the request
     * @throws None
     * @details Generates a UUID for request tracking and logs the request path and input
     */
    """
    
    trace_id = str(uuid.uuid4())
    logging.info(f"Trace ID: {trace_id} | Path: {request.url.path} | Input: {user_input}")
    return trace_id

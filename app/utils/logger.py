'''
@file logger.py
@brief Logs the request and user input
@author Huy Le (huyisme-005)
'''

#import uuid for trace ID
import uuid

#import logging for logging
import logging


def log_request(request, user_input):
    '''
@brief Logs the request and user input
@param request The request object
@param user_input THe user's input
@return trace_id The trace ID for the request
'''
    trace_id = str(uuid.uuid4())
    logging.info(f"Trace ID: {trace_id} | Path: {request.url.path} | Input: {user_input}")
    return trace_id

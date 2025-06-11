# NL2Flow: Natural Language to Automation Flow Generator

This project converts natural language automation requests into structured flow definitions using GPT-4 Turbo, FastAPI, and Pyke for rule-based field mapping.

## Features
- Natural language input via REST API
- GPT-4 Turbo intent extraction
- Field mapping via Pyke rules engine
- Validated JSON flow output

## Run
```bash
pip install -r requirements.txt
./run.sh
```

##API Example
Request
POST /parse-request
{
  "user_input": "When a new user signs up, send a welcome email with their name and signup date."
}

Response
{
  "trace_id": "uuid-1234",
  "flow": { ... }
}


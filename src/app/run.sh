#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include the project root
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Change to project directory
cd "$SCRIPT_DIR"

# Load environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
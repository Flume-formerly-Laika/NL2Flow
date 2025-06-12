#!/bin/bash
cd "$(dirname "$0")"  # Ensure script runs in project root
uvicorn app.main:app --reload

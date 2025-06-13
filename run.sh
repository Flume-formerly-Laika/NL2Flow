#!/bin/bash
cd "$(dirname "$0")"  # Ensure script runs in project root
python scripts/compile_pyke_rules.py
uvicorn app.main:app --reload

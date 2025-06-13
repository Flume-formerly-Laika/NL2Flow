# NL2Flow: Natural Language to Automation Flow Generator

This project converts natural language automation requests into structured flow definitions using GPT-4 Turbo, FastAPI, and simplified field mapping.

## Features
- Natural language input via REST API
- GPT-4 Turbo intent extraction
- Field mapping via dictionary rules
- Validated JSON flow output
- Cross-platform support (Windows PowerShell, Command Prompt, Unix/Linux)

## Quick Setup

### For Windows PowerShell Users:
```powershell
# Run the setup script
.\setup.ps1

# Edit the .env file to add your OpenAI API key
notepad .env

# Start the application
.\run.ps1
```

### For Windows Command Prompt Users:
```cmd
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env file
copy .env.example .env
notepad .env

# Start the application
run.bat
```

### For Unix/Linux/macOS Users:
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit .env file
cp .env.example .env
nano .env

# Make script executable and run
chmod +x run.sh
./run.sh
```

## Configuration

1. **Get an OpenAI API key** from https://platform.openai.com/api-keys
2. **Edit the `.env` file** and replace `your_openai_api_key_here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

## API Usage

The server runs on `http://localhost:8000`

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

### Example Request
```bash
POST http://localhost:8000/parse-request
Content-Type: application/json

{
  "user_input": "When a new user signs up, send a welcome email with their name and signup date."
}
```

### Example Response
```json
{
  "trace_id": "uuid-1234-5678-9abc",
  "flow": {
    "flow": {
      "trigger": {
        "event": "user_signup"
      },
      "actions": [
        {
          "action_type": "send_email",
          "template_id": "welcome",
          "params": {
            "first_name": "{{ user.user.name }}",
            "user_email": "{{ user.user.email }}",
            "registration_date": "{{ user.user.signup_date }}"
          }
        }
      ]
    }
  }
}
```

## Testing

Run tests with:
```bash
# Install test dependencies (if not already installed)
pip install pytest httpx

# Run tests
pytest tests/
```

## Project Structure

```
nl2flow/
├── .env                 # Environment configuration
├── setup.ps1           # PowerShell setup script
├── run.ps1             # PowerShell run script
├── run.bat             # Windows batch run script
├── run.sh              # Unix/Linux run script
├── requirements.txt    # Python dependencies
├── app/
│   ├── main.py         # FastAPI application
│   ├── gpt_handler.py  # OpenAI GPT integration
│   ├── models.py       # Pydantic models
│   ├── transformer.py  # Flow JSON builder
│   ├── rules/
│   │   └── field_mapper.py  # Field mapping logic
│   ├── schemas/
│   │   └── email_flow_schema.json  # JSON schema
│   └── utils/
│       ├── logger.py   # Request logging
│       └── validator.py # Flow validation
└── tests/
    ├── test_main.py    # API tests
    └── test_transformer.py  # Transform tests
```

## Troubleshooting

### PowerShell Execution Policy
If you get an execution policy error in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found
Make sure Python 3.8+ is installed and in your PATH:
- Download from https://python.org/downloads/
- During installation, check "Add Python to PATH"

### OpenAI API Errors
- Ensure your API key is correct in the `.env` file
- Check your OpenAI account has credits/billing set up
- The application includes fallback responses if the API is unavailable

### Port Already in Use
If port 8000 is busy, modify the run scripts to use a different port:
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## License

MIT License - see LICENSE file for details.
# PowerShell script to run the NL2Flow application

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Set PYTHONPATH to include the project root
$env:PYTHONPATH = "$ScriptDir;$env:PYTHONPATH"

# Change to project directory
Set-Location $ScriptDir

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env file..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
            Write-Host "Set $name"
        }
    }
}

# Check if OpenAI API key is set
if (-not $env:OPENAI_API_KEY) {
    Write-Warning "OPENAI_API_KEY not found in environment variables. Please set it in the .env file."
}

Write-Host "Starting FastAPI server..."
Write-Host "Server will be available at: http://localhost:8000"
Write-Host "API documentation at: http://localhost:8000/docs"
Write-Host "Press Ctrl+C to stop the server"

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
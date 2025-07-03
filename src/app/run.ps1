# PowerShell script to run the NL2Flow application

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Set PYTHONPATH to include the project root
$env:PYTHONPATH = "$ScriptDir;$env:PYTHONPATH"

# Change to project directory
Set-Location $ScriptDir

# Check if python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in PATH"
    exit 1
}

# Check if uvicorn is installed
try {
    uvicorn --version 2>&1 | Out-Null
    Write-Host "Uvicorn is available" -ForegroundColor Green
} catch {
    Write-Error "Uvicorn is not installed. Run: pip install uvicorn"
    exit 1
}

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "Set $name" -ForegroundColor Green
        }
    }
} else {
    Write-Warning ".env file not found. Creating a template..."
    @"
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
PYTHONPATH=.
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Warning "Please edit .env file and add your OpenAI API key"
}

# Check if OpenAI API key is set
if (-not $env:OPENAI_API_KEY -or $env:OPENAI_API_KEY -eq "your_openai_api_key_here") {
    Write-Warning "OPENAI_API_KEY not properly configured in .env file"
    Write-Host "The server will start but API calls may fail" -ForegroundColor Yellow
}

# Verify the main module exists
if (-not (Test-Path "src/app/main.py")) {
    Write-Error "src/app/main.py not found. Make sure you're in the correct directory."
    exit 1
}

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health check at: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the FastAPI server with error handling
try {
    uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Error "Failed to start the server. Error: $_"
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "1. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "2. Check if port 8000 is already in use" -ForegroundColor White
    Write-Host "3. Verify Python path and module structure" -ForegroundColor White
}
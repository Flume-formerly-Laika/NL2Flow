# PowerShell setup script for NL2Flow

Write-Host "Setting up NL2Flow project..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8+ and try again."
    exit 1
}

# Check if pip is available
try {
    pip --version | Out-Null
    Write-Host "pip is available" -ForegroundColor Green
} catch {
    Write-Error "pip is not available. Please ensure pip is installed."
    exit 1
}

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements. Please check the error messages above."
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
PYTHONPATH=.
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Created .env file. Please edit it and add your OpenAI API key." -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

# Check if OPENAI_API_KEY is set
if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    $apiKeyLine = $envContent | Where-Object { $_ -match "^OPENAI_API_KEY=" }
    if ($apiKeyLine -and $apiKeyLine -notmatch "your_openai_api_key_here") {
        Write-Host "OpenAI API key appears to be configured" -ForegroundColor Green
    } else {
        Write-Warning "Please edit the .env file and add your OpenAI API key"
    }
}

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  PowerShell: .\run.ps1" -ForegroundColor White
Write-Host "  Command Prompt: run.bat" -ForegroundColor White
Write-Host "`nMake sure to add your OpenAI API key to the .env file first!" -ForegroundColor Yellow
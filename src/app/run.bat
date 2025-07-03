@echo off
REM Windows batch script to run the NL2Flow application

REM Get the directory where the batch file is located
set SCRIPT_DIR=%~dp0

REM Set PYTHONPATH to include the project root
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Change to project directory
cd /d "%SCRIPT_DIR%"

REM Load environment variables from .env file if it exists
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
            echo Set %%a
        )
    )
)

REM Check if OpenAI API key is set
if "%OPENAI_API_KEY%"=="" (
    echo WARNING: OPENAI_API_KEY not found in environment variables. Please set it in the .env file.
)

echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server

REM Start the FastAPI server
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
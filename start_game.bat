@echo off
cd /d "%~dp0"

set MODEL=qwen3:1.7b

where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama is not installed or not found.
    echo Please install Ollama first.
    pause
    exit /b
)

echo Starting Ollama server...
start "" /min ollama serve

echo Waiting for Ollama...
timeout /t 3 >nul

echo Checking if %MODEL% is installed...
ollama list | findstr /C:"%MODEL%" >nul

if errorlevel 1 (
    echo Model not found. Downloading %MODEL%...
    ollama pull %MODEL%
) else (
    echo Model already installed.
)

echo Starting LLM Mystery Game...
.\.venv\Scripts\python.exe main.py

pause
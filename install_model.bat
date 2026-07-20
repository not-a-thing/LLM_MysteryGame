@echo off
cd /d "%~dp0"

set MODEL=llama3.2:3b

where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama is not installed or not found.
    echo Please install Ollama first.
    pause
    exit /b
)

echo Downloading %MODEL%...
ollama pull %MODEL%

echo Done. You do not need to run this again unless you change model.
pause
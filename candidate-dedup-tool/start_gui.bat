@echo off
REM Startup script for Candidate Deduplication Tool GUI (Windows)

echo ===================================
echo Candidate Deduplication Tool - GUI
echo ===================================
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ^>^> Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ^>^> Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ^>^> Installing dependencies...
    pip install -r requirements.txt
)

REM Check if PyQt5 is installed
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo ^>^> PyQt5 not found. Installing...
    pip install PyQt5>=5.15.0
)

echo.
echo ^>^> Starting application...
echo.

REM Run the application
python -m app --debug

echo.
echo Application closed.
pause

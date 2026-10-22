@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting SmartStock...
python run.py
goto :eof

:error
echo.
echo Setup failed. Confirm Python 3.10 or newer is installed and available as "python".
pause
exit /b 1

@echo off
REM Wonderfeed. Double-click this file. Nothing to type.
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Python is not installed.
  echo   Install it from https://www.python.org/downloads/
  echo   Remember to tick "Add Python to PATH" during install.
  echo.
  pause
  exit /b 1
)

if not exist .venv (
  echo.
  echo   First run - setting up. This takes 2-3 minutes.
  echo.
  python -m venv .venv
  .venv\Scripts\pip install --quiet --upgrade pip
  .venv\Scripts\pip install --quiet -r requirements.txt
)

if not exist config\settings.yaml copy /y config\settings.example.yaml config\settings.yaml >nul
if not exist config\products.yaml copy /y config\products.example.yaml config\products.yaml >nul

start "" http://localhost:8501
.venv\Scripts\python -m wonderfeed.netinfo

.venv\Scripts\streamlit run wonderfeed/app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --browser.gatherUsageStats false --logger.level error
pause

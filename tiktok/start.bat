@echo off
REM Wonderfeed desktop. Double-click this file.
cd /d "%~dp0"

if not exist .venv (
  echo First run - setting up...
  python -m venv .venv
  .venv\Scripts\pip install --quiet --upgrade pip
  .venv\Scripts\pip install --quiet -r requirements.txt
)

if not exist config\settings.yaml copy config\settings.example.yaml config\settings.yaml
if not exist config\products.yaml copy config\products.example.yaml config\products.yaml

echo Opening Wonderfeed at http://localhost:8501
.venv\Scripts\streamlit run wonderfeed/app.py

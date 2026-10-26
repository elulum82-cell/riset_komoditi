@echo off
cd /d "%~dp0"
if not exist .venv (
  echo Membuat lingkungan Python...
  python -m venv .venv
  call .venv\Scripts\activate
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate
)
if not exist .env copy .env.example .env >nul
streamlit run app.py
pause

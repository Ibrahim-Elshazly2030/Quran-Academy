@echo off
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo Creating virtual environment...
    python -m venv venv
)

if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
)

venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py collectstatic --noinput
echo Starting Django production-like server on port 8005...
venv\Scripts\python.exe manage.py runserver 0.0.0.0:8005
pause

@echo off
setlocal
title Law Mithra Launcher

echo =====================================================================
echo                     LAW MITHRA LAUNCHER
echo          "Understand the Law. Understand Your Rights."
echo =====================================================================
echo.

cd /d "%~dp0"

REM 1. Ensure Backend Virtual Environment exists
if not exist "backend\.venv\Scripts\activate.bat" (
    echo [*] Setting up backend virtual environment...
    python -m venv backend\.venv
)

REM 2. Ensure Backend Dependencies are installed
if not exist "backend\.venv\Scripts\django-admin.exe" (
    echo [*] Installing backend packages from requirements.txt...
    echo [*] This may take a couple of minutes on first run. Please wait...
    call backend\.venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r backend\requirements.txt
)

REM 3. Ensure Frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo [*] Installing frontend packages...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
)

REM 4. Launch Django Backend
echo [*] Launching Backend (Django REST Framework)...
start "Law Mithra - Backend" cmd /k "cd /d "%~dp0backend" && call .venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000"

REM 5. Launch Frontend (Vite)
echo [*] Launching Frontend (React / Vite)...
start "Law Mithra - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo =====================================================================
echo  Services started in separate terminal windows:
echo  - Frontend Web UI:  http://localhost:5173
echo  - Backend API:      http://127.0.0.1:8000
echo  - API Docs:         http://127.0.0.1:8000/api/docs/
echo =====================================================================
echo.

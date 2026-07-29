@echo off
title KRATOS Automated Launcher and Environment Diagnostic Tool

python -c "from ascii_banner import KRATOS_ASCII_BANNER; print(KRATOS_ASCII_BANNER)" 2>nul || python -c "import sys; sys.path.append('tui'); from ascii_banner import KRATOS_ASCII_BANNER; print(KRATOS_ASCII_BANNER)" 2>nul || echo      __ __    ____     ___       ______   ____     _____    && echo    / //_/   / __ \   /   ^|     /_  __/  / __ \   / ___/    && echo   / ,^<     / /_/ /  / /^| ^|      / /    / / / /   \__ \     && echo  / /^| ^|   / _, _/  / ___ ^|     / /    / /_/ /   ___/ /     && echo /_/ ^|_^|  /_/ ^|_^|  /_/  ^|_^|    /_/     \____/   /____/  - By Dzio
echo ===============================================================================
echo.

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

rem 1. Check or Create Virtual Environment
if not exist "venv\Scripts\activate.bat" goto create_venv
echo [1/4] Python virtual environment (venv) detected.
goto check_deps

:create_venv
echo [1/4] Creating Python virtual environment (venv)...
python -m venv venv
if errorlevel 1 goto venv_fail
echo [SUCCESS] Virtual environment created.
goto check_deps

:venv_fail
echo [ERROR] Failed to create Python virtual environment. Please ensure Python 3.10+ is installed and on your PATH.
pause
exit /b 1

:check_deps
call "%ROOT_DIR%venv\Scripts\activate.bat"

rem 2. Install / Verify Python Backend Requirements
echo [2/4] Verifying Python backend dependencies...
python -c "import fastapi, uvicorn, networkx, rich, textual, reportlab, cv2" >nul 2>&1
if errorlevel 1 goto install_deps
echo [SUCCESS] Backend Python dependencies satisfied.
goto check_env

:install_deps
echo [INFO] Installing/repairing backend dependencies from requirements.txt...
python -m pip install -r backend/requirements.txt
python -m pip install textual
if errorlevel 1 goto deps_fail
goto check_env

:deps_fail
echo [ERROR] Dependency installation failed!
pause
exit /b 1

:check_env
rem 3. Check .env and NVIDIA Credentials
echo [3/4] Checking NVIDIA NIM Credentials...
if exist ".env" (
    echo [INFO] Found .env configuration file.
) else (
    echo [WARNING] .env file not found in project root!
    echo [NOTE] KRATOS will run in OpenCV / String template fallback mode without NIM_API_KEY.
)

rem 4. Check Frontend NPM Dependencies
echo [4/4] Verifying React Frontend Dependencies...
if not exist "frontend\node_modules" goto install_npm
echo [SUCCESS] Frontend npm dependencies verified.
goto select_mode

:install_npm
echo [INFO] Node modules not found in frontend. Installing dependencies via npm...
cd /d "%ROOT_DIR%frontend"
call npm install
cd /d "%ROOT_DIR%"
goto select_mode

:select_mode
echo.
echo ===============================================================================
echo                   SELECT LAUNCH MODE FOR KRATOS SYSTEM
echo ===============================================================================
echo   [1] Terminal User Interface (TUI)
echo   [2] Web Dashboard User Interface (UI)
echo   [3] IDK / Spawn Both (Starts Backend Server, Frontend UI and TUI)
echo ===============================================================================
echo.

set /p MODE_CHOICE="Enter choice [1, 2, or 3]: "

if "%MODE_CHOICE%"=="1" goto launch_tui
if "%MODE_CHOICE%"=="2" goto launch_ui
if "%MODE_CHOICE%"=="3" goto launch_both

:launch_tui
echo Starting Backend Server...
start "KRATOS Backend" cmd /k "cd /d %ROOT_DIR%backend && %ROOT_DIR%venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo Waiting for backend server startup...
timeout /t 3 >nul
echo Launching KRATOS Interactive TUI...
cd /d "%ROOT_DIR%tui"
"%ROOT_DIR%venv\Scripts\python.exe" app.py
goto end

:launch_ui
echo Starting Backend Server...
start "KRATOS Backend" cmd /k "cd /d %ROOT_DIR%backend && %ROOT_DIR%venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo Waiting for backend server startup...
timeout /t 3 >nul
echo Starting React Web Dashboard...
cd /d "%ROOT_DIR%frontend"
call npm run dev
goto end

:launch_both
echo Spawning Full Ecosystem (Backend + React UI + TUI Control Center)...
start "KRATOS Backend Server" cmd /k "cd /d %ROOT_DIR%backend && %ROOT_DIR%venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo Waiting for backend server startup...
timeout /t 3 >nul
start "KRATOS Web UI" cmd /k "cd /d %ROOT_DIR%frontend && npm run dev"
echo Launching KRATOS Interactive TUI...
cd /d "%ROOT_DIR%tui"
"%ROOT_DIR%venv\Scripts\python.exe" app.py
goto end

:end
pause

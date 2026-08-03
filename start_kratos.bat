@echo off
setlocal EnableExtensions
title KRATOS Automated Launcher and Environment Diagnostic Tool

set "ROOT_DIR=%~dp0"
set "VENV_DIR=%ROOT_DIR%venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "TUI_DIR=%ROOT_DIR%tui"

cd /d "%ROOT_DIR%"

if not exist "%VENV_PY%" goto create_venv
"%VENV_PY%" -V >nul 2>&1
if errorlevel 1 goto create_venv
echo [1/4] Python virtual environment (venv) detected and healthy.
goto show_banner

:create_venv
echo [1/4] Creating Python virtual environment (venv)...
py -3 -m venv --clear "%VENV_DIR%" >nul 2>&1
if errorlevel 1 goto venv_fallback
if not exist "%VENV_PY%" goto venv_fail
goto show_banner

:venv_fallback
py -3.14 -m venv --clear "%VENV_DIR%" >nul 2>&1
if not exist "%VENV_PY%" goto venv_fail
echo [SUCCESS] Virtual environment created.
goto show_banner

:venv_fail
echo [ERROR] Failed to create Python virtual environment. Please ensure Python 3.10+ is installed and available.
pause
exit /b 1

:show_banner
echo.
"%VENV_PY%" -c "import sys; sys.path.append(r'%TUI_DIR%'); from ascii_banner import KRATOS_ASCII_BANNER; print(KRATOS_ASCII_BANNER)" 2>nul
if errorlevel 1 (
    echo      __ __    ____     ___       ______   ____     _____
    echo    / //_/   / __ \   /   ^|     /_  __/  / __ \   / ___/
    echo   / ,^<     / /_/ /  / /^| ^|      / /    / / / /   \__ \
    echo  / /^| ^|   / _, _/  / ___ ^|     / /    / /_/ /   ___/ /
    echo /_/ ^|_^|  /_/ ^|_^|  /_/  ^|_^|    /_/     \____/   /____/  - By Dzio
)
echo ===============================================================================
echo.

:check_deps
echo [2/4] Verifying Python backend dependencies...
"%VENV_PY%" -c "import fastapi, uvicorn, networkx, rich, textual, reportlab, cv2, numpy, PIL, torch" >nul 2>&1
if errorlevel 1 goto install_deps
echo [SUCCESS] Backend Python dependencies satisfied.
goto check_env

:install_deps
echo [INFO] Installing / repairing backend dependencies from requirements.txt...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r "%ROOT_DIR%requirements.txt"
if errorlevel 1 goto deps_fail
goto check_env

:deps_fail
echo [ERROR] Dependency installation failed.
pause
exit /b 1

:check_env
echo [3/4] Checking NVIDIA NIM credentials...
if exist "%ROOT_DIR%.env" (
    echo [INFO] Found .env configuration file.
) else (
    echo [WARNING] .env file not found in project root.
    echo [NOTE] KRATOS will run in fallback mode without NIM_API_KEY.
)

echo [4/4] Verifying React frontend dependencies...
if not exist "%FRONTEND_DIR%\node_modules" goto install_npm
echo [SUCCESS] Frontend npm dependencies verified.
goto select_mode

:install_npm
echo [INFO] Frontend node_modules not found. Installing dependencies via npm...
cd /d "%FRONTEND_DIR%"
call npm install
if errorlevel 1 goto npm_fail
cd /d "%ROOT_DIR%"
goto select_mode

:npm_fail
echo [ERROR] Frontend dependency installation failed.
pause
exit /b 1

:select_mode
echo.
echo ===============================================================================
echo                   SELECT LAUNCH MODE FOR KRATOS SYSTEM
echo ===============================================================================
echo   [1] Terminal User Interface (TUI)
echo   [2] Web Dashboard User Interface (UI)
echo   [3] Spawn Both (Backend Server, Frontend UI, and TUI)
echo ===============================================================================
echo.

set /p MODE_CHOICE="Enter choice [1, 2, or 3]: "
if "%MODE_CHOICE%"=="" set "MODE_CHOICE=3"

if "%MODE_CHOICE%"=="1" goto launch_tui
if "%MODE_CHOICE%"=="2" goto launch_ui
if "%MODE_CHOICE%"=="3" goto launch_both

echo [WARNING] Invalid choice. Defaulting to option 3.
goto launch_both

:launch_backend
start "KRATOS Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%VENV_PY%"" -m uvicorn main:app --host 0.0.0.0 --port 8000"
exit /b 0

:launch_tui
echo Starting Backend Server...
call :launch_backend
echo Waiting for backend server startup...
timeout /t 3 >nul
echo Launching KRATOS Interactive TUI...
"%VENV_PY%" "%TUI_DIR%\app.py"
goto end

:launch_ui
echo Starting Backend Server...
call :launch_backend
echo Waiting for backend server startup...
timeout /t 3 >nul
echo Starting React Web Dashboard...
cd /d "%FRONTEND_DIR%"
call npm run dev
goto end

:launch_both
echo Spawning Full Ecosystem (Backend + React UI + TUI Control Center)...
call :launch_backend
echo Waiting for backend server startup...
timeout /t 3 >nul
start "KRATOS Web UI" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"
echo Launching KRATOS Interactive TUI...
"%VENV_PY%" "%TUI_DIR%\app.py"
goto end

:end
pause
endlocal

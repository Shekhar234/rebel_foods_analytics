@echo off
title Cloud Kitchen Analytics
color 0A
cd /d "%~dp0"

echo.
echo  ============================================
echo   Cloud Kitchen Review Analytics
echo  ============================================
echo.

REM ════════════════════════════════════════════
REM  STEP 1 — Find Python
REM ════════════════════════════════════════════
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON_CMD=python & goto :found_python )
python3 --version >nul 2>&1
if not errorlevel 1 ( set PYTHON_CMD=python3 & goto :found_python )
for %%V in (313 312 311 310 39) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :found_python
    )
)
echo  [ERROR] Python not found. Install from https://python.org
pause & exit /b 1
:found_python
echo  [OK] Python found.

REM ════════════════════════════════════════════
REM  STEP 2 — pip
REM ════════════════════════════════════════════
set PIP_CMD=
%PYTHON_CMD% -m pip --version >nul 2>&1
if not errorlevel 1 ( set PIP_CMD=%PYTHON_CMD% -m pip & goto :found_pip )
pip --version >nul 2>&1
if not errorlevel 1 ( set PIP_CMD=pip & goto :found_pip )
%PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1
%PYTHON_CMD% -m pip --version >nul 2>&1
if not errorlevel 1 ( set PIP_CMD=%PYTHON_CMD% -m pip & goto :found_pip )
echo  [ERROR] pip not found. Run: python -m ensurepip --upgrade
pause & exit /b 1
:found_pip
echo  [OK] pip found.

REM ════════════════════════════════════════════
REM  STEP 3 — Install dependencies
REM ════════════════════════════════════════════
echo  Installing Flask and pandas (skip if already installed)...
%PIP_CMD% install flask pandas -q --disable-pip-version-check 2>nul
if errorlevel 1 ( %PIP_CMD% install flask pandas --user -q 2>nul )
echo  [OK] Dependencies ready.
echo.

REM ════════════════════════════════════════════
REM  STEP 4 — CSV CHECK (most important step)
REM ════════════════════════════════════════════
echo  ┌─────────────────────────────────────────────────┐
echo  │  IMPORTANT: CSV DATA FILE CHECK                 │
echo  └─────────────────────────────────────────────────┘
echo.

REM Check if CSV is in the data\ folder
if exist "data\*.csv" (
    echo  [OK] CSV file found in data\ folder:
    dir /b "data\*.csv"
    echo.
    goto :launch
)

REM No CSV found - show clear instructions and open the folder
echo  [!] No CSV file found in the data\ folder.
echo.
echo  You need to copy your Zomato/Swiggy CSV file into:
echo.
echo    %cd%\data\
echo.
echo  Opening that folder for you now...
echo  Please drag your CSV file into that window, then come back here.
echo.
start "" "%cd%\data"
echo  Press any key once you have copied the CSV into the data folder...
pause
echo.

REM Check again after user action
if exist "data\*.csv" (
    echo  [OK] CSV found:
    dir /b "data\*.csv"
    echo.
    goto :launch
) else (
    echo  [ERROR] Still no CSV in data\ folder.
    echo  The app will start but will show 0 data.
    echo  Add your CSV to %cd%\data\ and restart.
    echo.
)

REM ════════════════════════════════════════════
REM  STEP 5 — Launch Flask + open browser
REM ════════════════════════════════════════════
:launch
echo  Starting Flask server...
echo  FIRST RUN: classifying 164k rows takes ~60 seconds. Subsequent runs load instantly.
echo.
echo  ┌─────────────────────────────────────────────────┐
echo  │  Dashboard: http://localhost:5000               │
echo  │                                                  │
echo  │  The server output will appear below.           │
echo  │  Wait for "Ready: 164,xxx rows loaded"          │
echo  │  then refresh your browser.                     │
echo  └─────────────────────────────────────────────────┘
echo.

REM Open browser after 35 seconds (enough time for CSV classification)
REM Wait 70s on first run (classification), 15s on subsequent runs (cache load)
if exist "data\reviews_local.pkl" (
    start "" cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:5000"
) else (
    echo  First run detected - browser will open after ~70 seconds while CSV is classified...
    start "" cmd /c "timeout /t 70 /nobreak >nul && start http://localhost:5000"
)

REM Run Flask in THIS window so output is visible
%PYTHON_CMD% app.py

echo.
echo  Server stopped. Press any key to close.
pause

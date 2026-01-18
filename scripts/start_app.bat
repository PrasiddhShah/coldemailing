@echo off
echo ==========================================
echo   Starting Apollo Job Search Tool
echo ==========================================

:: Change to project root directory
cd /d "%~dp0\.."

:: 1. Check Database Connection (Supabase)
echo [1/4] Checking Supabase Database Connection...
python -c "from database import test_connection; exit(0 if test_connection() else 1)"
if errorlevel 1 (
    echo [ERROR] Database connection failed!
    echo Please check your .env file has correct Supabase credentials:
    echo   DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    pause
    exit /b 1
)

:: 2. Start Backend Server
echo [2/4] Starting Backend Server...
start "Apollo Backend" cmd /k "python server.py"

:: 3. Start Frontend Server
echo [3/4] Starting Frontend Server...
cd web
start "Apollo Frontend" cmd /k "npm run dev"
cd ..

:: 4. Open Browser
echo [4/4] Opening Browser...
timeout /t 3 >nul
start http://localhost:5173

echo.
echo ==========================================
echo   App is running!
echo ==========================================
echo Backend:   http://localhost:8000
echo Frontend:  http://localhost:5173
echo Database:  Supabase (managed PostgreSQL)
echo.
echo Close the command windows to stop the app.
pause

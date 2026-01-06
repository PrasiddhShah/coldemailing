@echo off
echo ==========================================
echo   Starting Apollo Job Search Tool 🚀
echo ==========================================

:: 1. Start Backend Server
echo Starting Backend...
start "Apollo Backend" cmd /k "python -m uvicorn server:app --reload"

:: 2. Start Frontend Server
echo Starting Frontend...
cd web
start "Apollo Frontend" cmd /k "npm run dev"

:: 3. Open Browser
echo Opening Browser...
timeout /t 3 >nul
start http://localhost:5173

echo.
echo App is running! Close the command windows to stop.
pause

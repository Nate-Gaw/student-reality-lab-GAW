@echo off
REM Start the MCP bridge and website together

cd /d "d:\College Classes\IS219\student-reality-lab-GAW\Website"

echo Starting MCP Bridge...
start "MCP Bridge" cmd /k "d:\College Classes\IS219\.venv\Scripts\python.exe" mcp_bridge.py

timeout /t 3 /nobreak > nul

echo Starting Vite Frontend...
start "Vite Frontend" cmd /k npm run dev

echo.
echo ===================================================
echo Both services are starting in separate windows:
echo - MCP Bridge: http://127.0.0.1:5055
echo - Frontend: http://localhost:5173
echo ===================================================
echo.
echo Press any key to exit this launcher...
pause > nul

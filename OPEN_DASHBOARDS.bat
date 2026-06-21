@echo off
REM One-click launcher for the GridLock IQ web dashboards.
REM Starts a tiny local server (so the street map + data load reliably) and
REM opens both the Police and Analyst dashboards in your browser.
cd /d "%~dp0"
echo Starting GridLock IQ dashboards + live CV server on http://localhost:8531 ...
start "GridLock IQ server" cmd /c "python server.py"
timeout /t 3 >nul
start "" "http://localhost:8531/index.html"
start "" "http://localhost:8531/analyst.html"
echo.
echo Police dashboard : http://localhost:8531/index.html
echo Analyst dashboard: http://localhost:8531/analyst.html
echo (Close the "GridLock IQ server" window to stop.)

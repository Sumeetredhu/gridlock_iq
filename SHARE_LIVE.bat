@echo off
REM ===================================================================
REM  GridLock IQ - put the WHOLE app (dashboards + live CV) on a public
REM  URL with zero accounts, via a Cloudflare quick tunnel.
REM  Double-click this. A "trycloudflare.com" link prints below - share it.
REM  Keep this window (and your PC) on for the link to stay live.
REM ===================================================================
cd /d "%~dp0"

echo [1/3] Starting GridLock IQ server (dashboards + YOLO CV)...
start "GridLock IQ server" cmd /c "python server.py"
timeout /t 5 >nul

echo [2/3] Locating cloudflared...
set CF=..\cloudflared.exe
if not exist "%CF%" set CF=cloudflared.exe
if not exist "%CF%" (
  echo Downloading cloudflared (one-time, ~50 MB)...
  powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
  set CF=cloudflared.exe
)

echo [3/3] Opening public tunnel. Your shareable link appears below:
echo ------------------------------------------------------------------
"%CF%" tunnel --url http://localhost:8531 --no-autoupdate

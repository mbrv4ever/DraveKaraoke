@echo off
cd /d "%~dp0"
set PY=
for %%v in (3.10 3.11 3.12) do (
  if not defined PY ( py -%%v -c "import sys" >nul 2>&1 && set PY=py -%%v )
)
if not defined PY ( echo Geen Python 3.10-3.12 gevonden. & pause & exit /b 1 )
%PY% -c "import PyQt6.QtWebEngineWidgets" >nul 2>&1 || %PY% -m pip install PyQt6 PyQt6-WebEngine
%PY% -c "import yt_dlp, qrcode, PIL" >nul 2>&1 || %PY% -m pip install yt-dlp qrcode pillow
start "" %PY% main.py

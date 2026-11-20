@echo off
cd /d "%~dp0"
set PY=
for %%v in (3.10 3.11 3.12) do (
  if not defined PY ( py -%%v -c "import sys" >nul 2>&1 && set PY=py -%%v )
)
if not defined PY ( echo Geen Python 3.10-3.12 gevonden. & pause & exit /b 1 )
%PY% -c "import PyQt6.QtWebEngineWidgets" >nul 2>&1 || %PY% -m pip install PyQt6 PyQt6-WebEngine
%PY% -c "import yt_dlp, qrcode, PIL" >nul 2>&1 || %PY% -m pip install yt-dlp qrcode pillow
%PY% -c "import PyInstaller" >nul 2>&1 || %PY% -m pip install pyinstaller
%PY% make_icon.py
rem jouw gegevens in dist eerst bewaren (namen, tekst-verschuivingen en duetten), na het bouwen terugzetten
if exist _bewaar rmdir /s /q _bewaar
mkdir _bewaar
for %%f in (instellingen.json liedjes.json) do if exist "dist\DraveKaraoke\%%f" copy /y "dist\DraveKaraoke\%%f" _bewaar\ >nul
if exist "dist\DraveKaraoke\cache\web" robocopy "dist\DraveKaraoke\cache" "_bewaar\cache" /E /NFL /NDL /NJH /NJS /NP >nul
%PY% -m PyInstaller --noconfirm --clean --windowed --onedir --name DraveKaraoke --icon assets\icon.ico --add-data "web;web" --hidden-import karaoke --hidden-import server --collect-all PyQt6 --collect-all yt_dlp --collect-all qrcode main.py
if errorlevel 1 ( echo BOUWEN MISLUKT & pause & exit /b 1 )
if not exist "dist\DraveKaraoke\DraveKaraoke.exe" ( echo GEEN EXE GEVONDEN & pause & exit /b 1 )
xcopy /e /i /y assets "dist\DraveKaraoke\assets" >nul
if exist DraveKaraoke_snelgids.pdf copy /y DraveKaraoke_snelgids.pdf "dist\DraveKaraoke\" >nul
if exist DraveKaraoke.apk copy /y DraveKaraoke.apk "dist\DraveKaraoke\" >nul
for %%f in (instellingen.json liedjes.json) do if exist "_bewaar\%%f" copy /y "_bewaar\%%f" "dist\DraveKaraoke\" >nul
if exist "_bewaar\cache" robocopy "_bewaar\cache" "dist\DraveKaraoke\cache" /E /NFL /NDL /NJH /NJS /NP >nul
echo KLAAR: dist\DraveKaraoke\DraveKaraoke.exe

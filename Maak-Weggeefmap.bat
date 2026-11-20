@echo off
rem Maak-Weggeefmap.bat - een schone map om DraveKaraoke weg te geven.
rem ZONDER jouw eigen gegevens: geen cache (YouTube-inlog!), geen namen, geen liedjes-instellingen, geen logboeken.
cd /d "%~dp0"
if not exist "dist\DraveKaraoke\DraveKaraoke.exe" ( echo Eerst bouwen: Build-DraveKaraoke-EXE.bat & pause & exit /b 1 )
if exist "weggeven\DraveKaraoke" rmdir /s /q "weggeven\DraveKaraoke"
mkdir "weggeven\DraveKaraoke"
robocopy "dist\DraveKaraoke" "weggeven\DraveKaraoke" /E /NFL /NDL /NJH /NJS /XD cache _bewaar /XF instellingen.json liedjes.json *.log *.bak >nul
if errorlevel 8 ( echo KOPIEREN MISLUKT & pause & exit /b 1 )
copy /y "Lees_mij_eerst.pdf" "weggeven\DraveKaraoke\" >nul
copy /y "DraveKaraoke_snelgids.pdf" "weggeven\DraveKaraoke\" >nul
copy /y "DraveKaraoke.apk" "weggeven\DraveKaraoke\" >nul
if exist "DraveKaraoke_uitleg.mp4" copy /y "DraveKaraoke_uitleg.mp4" "weggeven\DraveKaraoke\" >nul
if exist "weggeven\DraveKaraoke\cache" ( echo FOUT: CACHE ZIT ERIN & pause & exit /b 1 )
if exist "weggeven\DraveKaraoke\instellingen.json" ( echo FOUT: INSTELLINGEN ZITTEN ERIN & pause & exit /b 1 )
if not exist "weggeven\DraveKaraoke\DraveKaraoke.exe" ( echo GEEN EXE IN DE WEGGEEFMAP & pause & exit /b 1 )
echo KLAAR: weggeven\DraveKaraoke

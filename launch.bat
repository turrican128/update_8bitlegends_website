@echo off
REM Double-click launcher for the 8bit Legends Web Editor.
REM Frees a stuck port, starts Flask, and opens your browser at :5000.
cd /d "%~dp0"
echo Launching 8bit Legends Web Editor...
python app.py %*
pause

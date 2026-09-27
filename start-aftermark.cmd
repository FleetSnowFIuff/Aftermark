@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup.cmd first. Python 3.11 or newer is required.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m aftermark --data-dir "%~dp0.local\library" serve --open
if errorlevel 1 pause

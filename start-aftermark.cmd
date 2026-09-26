@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the environment first. See README.zh-CN.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m aftermark --data-dir "%~dp0.local\library" serve --open
if errorlevel 1 pause

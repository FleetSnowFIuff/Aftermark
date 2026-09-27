@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 goto failed
echo Ready. Run start-aftermark.cmd to open your local library.
pause
exit /b 0
:failed
echo Setup failed. Python 3.11 or newer and internet access are required.
pause
exit /b 1

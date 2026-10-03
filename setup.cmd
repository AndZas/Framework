@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv-framework\Scripts\python.exe" py -3.13 -m venv .venv-framework
if errorlevel 1 exit /b 1
".venv-framework\Scripts\python.exe" -m pip install -e ".[dev]"
exit /b %errorlevel%

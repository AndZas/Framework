@echo off
setlocal
cd /d "%~dp0\..\.."
if not exist .venv-theme-spike\Scripts\python.exe py -3.13 -m venv .venv-theme-spike
if errorlevel 1 exit /b 1
.venv-theme-spike\Scripts\python.exe -m pip install -r prototypes\theme_api_spike\requirements.txt
exit /b %errorlevel%

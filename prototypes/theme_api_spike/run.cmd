@echo off
setlocal
cd /d "%~dp0\..\.."
if not exist .venv-theme-spike\Scripts\python.exe (
    echo Run prototypes\theme_api_spike\setup.cmd first.
    exit /b 1
)
.venv-theme-spike\Scripts\python.exe prototypes\theme_api_spike\app.py
exit /b %errorlevel%

@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv-framework\Scripts\python.exe" (
    echo Run setup.cmd first.
    exit /b 1
)
".venv-framework\Scripts\python.exe" examples\animations.py
exit /b %errorlevel%

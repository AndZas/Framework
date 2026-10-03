@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv-qt-quick\Scripts\python.exe" (
    py -3.13 -m venv .venv-qt-quick
    if errorlevel 1 exit /b 1
)
".venv-qt-quick\Scripts\python.exe" -m pip install -r "prototypes\layout_api_comparison\requirements.txt"
exit /b %errorlevel%

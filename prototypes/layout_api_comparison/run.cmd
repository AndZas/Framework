@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv-qt-quick\Scripts\python.exe" (
    echo Missing project-local environment. Run prototypes\layout_api_comparison\setup.cmd first.
    exit /b 1
)
set "LAYOUT_STYLE=%~1"
if "%LAYOUT_STYLE%"=="" set "LAYOUT_STYLE=hybrid"
".venv-qt-quick\Scripts\python.exe" "prototypes\layout_api_comparison\main.py" --style "%LAYOUT_STYLE%" %2
exit /b %errorlevel%

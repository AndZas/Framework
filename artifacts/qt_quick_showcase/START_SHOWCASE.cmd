@echo off
setlocal
cd /d "%~dp0QtQuickShowcase.dist"
if not exist "example_app.exe" (
  echo The showcase EXE is missing. Keep START_SHOWCASE.cmd and QtQuickShowcase.dist together.
  pause
  exit /b 1
)
"example_app.exe" %*
if errorlevel 1 (
  echo The showcase exited with an error. Check PACKAGE_README.md and the console output.
  pause
  exit /b 1
)
exit /b 0

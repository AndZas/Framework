@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_RUN="
where py >nul 2>nul
if not errorlevel 1 (
  py -3.13 -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul
  if not errorlevel 1 set "PYTHON_RUN=py -3.13"
  if not defined PYTHON_RUN (
    py -3.12 -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul
    if not errorlevel 1 set "PYTHON_RUN=py -3.12"
  )
)
if not defined PYTHON_RUN (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; assert sys.version_info[:2] in ((3, 12), (3, 13)) and sys.maxsize > 2**32" >nul 2>nul
    if not errorlevel 1 set "PYTHON_RUN=python"
  )
)
if not defined PYTHON_RUN goto no_python
if not exist ".venv-showcase\Scripts\python.exe" (
  echo Creating a dedicated showcase environment...
  %PYTHON_RUN% -m venv ".venv-showcase"
  if errorlevel 1 goto venv_failed
)
".venv-showcase\Scripts\python.exe" -c "import PySide6; assert PySide6.__version__ == '6.11.2'" >nul 2>nul
if errorlevel 1 (
  echo Installing pinned PySide6 into the showcase environment. Internet access may be needed...
  ".venv-showcase\Scripts\python.exe" -m pip install --disable-pip-version-check -r "requirements.txt"
  if errorlevel 1 goto install_failed
)
echo Starting Qt Quick showcase...
".venv-showcase\Scripts\python.exe" "example_app.py" %*
if errorlevel 1 goto run_failed
exit /b 0
:no_python
echo 64-bit Python 3.13 or 3.12 was not found through py or PATH.
echo Install Python 3.13 from python.org with the Windows py launcher, then double-click this file again.
pause
exit /b 1
:venv_failed
echo Could not create .venv-showcase. Check permissions and free disk space.
pause
exit /b 1
:install_failed
echo Pinned PySide6 installation failed. Check network access and retry this file.
echo No global Python packages were changed.
pause
exit /b 1
:run_failed
echo The showcase exited with an error. See the messages above and START_HERE.md.
pause
exit /b 1

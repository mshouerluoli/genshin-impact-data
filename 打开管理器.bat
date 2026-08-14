@echo off
title Item.json Manager
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "%~dp0ItemManagerServer.py"
  exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
  start "" python "%~dp0ItemManagerServer.py"
  exit /b
)
echo [Error] Python 3 not found. Please install Python and add to PATH.
pause

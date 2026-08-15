@echo off
title ¼ÓÃÜ Item.json
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0encrypt_item.py"
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  pythonw "%~dp0encrypt_item.py"
  exit /b
)
echo [Error] Python 3 not found. Please install Python and add to PATH.
pause

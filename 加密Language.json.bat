@echo off
title ¼ÓÃÜ Language.json
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0build_language.py"
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  pythonw "%~dp0build_language.py"
  exit /b
)
echo [Error] Python 3 not found. Please install Python and add to PATH.
pause

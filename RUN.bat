@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title UPSC Anchor with Kumar - Monthly PDF Production

echo ========================================================
echo       UPSC ANCHOR WITH KUMAR - YK MONTHLY
echo                 PDF PRODUCTION
echo ========================================================
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=%CD%\.venv\Scripts\python.exe"

if not exist "INPUT_DATA.txt" (
    echo ERROR: INPUT_DATA.txt is missing from the project root.
    goto :failed
)
if not exist "input_processing\text_to_json_converter.py" (
    echo ERROR: input_processing\text_to_json_converter.py is missing.
    goto :failed
)
if not exist "input_processing\validator.py" (
    echo ERROR: input_processing\validator.py is missing.
    goto :failed
)

echo [1/3] Converting root INPUT_DATA.txt to INPUT.json...
"%PYTHON%" -u "input_processing\text_to_json_converter.py" "INPUT_DATA.txt"
if errorlevel 1 goto :failed

echo.
echo [2/3] Validating INPUT.json...
"%PYTHON%" -u "input_processing\validator.py"
if errorlevel 1 goto :failed

echo.
echo [3/3] Generating monthly PDFs...
"%PYTHON%" -u -m src.main
if errorlevel 1 goto :failed

echo.
echo ========================================================
echo             PRODUCTION COMPLETED
echo ========================================================
echo.
pause
exit /b 0

:failed
echo.
echo ========================================================
echo              PRODUCTION FAILED
echo        Check the error shown above.
echo ========================================================
echo.
pause
exit /b 1

@echo off
echo Installing BackupX dependencies...

REM This script assumes that Python is added to the system PATH.
REM If you see an error like "'python' is not recognized as an internal or external command...",
REM then Python is not in the PATH. To fix this:
REM 1. Use the full path to python.exe instead of just "python"
REM    For example: "C:\Users\<your_username>\AppData\Local\Programs\Python\Python3X\python.exe"
REM 2. Or add Python to the PATH during installation or manually via environment variables.

REM Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo BackupX installed successfully!
pause

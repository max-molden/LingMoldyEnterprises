@echo off
setlocal

pyinstaller --noconfirm --clean --windowed --name QRScreenReader --paths . --collect-all PySide6 app/main.py
if errorlevel 1 exit /b 1

call build_helper.bat
if errorlevel 1 exit /b 1

echo Build complete.

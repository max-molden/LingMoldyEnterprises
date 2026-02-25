@echo off
setlocal
pyinstaller --noconfirm --clean --windowed --name QRScreenReader --paths . --collect-all PySide6 app/main.py

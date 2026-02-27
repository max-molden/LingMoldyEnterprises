@echo off
setlocal

if exist build-helper\QRHotkeyHelper.exe (
  start "" build-helper\QRHotkeyHelper.exe
) else if exist dist\QRScreenReader\QRHotkeyHelper.exe (
  start "" dist\QRScreenReader\QRHotkeyHelper.exe
)

python -m app.main %*

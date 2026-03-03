@echo off
setlocal

echo [1/3] Stopping running processes...
taskkill /IM QRHotkeyHelper.exe /F >nul 2>&1
taskkill /IM QRScreenReader.exe /F >nul 2>&1

echo [2/3] Removing dev build artifacts...
if exist build-helper rmdir /S /Q build-helper
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist
del /Q *.spec >nul 2>&1
for /d /r %%D in (__pycache__) do (
  if exist "%%D" rmdir /S /Q "%%D"
)

echo [3/3] Removing local app data and startup shortcut...
if defined APPDATA (
  if exist "%APPDATA%\QrScreenReader" rmdir /S /Q "%APPDATA%\QrScreenReader"
  del /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\QR Screen Reader Hotkey Launcher.lnk" >nul 2>&1
)

echo Dev cleanup complete.
endlocal

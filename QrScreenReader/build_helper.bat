@echo off
setlocal

if not exist dist\QRScreenReader mkdir dist\QRScreenReader

cmake -S native_helper -B build-helper -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 exit /b 1

cmake --build build-helper --config Release
if errorlevel 1 exit /b 1

if exist build-helper\Release\QRHotkeyHelper.exe (
  copy /Y build-helper\Release\QRHotkeyHelper.exe dist\QRScreenReader\QRHotkeyHelper.exe >nul
) else if exist build-helper\QRHotkeyHelper.exe (
  copy /Y build-helper\QRHotkeyHelper.exe dist\QRScreenReader\QRHotkeyHelper.exe >nul
) else (
  echo QRHotkeyHelper.exe not found after build.
  exit /b 1
)

echo Native helper ready: dist\QRScreenReader\QRHotkeyHelper.exe

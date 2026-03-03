@echo off
setlocal

if not exist dist\QRScreenReader mkdir dist\QRScreenReader

cmake -S native_helper -B build-helper -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 exit /b 1

cmake --build build-helper --config Release
if errorlevel 1 exit /b 1

set "HELPER_SRC="
if exist build-helper\Release\QRHotkeyHelper.exe (
  set "HELPER_SRC=build-helper\Release\QRHotkeyHelper.exe"
) else if exist build-helper\QRHotkeyHelper.exe (
  set "HELPER_SRC=build-helper\QRHotkeyHelper.exe"
) else (
  echo QRHotkeyHelper.exe not found after build.
  exit /b 1
)

set /a COPY_RETRIES=5
:copy_retry
copy /Y "%HELPER_SRC%" dist\QRScreenReader\QRHotkeyHelper.exe >nul
if not errorlevel 1 goto copy_ok

set /a COPY_RETRIES-=1
if %COPY_RETRIES% LEQ 0 (
  echo Failed to copy QRHotkeyHelper.exe to dist\QRScreenReader.
  echo The destination file appears to be in use by another process.
  echo Close the running helper and retry.
  exit /b 1
)

timeout /t 1 /nobreak >nul
goto copy_retry

:copy_ok
echo Native helper ready: dist\QRScreenReader\QRHotkeyHelper.exe

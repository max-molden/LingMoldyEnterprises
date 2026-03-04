@echo off
setlocal

call build_exe.bat
if errorlevel 1 exit /b 1

set "ISCC_PATH="
where /Q ISCC.exe
if not errorlevel 1 (
  set "ISCC_PATH=ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
  set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
  set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%ISCC_PATH%"=="" (
  echo Inno Setup compiler not found.
  echo Install Inno Setup 6 and add ISCC.exe to PATH, or install to the default folder.
  exit /b 1
)

"%ISCC_PATH%" installer\QRScreenReader.iss
if errorlevel 1 exit /b 1

echo Installer build complete: installer\QRScreenReaderInstaller.exe
endlocal

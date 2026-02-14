# CodexUlator (C++ GUI Calculator)

Lightweight desktop calculator built in modern C++ with FLTK.

## Features
- Addition (`+`)
- Subtraction (`-`)
- Multiplication (`*`)
- Division (`/`)

## Safety Notes
- Single-threaded app (no background threads).
- No network, shell, or file I/O in calculator logic.
- Strict input validation before numeric parsing.
- Division-by-zero and non-finite result checks.

## Project Layout
- `CodexUlator/CMakeLists.txt`
- `CodexUlator/src/main.cpp`
- `CodexUlator/cmake/toolchains/mingw-w64.cmake`

## Dependencies
- `cmake` (3.16+)
- C++20 compiler (`g++`, `clang++`, or MSVC)
- FLTK development libraries

## Check Dependencies

### Linux
```bash
cmake --version
g++ --version
pkg-config --modversion fltk || echo "FLTK not found"
```

### Windows (PowerShell)
```powershell
cmake --version
ninja --version
cl
if ($LASTEXITCODE -ne 0) { "MSVC compiler not detected in this shell" }
vcpkg version
```
Check FLTK package:
```powershell
vcpkg list | Select-String fltk
```

## Install Dependencies

### Linux (Debian/Ubuntu)
Run from any directory:
```bash
sudo apt-get update
sudo apt-get install -y cmake g++ libfltk1.3-dev pkg-config
```

### Linux (Fedora)
Run from any directory:
```bash
sudo dnf install -y cmake gcc-c++ fltk-devel pkgconf-pkg-config
```

### Windows (PowerShell, command-only)
Run from any directory:

Install required tools with `winget`:
```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --source winget --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
winget install --id Kitware.CMake --exact --source winget
winget install --id Ninja-build.Ninja --exact --source winget
winget install --id Git.Git --exact --source winget
```

Restart PowerShell after installs complete, then bootstrap `vcpkg`:
```powershell
Set-Location $HOME
git clone https://github.com/microsoft/vcpkg.git $HOME\vcpkg
& $HOME\vcpkg\bootstrap-vcpkg.bat
$env:PATH = "$HOME\vcpkg;$env:PATH"
```

Install FLTK via `vcpkg`:
```powershell
Set-Location $HOME\vcpkg
vcpkg install fltk:x64-windows
```

Optional: persist `vcpkg` in your user PATH:
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$HOME\vcpkg", "User")
```

Open **x64 Native Tools Command Prompt for VS 2022** or **Developer PowerShell for VS 2022** before building with MSVC.

## Build and Run

### Linux
Run from repo root (`LingMoldyEnterprises/`):
```bash
cmake -S CodexUlator -B CodexUlator/build -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build -j
./CodexUlator/build/secure_calc
```

### Windows (MSVC + Ninja)
Run from repo root (`LingMoldyEnterprises/`) in **Developer PowerShell for VS 2022**:
```powershell
Set-Location <path-to>\LingMoldyEnterprises
cmake -S CodexUlator -B CodexUlator/build -G "Ninja" -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build
.\CodexUlator\build\secure_calc.exe
```

If using vcpkg, add your toolchain file:
```powershell
Set-Location <path-to>\LingMoldyEnterprises
cmake -S CodexUlator -B CodexUlator/build -G "Ninja" `
  -DCMAKE_TOOLCHAIN_FILE="$HOME/vcpkg/scripts/buildsystems/vcpkg.cmake" `
  -DVCPKG_TARGET_TRIPLET=x64-windows `
  -DCMAKE_BUILD_TYPE=Release
```

## Cross-Compile (Linux -> Windows with MinGW-w64)
Install MinGW-w64 and ensure Windows-target FLTK is available to that toolchain.

Run from repo root (`LingMoldyEnterprises/`):
```bash
cmake -S CodexUlator -B CodexUlator/build-win \
  -DCMAKE_TOOLCHAIN_FILE=CodexUlator/cmake/toolchains/mingw-w64.cmake \
  -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build-win -j
```

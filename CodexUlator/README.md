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
cl
# or
mingw32-g++ --version
```
For FLTK with vcpkg:
```powershell
vcpkg list | findstr fltk
```

## Install Dependencies

### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y cmake g++ libfltk1.3-dev pkg-config
```

### Linux (Fedora)
```bash
sudo dnf install -y cmake gcc-c++ fltk-devel pkgconf-pkg-config
```

### Windows
1. Install Visual Studio Build Tools (or MinGW-w64).
2. Install CMake: https://cmake.org/download/
3. Install vcpkg: https://learn.microsoft.com/vcpkg/get_started/get-started
4. Install FLTK:
```powershell
vcpkg install fltk
```

## Build and Run

### Linux
From repo root:
```bash
cmake -S CodexUlator -B CodexUlator/build -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build -j
./CodexUlator/build/secure_calc
```

### Windows (MSVC + Ninja)
From repo root:
```powershell
cmake -S CodexUlator -B CodexUlator/build -G "Ninja" -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build
.\CodexUlator\build\secure_calc.exe
```

If using vcpkg, add your toolchain file:
```powershell
cmake -S CodexUlator -B CodexUlator/build -G "Ninja" `
  -DCMAKE_TOOLCHAIN_FILE=C:/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake `
  -DCMAKE_BUILD_TYPE=Release
```

## Cross-Compile (Linux -> Windows with MinGW-w64)
Install MinGW-w64 and ensure Windows-target FLTK is available to that toolchain.

From repo root:
```bash
cmake -S CodexUlator -B CodexUlator/build-win \
  -DCMAKE_TOOLCHAIN_FILE=CodexUlator/cmake/toolchains/mingw-w64.cmake \
  -DCMAKE_BUILD_TYPE=Release
cmake --build CodexUlator/build-win -j
```

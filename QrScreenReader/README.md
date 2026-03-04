# QR Screen Reader (Windows)

Desktop app to scan QR codes from a selected screen region.

## End-User Quick Start (2-3 minutes)

1. Download `QRScreenReaderInstaller.exe` from the [GitHub Release assets page](https://github.com/max-molden/LingMoldyEnterprises/releases) when a release is published; otherwise build it via the **Build Installer** section below.
2. Run installer and accept UAC prompt.
3. Keep "Enable always-on native global hotkey launcher" checked if you want `Win+Shift+Q` to work system-wide after sign-in.
4. Finish install.

No Python/CMake/dev tools are needed for end users.
No virtual environment is needed when using the installer.

## Features

- Snip overlay workflow similar to `Win+Shift+S`.
- Global hotkey support (`Win+Shift+Q` by default):
  - In-app hotkey when app is running.
  - Optional always-on native helper for system-wide hotkey availability.
- Direct launch mode with `--mode snip` (or `--snip`) to immediately start selecting a region.
- Decodes QR from snips or image files.
- Configurable behavior stored in `%APPDATA%\\QrScreenReader\\config.json` and editable in the GUI:
  - Auto-copy link to clipboard (default: on)
  - Auto-open decoded link (default: off)
  - Safety checks for suspicious links (default: on)
  - Browser mode: system default or custom browser executable path
  - Enable/disable global hotkey and change combination
- GUI includes explicit `Copy` and `Open` buttons.

## Launch Methods

- Start Menu shortcut
- Desktop shortcut (if selected during install)
- Direct executable launch: `QRScreenReader.exe`
- Command line launch with arguments

## Project Layout

- `app/main.py`: app entrypoint and CLI arguments
- `app/ui_main.py`: main UI and behavior wiring
- `app/snip_overlay.py`: area selection overlay
- `app/hotkey.py`: in-app global hotkey registration
- `app/win_integration.py`: native helper integration hooks
- `app/qr_decode.py`: QR detection/decoding
- `app/safety.py`: suspicious-link checks
- `app/config.py`: config load/save
- `native_helper/QRHotkeyHelper.cpp`: native always-on hotkey helper
- `build_exe.bat`: build Python app + native helper
- `build_helper.bat`: build native helper only
- `installer/QRScreenReader.iss`: Inno Setup installer script

## Build Safely (Developer)

Use a dedicated virtual environment.
If you are following the build/developer steps below, creating a venv is required.

### Build Dependencies (Windows)

1. Python 3.11+ (Python 3.13 is also acceptable)
2. CMake 3.16+
3. Visual Studio Build Tools 2022 (Desktop development with C++)
4. Inno Setup 6

### Python Dependencies

1. Open PowerShell.
2. Go to the project folder:

```powershell
cd path\to\LingMoldyEnterprises\QrScreenReader
```

3. Check available Python versions:

```powershell
py -0
```

4. Create the virtual environment with any installed Python version that is `3.11` or newer.

Examples:

```powershell
py -3.13 -m venv .venv
```

or:

```powershell
py -3.11 -m venv .venv
```

or use your current default Python 3 launcher target:

```powershell
py -3 -m venv .venv
```

If dependency installation fails on 3.13+, recreate the venv with 3.11.

5. Activate the virtual environment:

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt (`cmd.exe`):

```bat
.\.venv\Scripts\activate.bat
```

6. Install Python dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

## Run in Development

From `QrScreenReader` folder:

```bat
build_helper.bat
```

Virtual environment: **not required** for this command (native C++ build only).

This builds `QRHotkeyHelper.exe` for the always-on global hotkey path in development.
If the helper is running, `Win+Shift+Q` can trigger snip mode even when the main app window is not running.

Then activate your virtual environment and run:

```bat
run_dev.bat
```

Virtual environment: **required** for this command (`python -m app.main`).

Direct snip launch:

```bat
run_dev.bat --mode snip
```

## Clean Development Artifacts

From `QrScreenReader` folder:

```bat
clean_dev.bat
```

This script:

- Stops `QRHotkeyHelper.exe` and `QRScreenReader.exe` if running.
- Removes local build artifacts (`build-helper`, `build`, `dist`, `*.spec`, `__pycache__`).
- Removes local app data at `%APPDATA%\\QrScreenReader`.
- Removes the Startup shortcut for the native helper if present.

## Command Line Arguments

```text
--mode {gui,snip}        Startup mode (default: gui)
--snip                   Alias for --mode snip
--decode-file PATH       Decode a local image after launch
--disable-tray           Disable tray icon and quit on window close
--disable-hotkey         Disable the in-app global hotkey for this run
--hotkey COMBO           Override hotkey for this run (e.g., Win+Shift+Q)
```

## Build Windows Executable Bundle

From `QrScreenReader` folder, with your virtual environment activated:

```bat
build_exe.bat
```

Virtual environment: **required** for this command (`pyinstaller` + Python deps).

This builds:

- `dist\\QRScreenReader\\QRScreenReader.exe`
- `dist\\QRScreenReader\\QRHotkeyHelper.exe`

## Build Installer

Prerequisite: run `build_exe.bat` first (in activated venv) so `dist\\QRScreenReader\\*` exists.

1. Open `installer/QRScreenReader.iss` in Inno Setup Compiler.
2. Build.

Virtual environment: **not required** for Inno Setup compile step.

Output:

- `installer\\QRScreenReaderInstaller.exe`

Installer behavior:

- Creates Start Menu shortcut for normal launch.
- Creates Start Menu shortcut for snip mode launch.
- Optional desktop shortcut.
- Optional Startup shortcut for native helper (`QRHotkeyHelper.exe`).

## Installer UAC / Elevation

Installer requests UAC elevation because it installs to `Program Files`.

The installer shows `installer/UAC_INFO.txt` before installation, explaining:

- Exactly which files/shortcuts are created
- What the native helper does
- What is not modified (no drivers/services/firewall/proxy changes)

## GitHub Release for Fast Installs

To let users install in minutes:

1. Activate venv and build executable bundle with `build_exe.bat`.
2. Build installer from `installer/QRScreenReader.iss`.
3. Create a GitHub Release.
4. Upload `QRScreenReaderInstaller.exe` as a release asset.

## Troubleshooting

- `py` or `python` not found:
  - Install Python 3.11+ with PATH enabled, reopen terminal.
- PowerShell blocks venv activation:
  - Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
- `cmake` not found:
  - Install CMake and reopen terminal.
- Native helper build fails with missing compiler:
  - Install Visual Studio Build Tools 2022 + C++ workload.
- Installer builds but global hotkey does not work after reboot:
  - Re-run installer and enable "always-on native global hotkey launcher".
  - Ensure no other app owns the same hotkey.
- Hotkey changed in app settings but helper still uses old one:
  - Open app settings and save once; the app signals helper reload automatically.

## Notes

- Safety checks are heuristic only, not a full security scanner.
- Global hotkey requires either app running or native helper running.

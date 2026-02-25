# QR Screen Reader (Windows)

Desktop app to scan QR codes from a selected screen region.

## Features

- Global hotkey (configurable): default `Win+Shift+Q`.
- Snip overlay workflow similar to `Win+Shift+S`.
- Direct launch mode with `--mode snip` (or `--snip`) to immediately start selecting a region.
- Decodes QR from snips or image files.
- Configurable behavior stored in `%APPDATA%\\QrScreenReader\\config.json` and editable in the GUI:
  - Auto-copy link to clipboard (default: on)
  - Auto-open decoded link (default: off)
  - Safety checks for suspicious links (default: on)
  - Browser mode: system default or custom browser executable path
  - Enable/disable global hotkey
  - Change hotkey combination
- GUI includes explicit `Copy` and `Open` buttons.

## Project Layout

- `app/main.py`: app entrypoint and CLI arguments
- `app/ui_main.py`: main UI and behavior wiring
- `app/snip_overlay.py`: area selection overlay
- `app/hotkey.py`: global hotkey registration and parsing
- `app/qr_decode.py`: QR detection/decoding
- `app/safety.py`: suspicious-link checks
- `app/config.py`: config load/save
- `build_exe.bat`: pyinstaller build command
- `installer/QRScreenReader.iss`: Inno Setup installer script

## Install Dependencies (Windows)

Run these commands in PowerShell or cmd from this project directory:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

## Run in Development

```bat
run_dev.bat
```

Direct snip launch:

```bat
run_dev.bat --mode snip
```

## Command Line Arguments

```text
--mode {gui,snip}        Startup mode (default: gui)
--snip                   Alias for --mode snip
--decode-file PATH       Decode a local image after launch
--disable-tray           Disable tray icon and quit on window close
--disable-hotkey         Disable global hotkey for this run
--hotkey COMBO           Override hotkey for this run (e.g., Win+Shift+Q)
```

## Build Windows Executable

```bat
build_exe.bat
```

Output: `dist\\QRScreenReader\\QRScreenReader.exe`

## Build Installer (Inno Setup)

1. Install Inno Setup 6.
2. Open `installer/QRScreenReader.iss` in Inno Setup Compiler.
3. Build the script.

Output installer: `installer\\QRScreenReaderInstaller.exe`

Installer behavior:

- Creates Start Menu shortcut for normal launch.
- Creates Start Menu shortcut for snip mode launch.
- Optional desktop shortcut.
- Optional startup entry (`HKCU\\...\\Run`) so app starts at sign-in.

## Important Hotkey Note

Windows does not provide a native per-app `Win+Shift+Q` launch binding when the app is not running. This project achieves global hotkey behavior by running in the background (tray). Enabling startup in installer keeps the app running after sign-in so `Win+Shift+Q` works system-wide.

## GitHub Downloadable Installer

To let users download the installer directly from GitHub:

1. Build `dist\\QRScreenReader` with PyInstaller.
2. Build `installer\\QRScreenReaderInstaller.exe` with Inno Setup.
3. Create a GitHub Release and upload `QRScreenReaderInstaller.exe` as a release asset.

## Notes

- Safety checks are heuristic only, not a full security scanner.

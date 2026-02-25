# QR Screen Reader (Windows)

Desktop app to scan QR codes from a selected screen region.

## Features

- Global hotkey while app is running (configurable): default `Win+Shift+Q`.
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

## Launch Methods

After install, app launch is supported by:

- Start Menu shortcut
- Desktop shortcut (if selected during install)
- Direct executable launch: `QRScreenReader.exe`
- Command line launch with arguments

Installer can optionally add a startup launcher for global hotkey support.

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

## Build Safely (Recommended)

Use a dedicated Python virtual environment for this project. It is not strictly required, but it prevents dependency conflicts with other Python projects and keeps your global Python clean.

## Install Dependencies (Windows)

### Option A: Recommended (venv)

From the `QrScreenReader` folder in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

For `cmd.exe` activation:

```bat
.venv\Scripts\activate.bat
```

### Option B: Global install (not recommended)

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
--hotkey-daemon          Background launcher mode for global hotkey
```

## Build Windows Executable

From `QrScreenReader` folder:

```bat
build_exe.bat
```

Output:

- `dist\\QRScreenReader\\QRScreenReader.exe`

## Build Installer (Inno Setup)

1. Install Inno Setup 6.
2. Open `installer/QRScreenReader.iss` in Inno Setup Compiler.
3. Build the script.

Output installer:

- `installer\\QRScreenReaderInstaller.exe`

Installer behavior:

- Creates Start Menu shortcut for normal launch.
- Creates Start Menu shortcut for snip mode launch.
- Optional desktop shortcut.
- Optional global hotkey launcher task:
  - Creates Startup shortcut: `QRScreenReader.exe --hotkey-daemon`
  - Starts background hotkey listener after install

## Installer UAC / Elevation

Installer requests UAC elevation because it installs to `Program Files`.

The installer includes an information page (`installer/UAC_INFO.txt`) that explains:

- Exactly what files/shortcuts are created
- What the optional global hotkey launcher does
- What is not modified (no drivers/services/firewall/proxy changes)

## GitHub Downloadable Installer

To let users download the installer directly from GitHub:

1. Build `dist\\QRScreenReader` with PyInstaller.
2. Build `installer\\QRScreenReaderInstaller.exe` with Inno Setup.
3. Create a GitHub Release.
4. Upload `QRScreenReaderInstaller.exe` as a release asset.

## Troubleshooting

- `python` or `py` not found:
  - Install Python 3.11+ and check "Add Python to PATH" during install.
  - Reopen terminal and run `py --version`.
- PowerShell blocks venv activation:
  - Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then reopen PowerShell.
- `ModuleNotFoundError` when running app:
  - Activate your venv and reinstall deps with `python -m pip install -r requirements.txt`.
- `pyinstaller` command not found:
  - Run `python -m pip install pyinstaller` in the same environment.
- Build succeeds but app fails on another machine:
  - Use the installer output, not a partial folder copy.
  - Rebuild on a clean Windows machine/VM and test install/uninstall.
- Global hotkey does not trigger:
  - Ensure app is running, or enable the installer's global hotkey launcher task.
  - Check app setting for enabled hotkey and valid combination.
  - Another app may already own the same hotkey.
- QR does not decode from snip:
  - Try a tighter snip, higher zoom, or decode from saved image file.

## Notes

- Safety checks are heuristic only, not a full security scanner.
- `Win+Shift+Q` cannot trigger anything if neither the app nor the hotkey launcher is running.
- With the optional global hotkey launcher task enabled, `Win+Shift+Q` works even when the main window is closed because a background launcher process remains running.

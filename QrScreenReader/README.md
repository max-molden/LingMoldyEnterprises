# QR Screen Reader (Windows)

Desktop app to scan QR codes from a selected screen region.

## End-User Quick Start (2-3 minutes)

1. Download `QRScreenReaderInstaller.exe` from the [GitHub Release assets page](https://github.com/max-molden/LingMoldyEnterprises/releases).
2. Run installer and accept UAC prompt.
3. Keep "Enable always-on native global hotkey launcher" checked if you want `Win+Shift+Q` to work system-wide after sign-in.
4. Finish install.

No Python/CMake/dev tools are needed for end users.

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

### Build Dependencies (Windows)

1. Python 3.11+
2. CMake 3.16+
3. Visual Studio Build Tools 2022 (Desktop development with C++)
4. Inno Setup 6

### Python Dependencies

From `QrScreenReader` folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
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
--disable-hotkey         Disable the in-app global hotkey for this run
--hotkey COMBO           Override hotkey for this run (e.g., Win+Shift+Q)
```

## Build Windows Executable Bundle

From `QrScreenReader` folder:

```bat
build_exe.bat
```

This builds:

- `dist\\QRScreenReader\\QRScreenReader.exe`
- `dist\\QRScreenReader\\QRHotkeyHelper.exe`

## Build Installer

1. Open `installer/QRScreenReader.iss` in Inno Setup Compiler.
2. Build.

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

1. Build executable bundle with `build_exe.bat`.
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
  - Open app settings and save again; app signals helper reload automatically.

## Notes

- Safety checks are heuristic only, not a full security scanner.
- Global hotkey requires either app running or native helper running.

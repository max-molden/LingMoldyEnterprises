from __future__ import annotations

import argparse
import subprocess
import sys
import time

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from .config import load_config
from .hotkey import GlobalHotkeyListener
from .ui_main import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QR Screen Reader")
    parser.add_argument(
        "--mode",
        choices=["gui", "snip"],
        default="gui",
        help="Startup mode. Default: gui",
    )
    parser.add_argument(
        "--snip",
        action="store_true",
        help="Alias for --mode snip.",
    )
    parser.add_argument(
        "--decode-file",
        metavar="PATH",
        help="Decode a local image file after launch.",
    )
    parser.add_argument(
        "--disable-tray",
        action="store_true",
        help="Disable the system tray icon and quit when the window is closed.",
    )
    parser.add_argument(
        "--disable-hotkey",
        action="store_true",
        help="Do not register the global hotkey for this run.",
    )
    parser.add_argument(
        "--hotkey",
        metavar="COMBO",
        help="Temporarily override configured hotkey (example: Win+Shift+Q).",
    )
    parser.add_argument(
        "--hotkey-daemon",
        action="store_true",
        help="Run background launcher for global hotkey (no GUI window).",
    )
    return parser.parse_args()


def _build_snipe_launch_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--mode", "snip", "--disable-hotkey"]
    return [sys.executable, "-m", "app.main", "--mode", "snip", "--disable-hotkey"]


def run_hotkey_daemon() -> int:
    cfg = load_config()
    if not cfg.hotkey_enabled:
        return 0

    app = QCoreApplication(sys.argv)
    listener = GlobalHotkeyListener(cfg.hotkey)
    state = {"last_launch": 0.0}

    def launch_snip() -> None:
        now = time.monotonic()
        if now - state["last_launch"] < 0.4:
            return
        state["last_launch"] = now
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(_build_snipe_launch_command(), creationflags=creationflags)

    def on_failed(message: str) -> None:
        print(message, file=sys.stderr)
        app.quit()

    listener.triggered.connect(launch_snip)
    listener.registration_failed.connect(on_failed)
    listener.start()
    return app.exec()


def main() -> int:
    args = parse_args()
    if args.hotkey_daemon:
        return run_hotkey_daemon()

    start_in_snip_mode = args.snip or args.mode == "snip"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(
        start_in_snip_mode=start_in_snip_mode,
        tray_enabled=not args.disable_tray,
        hotkey_override=args.hotkey,
        disable_hotkey=args.disable_hotkey,
    )
    window.show()

    if args.decode_file:
        window.decode_from_path(args.decode_file)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

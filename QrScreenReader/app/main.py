from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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

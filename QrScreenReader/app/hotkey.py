from __future__ import annotations

import ctypes
import threading
from ctypes import wintypes

from PySide6.QtCore import QObject, Signal

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
HOTKEY_ID = 100

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]


def parse_hotkey(hotkey_text: str) -> tuple[int, int]:
    tokens = [t.strip() for t in hotkey_text.split("+") if t.strip()]
    if not tokens:
        raise ValueError("Hotkey is empty.")

    mods = 0
    key_token: str | None = None

    for token in tokens:
        upper = token.upper()
        if upper in {"WIN", "WINDOWS"}:
            mods |= MOD_WIN
            continue
        if upper in {"SHIFT"}:
            mods |= MOD_SHIFT
            continue
        if upper in {"CTRL", "CONTROL"}:
            mods |= MOD_CONTROL
            continue
        if upper in {"ALT"}:
            mods |= MOD_ALT
            continue

        if key_token is not None:
            raise ValueError("Hotkey must include exactly one non-modifier key.")
        key_token = upper

    if key_token is None:
        raise ValueError("Hotkey is missing its key (for example: Win+Shift+Q).")

    if len(key_token) == 1 and key_token.isalpha():
        return mods, ord(key_token)

    if len(key_token) == 1 and key_token.isdigit():
        return mods, ord(key_token)

    if key_token.startswith("F") and key_token[1:].isdigit():
        fn = int(key_token[1:])
        if 1 <= fn <= 24:
            return mods, 0x70 + (fn - 1)

    raise ValueError("Unsupported key. Use A-Z, 0-9, or F1-F24.")


class GlobalHotkeyListener(QObject):
    triggered = Signal()
    registration_failed = Signal(str)

    def __init__(self, hotkey: str) -> None:
        super().__init__()
        self._thread: threading.Thread | None = None
        self._running = threading.Event()
        self._thread_id: int | None = None
        self._hotkey = hotkey
        self._state_lock = threading.Lock()

    def set_hotkey(self, hotkey: str) -> None:
        self._hotkey = hotkey

    def start(self) -> None:
        with self._state_lock:
            if self._thread and self._thread.is_alive():
                return

            self._running.set()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        thread_to_join: threading.Thread | None = None
        thread_id: int | None = None
        with self._state_lock:
            self._running.clear()
            thread_id = self._thread_id
            thread_to_join = self._thread

        if thread_id:
            user32.PostThreadMessageW(thread_id, WM_QUIT, 0, 0)

        if thread_to_join and thread_to_join.is_alive() and thread_to_join is not threading.current_thread():
            thread_to_join.join(timeout=1.0)

    def _run_loop(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        try:
            mods, vk = parse_hotkey(self._hotkey)
        except ValueError as exc:
            self.registration_failed.emit(str(exc))
            return

        if not user32.RegisterHotKey(None, HOTKEY_ID, mods, vk):
            self.registration_failed.emit(
                f"Unable to register hotkey '{self._hotkey}'. It may already be in use."
            )
            return

        msg = MSG()
        try:
            while self._running.is_set():
                result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result <= 0:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.triggered.emit()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            with self._state_lock:
                self._thread_id = None
                if self._thread is threading.current_thread():
                    self._thread = None

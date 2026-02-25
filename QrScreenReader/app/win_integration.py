from __future__ import annotations

import ctypes

HELPER_MUTEX_NAME = "Local\\QrScreenReaderHotkeyHelperMutex"
HELPER_RELOAD_EVENT_NAME = "Local\\QrScreenReaderHotkeyReload"

SYNCHRONIZE = 0x00100000
EVENT_MODIFY_STATE = 0x0002


def is_hotkey_helper_running() -> bool:
    if not hasattr(ctypes, "windll"):
        return False

    handle = ctypes.windll.kernel32.OpenMutexW(SYNCHRONIZE, False, HELPER_MUTEX_NAME)
    if not handle:
        return False

    ctypes.windll.kernel32.CloseHandle(handle)
    return True


def signal_hotkey_helper_reload() -> bool:
    if not hasattr(ctypes, "windll"):
        return False

    handle = ctypes.windll.kernel32.OpenEventW(EVENT_MODIFY_STATE, False, HELPER_RELOAD_EVENT_NAME)
    if not handle:
        return False

    ok = bool(ctypes.windll.kernel32.SetEvent(handle))
    ctypes.windll.kernel32.CloseHandle(handle)
    return ok

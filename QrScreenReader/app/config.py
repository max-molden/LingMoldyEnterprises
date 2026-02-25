from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

APP_DIR_NAME = "QrScreenReader"
CONFIG_FILE_NAME = "config.json"


@dataclass
class AppConfig:
    auto_open_url: bool = False
    auto_copy_link: bool = True
    safety_checks_enabled: bool = True
    browser_mode: str = "system"  # system | custom
    custom_browser_path: str = ""
    hotkey_enabled: bool = True
    hotkey: str = "Win+Shift+Q"


def _get_config_dir() -> Path:
    base = os.getenv("APPDATA")
    if not base:
        base = str(Path.home() / ".config")
    config_dir = Path(base) / APP_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    return _get_config_dir() / CONFIG_FILE_NAME


def load_config() -> AppConfig:
    config_path = get_config_path()
    if not config_path.exists():
        default_cfg = AppConfig()
        save_config(default_cfg)
        return default_cfg

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        return AppConfig(
            auto_open_url=bool(raw.get("auto_open_url", False)),
            auto_copy_link=bool(raw.get("auto_copy_link", True)),
            safety_checks_enabled=bool(raw.get("safety_checks_enabled", True)),
            browser_mode=str(raw.get("browser_mode", "system")),
            custom_browser_path=str(raw.get("custom_browser_path", "")),
            hotkey_enabled=bool(raw.get("hotkey_enabled", True)),
            hotkey=str(raw.get("hotkey", "Win+Shift+Q")),
        )
    except Exception:
        # Fall back safely if file is malformed.
        return AppConfig()


def save_config(config: AppConfig) -> None:
    config_path = get_config_path()
    config_path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")

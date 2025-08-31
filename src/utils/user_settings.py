"""User settings persistence module."""
import json
import logging
from typing import Any, Dict
from src.utils.constants import to_appdata_path
from src.utils.utils import createDirByFilePath

USER_SETTINGS_PATH = to_appdata_path("user_configs/userSettings.json")


def load_user_settings() -> Dict[str, Any]:
    """Load user settings from persistent storage."""
    try:
        with open(USER_SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            logging.debug(f"Loaded user settings: {settings}")
            return settings
    except FileNotFoundError:
        logging.debug("No user settings file found, using defaults")
        return {}
    except Exception as e:
        logging.warning(f"Failed to load user settings: {e}")
        return {}


def save_user_settings(settings: Dict[str, Any]) -> bool:
    """Save user settings to persistent storage."""
    try:
        createDirByFilePath(USER_SETTINGS_PATH)
        with open(USER_SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        logging.debug(f"Saved user settings: {settings}")
        return True
    except Exception as e:
        logging.error(f"Failed to save user settings: {e}")
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value."""
    settings = load_user_settings()
    return settings.get(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Set a specific setting value."""
    settings = load_user_settings()
    settings[key] = value
    return save_user_settings(settings)


def update_settings(**kwargs) -> bool:
    """Update multiple settings at once."""
    settings = load_user_settings()
    settings.update(kwargs)
    return save_user_settings(settings)

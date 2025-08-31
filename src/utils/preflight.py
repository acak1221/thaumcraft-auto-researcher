import logging
import os
import onnxruntime as ort

from src.utils import constants


def _check_file(path: str, description: str) -> bool:
    exists = os.path.exists(path)
    if exists:
        logging.debug(f"[Preflight] Found {description}: {path}")
    else:
        logging.error(f"[Preflight] Missing {description}: {path}")
    return exists


def run_preflight(strict: bool = True) -> bool:
    """Validate required resources exist before running the app.

    Args:
        strict: If True, any missing item fails the check. If False, only warn.

    Returns:
        True when all critical files are present (or non-strict), False otherwise.
    """
    logging.info("Running preflight checks...")

    checks = [
        _check_file(constants.FIELD_OBJECT_DETECTION_PATH, "field object detection model"),
        _check_file(constants.INVENTORY_OBJECT_DETECTION_PATH, "inventory object detection model"),
        _check_file(constants.FIELD_CLASS_NAMES_PATH, "field class names"),
        _check_file(constants.INVENTORY_CLASS_NAMES_PATH, "inventory class names"),
        _check_file(constants.THAUM_ASPECT_RECIPES_CONFIG_PATH, "aspects recipes config (vanilla)"),
        _check_file(constants.THAUM_ASPECTS_ORDER_CONFIG_PATH, "aspects order config"),
        _check_file(constants.UNKNOWN_ASPECT_IMAGE_PATH, "unknown aspect image"),
    ]

    all_ok = all(checks)

    # Log ORT providers info
    try:
        available = ort.get_available_providers()
        logging.info(f"[Preflight] ORT providers available: {available}; desired: {constants.ORT_PROVIDERS}")
    except Exception as e:
        logging.warning(f"[Preflight] ORT providers detection failed: {e}")
    if all_ok:
        logging.info("Preflight OK")
        return True

    if strict:
        logging.critical("Preflight failed: some required files are missing. See errors above.")
        return False

    logging.warning("Preflight had missing items but continuing due to non-strict mode")
    return True



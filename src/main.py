import logging
import logging.handlers
import sys
import argparse
import os

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.controllers import Scenarios
from src.UI.OverlayUI import OverlayUI
from src.utils import constants
from src.utils.constants import LOG_FILE_PATH, MAX_LOG_FILE_SIZE_BYTES, DEBUG, LOG_LEVEL, MAX_LOG_FILES_COUNT
from src.utils.preflight import run_preflight
from src.utils.utils import createDirByFilePath

def setup_logging(log_level: int | str = LOG_LEVEL, to_stdout: bool = DEBUG):
    createDirByFilePath(LOG_FILE_PATH)
    loggingHandlers = [
        logging.handlers.RotatingFileHandler(
            filename=LOG_FILE_PATH, maxBytes=MAX_LOG_FILE_SIZE_BYTES, backupCount=MAX_LOG_FILES_COUNT
        )
    ]
    if to_stdout:
        loggingHandlers.append(logging.StreamHandler(sys.stdout))  # output both to console and log-files
    logging.basicConfig(
        handlers=loggingHandlers,
        format="%(asctime)s [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        level=log_level,
        force=True,
    )

UI = OverlayUI(opacity=1)


def main():
    try:
        Scenarios.beReadyForCreatingTI(UI)
    except Exception:
        logging.exception("Unhandled exception in main thread")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thaumcraft Auto Researcher")
    parser.add_argument("--log-level", default=None, help="Override log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    parser.add_argument("--no-stdout", action="store_true", help="Disable logging to stdout")
    parser.add_argument("--preflight", action="store_true", help="Run preflight checks and exit")
    parser.add_argument("--preflight-nonstrict", action="store_true", help="Preflight warns instead of failing")
    parser.add_argument("--confidence", type=float, default=None, help="Detection confidence threshold (0.0-1.0)")
    parser.add_argument("--iou", type=float, default=None, help="Detection IoU threshold (0.0-1.0)")
    parser.add_argument("--max-detections", type=int, default=None, help="Max detections per image")
    parser.add_argument("--use-gpu", action="store_true", help="Try to use GPU/CUDA if available")
    args = parser.parse_args()

    level = getattr(logging, args.log_level.upper(), LOG_LEVEL) if args.log_level else LOG_LEVEL
    setup_logging(level, to_stdout=(not args.no_stdout))

    # Apply CLI overrides to constants
    if args.confidence is not None:
        constants.DETECTION_CONFIDENCE = args.confidence
        logging.info(f"Overriding detection confidence to {args.confidence}")
    if args.iou is not None:
        constants.DETECTION_IOU = args.iou
        logging.info(f"Overriding detection IoU to {args.iou}")
    if args.max_detections is not None:
        constants.DETECTION_MAX_DETECTIONS = args.max_detections
        logging.info(f"Overriding max detections to {args.max_detections}")
    if args.use_gpu:
        # Try to add CUDA provider if available
        if "CUDAExecutionProvider" not in constants.ORT_PROVIDERS:
            constants.ORT_PROVIDERS.insert(0, "CUDAExecutionProvider")
            logging.info("GPU mode requested, adding CUDAExecutionProvider")

    logging.info("Program started")
    logging.info("###############")

    if args.preflight:
        ok = run_preflight(strict=not args.preflight_nonstrict)
        sys.exit(0 if ok else 1)

    try:
        UI.start(main)
    except Exception:
        logging.exception("Unhandled exception in UI thread")

import json
import logging
import math
import os
import time

from PIL import Image
from typing import Iterable

from src.utils.LinkableValue import linkableValueDumpsToJSON
from src.utils.constants import (
    THAUM_CONTROLS_CONFIG_PATH,
    THAUM_ASPECT_RECIPES_CONFIG_PATH,
    THAUM_VERSION_CONFIG_PATH,
    DELAY_BETWEEN_EVENTS,
    DELAY_BETWEEN_RENDER,
    THAUM_ADDONS_ASPECT_RECIPES_CONFIG_PATH,
)


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def createDirByFilePath(fullpath: str):
    dir_path = os.path.dirname(fullpath)
    if not os.path.exists(dir_path):
        logging.info(f"Directory {dir_path} not exists. Creating...")
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f"Directory {dir_path} successfully created")


def saveJSONConfig(fullpath: str, jsonToSave: dict):
    createDirByFilePath(fullpath)
    with open(fullpath, "w") as file:
        json.dump(jsonToSave, file, indent=4, ensure_ascii=False, default=linkableValueDumpsToJSON)


def saveThaumControlsConfig(
    pointWritingMaterials,
    pointPapers,
    rectAspectsListingLT,
    rectAspectsListingRB,
    pointAspectsScrollLeft,
    pointAspectsScrollRight,
    pointAspectsMixLeft,
    pointAspectsMixCreate,
    pointAspectsMixRight,
    rectInventoryLT,
    rectInventoryRB,
    rectHexagonsCC,
    hexagonSlotSizeY,
):
    saveJSONConfig(
        THAUM_CONTROLS_CONFIG_PATH,
        {
            "pointWritingMaterials": {"x": pointWritingMaterials.x, "y": pointWritingMaterials.y},
            "pointPapers": {"x": pointPapers.x, "y": pointPapers.y},
            "rectAspectsListingLT": {"x": rectAspectsListingLT.x, "y": rectAspectsListingLT.y},
            "rectAspectsListingRB": {"x": rectAspectsListingRB.x, "y": rectAspectsListingRB.y},
            "pointAspectsScrollLeft": {"x": pointAspectsScrollLeft.x, "y": pointAspectsScrollLeft.y},
            "pointAspectsScrollRight": {"x": pointAspectsScrollRight.x, "y": pointAspectsScrollRight.y},
            "pointAspectsMixLeft": {"x": pointAspectsMixLeft.x, "y": pointAspectsMixLeft.y},
            "pointAspectsMixCreate": {"x": pointAspectsMixCreate.x, "y": pointAspectsMixCreate.y},
            "pointAspectsMixRight": {"x": pointAspectsMixRight.x, "y": pointAspectsMixRight.y},
            "rectInventoryLT": {"x": rectInventoryLT.x, "y": rectInventoryLT.y},
            "rectInventoryRB": {"x": rectInventoryRB.x, "y": rectInventoryRB.y},
            "rectHexagonsCC": {"x": rectHexagonsCC.x, "y": rectHexagonsCC.y},
            "hexagonSlotSizeY": hexagonSlotSizeY,
        },
    )
    logging.info("Thaum controls config successfully saved")


def readJSONConfig(fullpath: str):
    if not os.path.isfile(fullpath):
        logging.warning(f"Config {fullpath} not exists")
        return None
    try:
        with open(fullpath, "r") as file:
            config = json.load(file)
    except Exception as e:
        logging.critical(f"Something went wrong while opening config {fullpath}: {e}")
        return None
    logging.debug(f"Config {fullpath} successfully loaded")
    return config


def _validate_images(image1: Image.Image, image2: Image.Image):
    if image1.size != image2.size:
        raise ValueError("Images sizes must be the same")
    if image1.mode != image2.mode:
        raise ValueError("Image modes must be the same")


def _prepare_masks(image_size: tuple[int, int], masks: Iterable[Image.Image]) -> list[bool]:
    pixels_count = image_size[0] * image_size[1]
    total_mask = [True] * pixels_count
    for mask in masks or []:
        if mask.size != image_size:
            raise ValueError("Images and all masks sizes must be the same")
        bool_mask = [val != 0 for val in mask.convert("L").getdata()]
        total_mask = [old and new for old, new in zip(total_mask, bool_mask)]
    return total_mask


def getImagesDiffPercent(
    image1: Image.Image,
    image2: Image.Image,
    masks: Iterable[Image.Image] | None = None,
) -> float:
    """Return percentage difference between two images with optional masks."""
    _validate_images(image1, image2)

    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())
    total_mask = _prepare_masks(image1.size, masks or [])

    total_diff = 0
    active_pixels = 0
    channels = len(pixels1[0])

    for pix1, pix2, use_pixel in zip(pixels1, pixels2, total_mask):
        if not use_pixel:
            continue
        active_pixels += 1
        total_diff += sum(abs(a - b) for a, b in zip(pix1, pix2))

    if active_pixels == 0:
        return 0.0

    percent_diff = total_diff / (active_pixels * channels * 255)
    return percent_diff


def saveThaumVersionConfig(version: str):
    saveJSONConfig(
        THAUM_VERSION_CONFIG_PATH,
        {
            "version": version,
        },
    )


def loadThaumVersionConfig() -> str | None:
    conf = readJSONConfig(THAUM_VERSION_CONFIG_PATH)
    if conf is None:
        return None
    return conf["version"]


def loadRecipesForSelectedVersion() -> dict[str, list[str, str]] | None:
    selectedVersion = loadThaumVersionConfig()
    allVersionsRecipes = readJSONConfig(THAUM_ASPECT_RECIPES_CONFIG_PATH)
    if selectedVersion is None or allVersionsRecipes is None:
        logging.error(
            f"Cannot load recipes for selected version. SelectedVersion or allRecipes is None: ({selectedVersion}, {allVersionsRecipes})"
        )
        return None
    totalRecipes = allVersionsRecipes.get(selectedVersion)
    if totalRecipes is None:
        logging.error(f"Selected unknown version: {selectedVersion}")
        return None
    addonsRecipes = readJSONConfig(THAUM_ADDONS_ASPECT_RECIPES_CONFIG_PATH)
    if addonsRecipes:
        for addonRecipes in addonsRecipes.values():
            totalRecipes |= addonRecipes
    else:
        logging.debug(
            f"No addon recipes found at {THAUM_ADDONS_ASPECT_RECIPES_CONFIG_PATH}"
        )
    return totalRecipes


def eventsDelay():
    time.sleep(DELAY_BETWEEN_EVENTS)


def renderDelay():
    time.sleep(DELAY_BETWEEN_RENDER)


def loadImage(path: str, backgroundImage: Image.Image = None, resize: tuple[int, int] | None = None) -> Image.Image:
    image = Image.open(path)
    if resize:
        image = image.resize(resize, Image.Resampling.LANCZOS)
    image = image.convert("RGBA")
    backgroundImage = backgroundImage or Image.new("RGBA", image.size, "BLACK")  # Create a white rgba background
    newImage = backgroundImage.convert("RGBA")
    newImage.paste(image, mask=image)  # Paste the image on the background. Go to the links given below for details.
    result = newImage.convert("RGB")
    logging.debug(f"Loaded image {path}")
    return result

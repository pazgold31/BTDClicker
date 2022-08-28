import re

import numpy as np
import pyautogui

from PIL import Image
import pytesseract


def get_screenshot() -> Image:
    return pyautogui.screenshot(region=(320, 0, 250, 100))


def preprocess_image(image: str) -> Image:
    data = np.array(image)

    converted = np.where(data == 255, 0, 255)

    return Image.fromarray(converted.astype('uint8'))


def get_amount_of_money() -> int:
    # TODO: fix the command thing to work for everyone.
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = preprocess_image(get_screenshot())
    image_text = pytesseract.image_to_string(image)
    return int(re.search(r"[Ss$](\d+)", image_text).group(1))

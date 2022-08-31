import re
import time

import numpy as np
import pyautogui

from PIL import Image
import pytesseract


def get_screenshot() -> Image:
    return pyautogui.screenshot(region=(345, 0, 250, 100))


def preprocess_image(image: str) -> Image:
    data = np.array(image)

    converted = np.where(data == 255, 0, 255)

    return Image.fromarray(converted.astype('uint8'))


def get_amount_of_money() -> int:
    # TODO: fix the command thing to work for everyone.
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = preprocess_image(get_screenshot())
    image_text = pytesseract.image_to_string(image)
    re_text = re.search(r"([\d,]+)", image_text).group(1)
    return int(re_text.replace(",", ""))


def safe_get_amount_of_money(amount_of_reads: int = 4):
    results = []
    for i in range(amount_of_reads):
        results.append(get_amount_of_money())
        time.sleep(0.3)

    for i in range(amount_of_reads - 1):
        if abs(results[i] - results[i + 1]) > 150:
            raise RuntimeError("Failed to get money")

    return results[-1]

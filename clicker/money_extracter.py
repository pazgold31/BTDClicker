import re
import time

import numpy as np
import pyautogui
import pytesseract
from PIL import Image


def get_screenshot() -> Image:
    return pyautogui.screenshot(region=(345, 20, 145, 50))


def preprocess_image(image: Image) -> Image:
    data = np.array(image)

    converted = np.where(data == 255, 0, 255)

    return Image.fromarray(converted.astype('uint8'))


def get_text_from_image(image: Image) -> str:
    image_text = pytesseract.image_to_string(image, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    return image_text


def _get_amount_of_money() -> int:
    image_text = get_text_from_image(image=preprocess_image(get_screenshot()))
    re_text = re.search(r"([\d,]+)", image_text).group(1)
    return int(re_text.replace(",", ""))


def get_amount_of_money(amount_of_reads=3) -> int:
    results = []
    for i in range(amount_of_reads):
        results.append(_get_amount_of_money())
        time.sleep(0.2)

    for i in range(amount_of_reads - 1):
        if abs(results[i] - results[i + 1]) > 800:
            print("Error with money")
            raise RuntimeError("Failed to get money")

    return results[-1]

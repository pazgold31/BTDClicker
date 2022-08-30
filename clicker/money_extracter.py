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


def safe_get_amount_of_money():
    results = []
    for i in range(3):
        results.append(get_amount_of_money())
        time.sleep(0.1)

    if abs(results[0] - results[1]) > 150 or abs(results[1] - results[2]) > 150:
        print("Failed to get money")
        raise RuntimeError("Failed to get money")

    print(results[-1])
    return results[-1]


get_screenshot().save("tmp.png")
